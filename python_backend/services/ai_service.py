import os
from sqlmodel import Session, select
from typing import List, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from database import get_session, engine
from models import Temple, Inscription
from config import settings

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    language: Optional[str] = "English"
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class ChatResponse(BaseModel):
    answer: str
    language: str
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class TranslateRequest(BaseModel):
    text: str
    target_language: Optional[str] = "English"
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class TranslateResponse(BaseModel):
    translation: str
    explanation: str
    target_language: str
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class IngestRequest(BaseModel):
    image_base64: Optional[str] = None
    mime_type: Optional[str] = None
    text: Optional[str] = None
    temple_name: Optional[str] = None
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class IngestResponse(BaseModel):
    title: str
    language: str
    script: str
    translation: str
    simple_explanation: str
    historical_significance: str
    ruler: str
    notes: str
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

def _get_client():
    if not settings.KALVETTU_AI_GEMINI_KEY:
        raise ValueError("AI is not configured. KALVETTU_AI_GEMINI_KEY is missing.")
    return genai.Client(api_key=settings.KALVETTU_AI_GEMINI_KEY)

def abbrev(s: Optional[str], max_len: int) -> str:
    if not s:
        return ""
    return s if len(s) <= max_len else s[:max_len] + "…"

def _build_context() -> str:
    with Session(engine) as session:
        temples = session.exec(select(Temple)).all()
        inscriptions = session.exec(select(Inscription)).all()
        
        ctx = "[TEMPLES]\n"
        for t in temples:
            ctx += f"- {t.name_en} (slug: {t.slug}, town: {t.town}, dynasty: {t.dynasty_slug}, deity: {t.deity}"
            if t.summary:
                ctx += f", summary: {t.summary}"
            ctx += ")\n"
            
        ctx += "\n[INSCRIPTIONS]\n"
        for i in inscriptions:
            ctx += f"- {i.title} (slug: {i.slug}, temple: {i.temple_slug}, ruler: {i.ruler_slug}, dynasty: {i.dynasty_slug}, reference: {i.reference_id}"
            if i.translation:
                ctx += f", translation: {abbrev(i.translation, 600)}"
            if i.simple_explanation:
                ctx += f", simple explanation: {abbrev(i.simple_explanation, 400)}"
            if i.historical_significance:
                ctx += f", significance: {abbrev(i.historical_significance, 300)}"
            ctx += ")\n"
            
        return ctx

def chat(request: ChatRequest) -> ChatResponse:
    client = _get_client()
    context = _build_context()
    
    history = ""
    for m in request.messages:
        history += f"{m.role}: {m.content}\n"
    if not history:
        history = "[no prior messages]"
        
    lang = request.language if request.language else "English"
    
    prompt = f"""
VERIFIED ARCHIVE CONTEXT (the only facts you may use):
{context}

CONVERSATION SO FAR:
{history}

TASK: Answer the user's latest message.
- Answer ONLY from the VERIFIED ARCHIVE CONTEXT above.
- If the context does not contain the answer, say so clearly instead of guessing.
- Never invent inscriptions, rulers, dates, temples, translations or sources.
- Answer in the language: {lang}
"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return ChatResponse(answer=response.text, language=lang)

def translate(request: TranslateRequest) -> TranslateResponse:
    client = _get_client()
    lang = request.target_language if request.target_language else "English"
    
    prompt = f"""
Translate the following Tamil/Grantha temple inscription into {lang}.
Then provide a simple plain-language explanation of what it means.

INSCRIPTION TEXT:
{request.text}

Return your response strictly as a JSON object with two string fields:
"translation": "..."
"explanation": "..."
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    import json
    try:
        data = json.loads(response.text)
        return TranslateResponse(
            translation=data.get("translation", ""),
            explanation=data.get("explanation", ""),
            target_language=lang
        )
    except Exception:
        return TranslateResponse(translation="Failed to parse response.", explanation=response.text, target_language=lang)

def ingest(request: IngestRequest) -> IngestResponse:
    client = _get_client()
    
    prompt = f"""
Analyze the provided Kalvettu (Tamil temple inscription) details.
Text: {request.text or 'None'}
Temple Name: {request.temple_name or 'Unknown'}

Return your response strictly as a JSON object with the following fields:
"title", "language", "script", "translation", "simpleExplanation", "historicalSignificance", "ruler", "notes".
"""
    
    contents = []
    if request.image_base64 and request.mime_type:
        contents.append(
            types.Part.from_bytes(
                data=bytes.fromhex(request.image_base64) if len(request.image_base64) % 2 == 0 else request.image_base64.encode(),
                mime_type=request.mime_type
            )
        )
        
    contents.append(prompt)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        import json
        data = json.loads(response.text)
        return IngestResponse(
            title=data.get("title", ""),
            language=data.get("language", ""),
            script=data.get("script", ""),
            translation=data.get("translation", ""),
            simple_explanation=data.get("simpleExplanation", ""),
            historical_significance=data.get("historicalSignificance", ""),
            ruler=data.get("ruler", ""),
            notes=data.get("notes", "")
        )
    except Exception as e:
        return IngestResponse(
            title="Error", language="", script="", translation=str(e),
            simple_explanation="", historical_significance="", ruler="", notes=""
        )
