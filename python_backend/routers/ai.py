from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlmodel import Session, select
import base64

from schemas import (
    ChatRequest, ChatResponse,
    TranslateRequest, TranslateResponse,
    IngestRequest, IngestResponse
)
from services.rag_service import search_verified_context
from services.ai.router import router as ai_router
from database import get_session
from models import Inscription, Temple, AuditLog, Image
from security import rate_limiter, validate_image_file, upload_image_to_supabase_storage

router = APIRouter(dependencies=[Depends(rate_limiter(max_requests=30, window_seconds=60))])

@router.post("/ask", response_model=ChatResponse)
@router.post("/chat", response_model=ChatResponse)
async def api_chat(request: ChatRequest):
    """
    Ask the Archive: Grounded RAG querying Supabase verified records.
    Never hallucinates facts or sources. Falls back across Groq -> Cerebras -> OpenRouter -> Gemini -> Local DB.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    last_user_message = request.messages[-1].content.strip()
    if not last_user_message:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    # 1. RAG retrieval from Supabase PostgreSQL
    context_str, citations, related_temples, related_inscriptions = search_verified_context(last_user_message)
    
    # 2. Chained AI Generation
    lang = request.language or "English"
    res = await ai_router.chat_with_fallback(
        prompt=last_user_message,
        context=context_str,
        language=lang
    )

    return ChatResponse(
        answer=res["answer"],
        language=lang,
        sources=citations,
        related_temples=related_temples,
        related_inscriptions=related_inscriptions,
        provider_used=res.get("provider")
    )

@router.post("/translate", response_model=TranslateResponse)
async def api_translate(request: TranslateRequest):
    """
    Translate an inscription: Identifies language & script, provides plain-language explanation.
    """
    target_lang = request.target_language or "English"
    
    # If an image was passed to translate:
    if request.image_base64:
        try:
            img_bytes = base64.b64decode(request.image_base64)
            _, detected_mime = validate_image_file(img_bytes)
            vision_res = await ai_router.vision_extract(
                image_bytes=img_bytes,
                mime_type=detected_mime,
                prompt=f"Translate visible inscription into {target_lang}."
            )
            return TranslateResponse(
                detected_language=vision_res.get("language", "Tamil"),
                detected_script=vision_res.get("script", "Tamil"),
                original_text=vision_res.get("original_text", ""),
                translation=vision_res.get("translation", "Unable to translate image text."),
                explanation=vision_res.get("simple_explanation", ""),
                target_language=target_lang,
                important_terms=[],
                historical_context=vision_res.get("historical_significance", ""),
                is_draft=True,
                verification_status="DRAFT",
                provider_used=vision_res.get("provider_used", "gemini-vision")
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process image for translation: {e}")

    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Inscription text is required for translation.")

    res = await ai_router.translate_with_fallback(
        text=request.text.strip(),
        target_language=target_lang
    )

    return TranslateResponse(
        detected_language=res.get("detected_language", "Tamil"),
        detected_script=res.get("detected_script", "Tamil"),
        original_text=request.text.strip(),
        translation=res.get("translation", "Translation not available."),
        explanation=res.get("explanation", ""),
        target_language=target_lang,
        important_terms=res.get("important_terms", []),
        historical_context=res.get("historical_context", ""),
        is_draft=False,
        verification_status="VERIFIED",
        provider_used=res.get("provider_used")
    )

@router.post("/extract", response_model=IngestResponse)
@router.post("/ingest", response_model=IngestResponse)
async def api_ingest(request: IngestRequest, session: Session = Depends(get_session)):
    """
    Add a Kalvettu (AI-assisted): Extracts draft structured record from photo or text.
    CRITICAL: Always marks extracted records as DRAFT for human review.
    Uploaded photos are validated for magic bytes, size limits, and stored in Supabase Storage.
    """
    if not request.image_base64 and not (request.text and request.text.strip()):
        raise HTTPException(status_code=400, detail="Either an inscription photo or transcription text must be provided.")

    extracted_data = {}
    provider_used = None
    uploaded_image_url = None

    if request.image_base64:
        try:
            img_bytes = base64.b64decode(request.image_base64)
            _, detected_mime = validate_image_file(img_bytes)
            
            # 1. Upload to Supabase Storage
            uploaded_image_url = upload_image_to_supabase_storage(img_bytes, bucket_name="inscriptions")
            
            # 2. Vision extraction
            prompt = f"Known temple: {request.temple_name or 'Unknown'}. User notes: {request.notes or 'None'}."
            extracted_data = await ai_router.vision_extract(img_bytes, detected_mime, prompt)
            provider_used = extracted_data.get("provider_used")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image OCR extraction error: {e}")
    else:
        # Text-only extraction using fallback router
        trans_res = await ai_router.translate_with_fallback(request.text, "English")
        extracted_data = {
            "title": f"Inscription at {request.temple_name}" if request.temple_name else "Extracted Inscription Record",
            "language": trans_res.get("detected_language", "Tamil"),
            "script": trans_res.get("detected_script", "Tamil"),
            "translation": trans_res.get("translation", ""),
            "simple_explanation": trans_res.get("explanation", ""),
            "historical_significance": trans_res.get("historical_context", ""),
            "ruler": "Not specified",
            "notes": request.notes or ""
        }
        provider_used = trans_res.get("provider_used")

    # Match existing temple if specified
    temple_slug = "unassociated"
    if request.temple_name:
        matched_t = session.exec(
            select(Temple).where(Temple.name_en.ilike(f"%{request.temple_name}%"))
        ).first()
        if matched_t:
            temple_slug = matched_t.slug

    # Save as DRAFT in Supabase (Never publish unverified!)
    import uuid
    draft_slug = f"draft-{uuid.uuid4().hex[:8]}"
    draft_ins = Inscription(
        slug=draft_slug,
        temple_slug=temple_slug,
        title=extracted_data.get("title") or "Untitled Draft Inscription",
        language=extracted_data.get("language") or "Tamil",
        script=extracted_data.get("script") or "Tamil",
        original_text=request.text or extracted_data.get("original_text"),
        translation=extracted_data.get("translation"),
        simple_explanation=extracted_data.get("simple_explanation"),
        historical_significance=extracted_data.get("historical_significance"),
        source_citation="AI-Assisted Ingestion Draft - Pending Expert Review",
        verification_status="DRAFT",
        verified=False,
        physical_location=request.location_in_temple
    )
    session.add(draft_ins)
    
    # Link uploaded image if present
    if uploaded_image_url:
        image_record = Image(
            entity_type="INSCRIPTION",
            entity_slug=draft_slug,
            image_url=uploaded_image_url,
            caption=draft_ins.title,
            author="User field submission (AI Ingestion)",
            verification_status="DRAFT"
        )
        session.add(image_record)

    # Audit log entry
    audit = AuditLog(
        actor="AI Ingestion Assistant",
        action="DRAFT_CREATED",
        record_type="INSCRIPTION",
        record_id=draft_slug
    )
    session.add(audit)
    session.commit()

    return IngestResponse(
        title=draft_ins.title,
        language=draft_ins.language or "Tamil",
        script=draft_ins.script or "Tamil",
        translation=draft_ins.translation or "",
        simple_explanation=draft_ins.simple_explanation or "",
        historical_significance=draft_ins.historical_significance or "",
        ruler=extracted_data.get("ruler", "Pending review"),
        dynasty=extracted_data.get("dynasty"),
        notes=request.notes or extracted_data.get("notes") or "",
        verification_status="DRAFT",
        status_message="AI-generated draft saved to database as DRAFT - requires human verification before publication.",
        provider_used=provider_used
    )
