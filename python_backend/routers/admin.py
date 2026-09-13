from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlmodel import Session, select
from typing import List, Optional
from database import get_session
from models import Inscription, Temple, AuditLog, Source, Image
from schemas import InscriptionCard, BaseSchema
from config import settings
from services.external_data import search_wikimedia_images

router = APIRouter()

def verify_admin_key(x_admin_key: Optional[str] = Header(None)):
    expected = settings.ADMIN_API_KEY
    if not expected or x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing administrator credentials.")
    return True

class ModerationRequest(BaseSchema):
    notes: Optional[str] = None

@router.get("/drafts", response_model=List[InscriptionCard])
def list_draft_inscriptions(
    authenticated: bool = Depends(verify_admin_key),
    session: Session = Depends(get_session)
):
    """List unverified draft inscriptions pending review"""
    drafts = session.exec(
        select(Inscription).where(Inscription.verification_status != "VERIFIED")
    ).all()
    
    return [
        InscriptionCard(
            id=d.id,
            slug=d.slug,
            temple_slug=d.temple_slug,
            title=d.title,
            title_ta=d.title_ta,
            reference_id=d.reference_id,
            ruler_slug=d.ruler_slug,
            dynasty_slug=d.dynasty_slug,
            language=d.language,
            script=d.script,
            verified=d.verified,
            verification_status=d.verification_status
        )
        for d in drafts
    ]

@router.post("/drafts/{slug}/verify")
def verify_inscription(
    slug: str,
    req: ModerationRequest,
    authenticated: bool = Depends(verify_admin_key),
    session: Session = Depends(get_session)
):
    """Verify and publish a draft inscription to the public archive"""
    ins = session.exec(select(Inscription).where(Inscription.slug == slug)).first()
    if not ins:
        raise HTTPException(status_code=404, detail="Draft record not found.")

    ins.verification_status = "VERIFIED"
    ins.verified = True
    session.add(ins)

    audit = AuditLog(
        actor="Administrator",
        action="VERIFIED",
        record_type="INSCRIPTION",
        record_id=slug
    )
    session.add(audit)
    session.commit()

    return {"message": f"Inscription '{ins.title}' verified and published.", "slug": slug}

@router.post("/drafts/{slug}/reject")
def reject_inscription(
    slug: str,
    req: ModerationRequest,
    authenticated: bool = Depends(verify_admin_key),
    session: Session = Depends(get_session)
):
    """Reject a draft inscription"""
    ins = session.exec(select(Inscription).where(Inscription.slug == slug)).first()
    if not ins:
        raise HTTPException(status_code=404, detail="Draft record not found.")

    ins.verification_status = "REJECTED"
    ins.verified = False
    session.add(ins)

    audit = AuditLog(
        actor="Administrator",
        action="REJECTED",
        record_type="INSCRIPTION",
        record_id=slug
    )
    session.add(audit)
    session.commit()

    return {"message": f"Inscription '{ins.title}' rejected.", "slug": slug}

@router.post("/sync/images")
async def sync_images_for_temple(
    temple_slug: str,
    authenticated: bool = Depends(verify_admin_key),
    session: Session = Depends(get_session)
):
    """Fetch and sync real Wikimedia Commons images for a temple"""
    temple = session.exec(select(Temple).where(Temple.slug == temple_slug)).first()
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found.")

    fetched_imgs = await search_wikimedia_images(temple.name_en, limit=5)
    added = 0
    for im in fetched_imgs:
        existing = session.exec(
            select(Image).where(Image.image_url == im["image_url"])
        ).first()
        if not existing:
            new_img = Image(
                entity_type="TEMPLE",
                entity_slug=temple_slug,
                category="exterior",
                commons_file=im.get("title"),
                image_url=im["image_url"],
                thumb_url=im.get("thumb_url"),
                width=im.get("width"),
                height=im.get("height"),
                author=im.get("author"),
                license=im.get("license"),
                license_url=im.get("license_url"),
                commons_url=im.get("commons_url"),
                caption=im.get("caption") or f"Photograph of {temple.name_en}",
                verification_status="VERIFIED"
            )
            session.add(new_img)
            added += 1

    session.commit()
    return {"temple": temple_slug, "images_added": added, "total_queried": len(fetched_imgs)}
