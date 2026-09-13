from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from typing import List, Optional
from database import get_session
from models import (
    Temple, Inscription, Dynasty, Ruler, District,
    Image, InscriptionLocation, Source, HistoricalEvent
)
from schemas import (
    TempleCard, TempleDetail, InscriptionCard, InscriptionDetail,
    DynastyDto, RulerDto, DistrictDto, InscriptionLocationDto,
    TimelineEvent, SearchResult, ImageDto, SourceDto, WikiFetchRequest
)

router = APIRouter()

def get_first_image_url(session: Session, entity_type: str, slug: str) -> Optional[str]:
    img = session.exec(
        select(Image).where(
            Image.entity_type == entity_type,
            Image.entity_slug == slug,
            Image.verification_status == "VERIFIED"
        )
    ).first()
    if img:
        return img.thumb_url if img.thumb_url else img.image_url
    return None

def to_temple_card(t: Temple, session: Optional[Session] = None, image_map: Optional[dict] = None) -> TempleCard:
    if image_map is not None:
        img_url = image_map.get(t.slug)
    else:
        img_url = get_first_image_url(session, "TEMPLE", t.slug)

    return TempleCard(
        id=t.id,
        slug=t.slug,
        name_en=t.name_en,
        name_ta=t.name_ta,
        town=t.town,
        district_slug=t.district_slug,
        dynasty_slug=t.dynasty_slug,
        deity=t.deity,
        period_note=t.period_note,
        consecration_year=t.consecration_year,
        lat=t.lat,
        lng=t.lng,
        summary=t.summary or (t.history[:200] + '...' if t.history else None),
        history=t.history,
        architecture=t.architecture,
        managed_by=t.managed_by,
        source_note=t.source_note,
        unesco_world_heritage=t.unesco_world_heritage,
        unesco_url=t.unesco_url,
        asi_monument=t.asi_monument,
        asi_url=t.asi_url,
        wikipedia_url=getattr(t, 'wikipedia_url', None),
        image_url=img_url,
        hero_image_url=img_url,
        alternate_names=t.alternate_names,
        patron=t.patron,
        verification_status=t.verification_status
    )

def to_ins_card(i: Inscription, session: Optional[Session] = None, image_map: Optional[dict] = None, temple_image_map: Optional[dict] = None) -> InscriptionCard:
    if image_map is not None and temple_image_map is not None:
        img_url = image_map.get(i.slug) or temple_image_map.get(i.temple_slug)
    else:
        img_url = get_first_image_url(session, "INSCRIPTION", i.slug)
        if not img_url:
            img_url = get_first_image_url(session, "TEMPLE", i.temple_slug)

    return InscriptionCard(
        id=i.id,
        slug=i.slug,
        temple_slug=i.temple_slug,
        title=i.title,
        title_ta=i.title_ta,
        reference_id=i.reference_id,
        are_number=i.are_number,
        sii_reference=i.sii_reference,
        ruler_slug=i.ruler_slug,
        dynasty_slug=i.dynasty_slug,
        regnal_year=i.regnal_year,
        language=i.language,
        script=i.script,
        physical_location=i.physical_location,
        image_url=img_url,
        thumb_image_url=img_url,
        verified=i.verified,
        verification_status=i.verification_status
    )

@router.get("/temples", response_model=List[TempleCard])
def get_temples(
    q: Optional[str] = None, 
    district: Optional[str] = None, 
    dynasty: Optional[str] = None, 
    session: Session = Depends(get_session)
):
    """
    Search and filter verified temples from Supabase.
    Supports English names, Tamil names, alternate names, deity, and town.
    """
    query = select(Temple).where(Temple.verification_status == "VERIFIED")
    
    if district:
        query = query.where(Temple.district_slug == district)
    if dynasty:
        query = query.where(Temple.dynasty_slug == dynasty)

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Temple.name_en.ilike(term),
                Temple.name_ta.ilike(term),
                Temple.alternate_names.ilike(term),
                Temple.town.ilike(term),
                Temple.deity.ilike(term)
            )
        )

    temples = session.exec(query).all()
    
    # Batch fetch images to prevent N+1 query issue
    temple_slugs = [t.slug for t in temples]
    if temple_slugs:
        images = session.exec(
            select(Image).where(
                Image.entity_type == "TEMPLE",
                Image.entity_slug.in_(temple_slugs),
                Image.verification_status == "VERIFIED"
            )
        ).all()
        image_map = {}
        for img in images:
            if img.entity_slug not in image_map:
                image_map[img.entity_slug] = img.thumb_url if img.thumb_url else img.image_url
    else:
        image_map = {}

    return [to_temple_card(t, session=None, image_map=image_map) for t in temples]

@router.get("/temples/{slug}", response_model=TempleDetail)
async def get_temple(slug: str, refresh: bool = False, session: Session = Depends(get_session)):
    """
    Retrieve single verified temple detail with full provenance and images.
    If history or architecture is missing, or refresh is requested, dynamically enriches via Wikipedia & AI.
    """
    t = session.exec(select(Temple).where(Temple.slug == slug, Temple.verification_status == "VERIFIED")).first()
    if not t:
        raise HTTPException(status_code=404, detail="No verified temple record found in the Kalvettu archive.")

    # Dynamic Wikipedia & AI enrichment on demand
    if refresh or not t.history or not t.architecture:
        try:
            from services.ai_wiki_engine import fetch_wikipedia_details, synthesize_with_ai
            wiki_target = getattr(t, "wikipedia_url", None) or t.name_en
            wiki_data = await fetch_wikipedia_details(wiki_target)
            if wiki_data:
                ai_res = await synthesize_with_ai(t.name_en, wiki_data)
                if ai_res.get("history") and (refresh or not t.history):
                    t.history = ai_res["history"]
                if ai_res.get("architecture") and (refresh or not t.architecture):
                    t.architecture = ai_res["architecture"]
                if ai_res.get("summary") and (refresh or not t.summary):
                    t.summary = ai_res["summary"]
                if wiki_data.get("wikipedia_url"):
                    t.wikipedia_url = wiki_data["wikipedia_url"]
                session.add(t)
                session.commit()
                session.refresh(t)
        except Exception as e:
            logger.warning(f"On-demand enrichment error for {t.name_en}: {e}")

    imgs = session.exec(select(Image).where(Image.entity_type == "TEMPLE", Image.entity_slug == slug)).all()
    image_dtos = [ImageDto.model_validate(im) for im in imgs]

    inscriptions = session.exec(select(Inscription).where(Inscription.temple_slug == slug, Inscription.verification_status == "VERIFIED")).all()
    ins_cards = [to_ins_card(i, session) for i in inscriptions]

    locations = session.exec(select(InscriptionLocation).where(InscriptionLocation.temple_slug == slug)).all()
    loc_dtos = [InscriptionLocationDto.model_validate(l) for l in locations]

    dynasty = session.exec(select(Dynasty).where(Dynasty.slug == t.dynasty_slug)).first() if t.dynasty_slug else None
    district = session.exec(select(District).where(District.slug == t.district_slug)).first() if t.district_slug else None
    
    source = None
    if t.source_id:
        src = session.exec(select(Source).where(Source.id == t.source_id)).first()
        if src:
            source = SourceDto.model_validate(src)

    return TempleDetail(
        temple=to_temple_card(t, session),
        images=image_dtos,
        inscriptions=ins_cards,
        locations=loc_dtos,
        dynasty=DynastyDto.model_validate(dynasty) if dynasty else None,
        district=DistrictDto.model_validate(district) if district else None,
        source=source
    )

@router.post("/temples/{slug}/enrich", response_model=TempleDetail)
async def enrich_temple(slug: str, session: Session = Depends(get_session)):
    """
    Force-fetch latest data from Wikipedia and re-synthesize easy-to-understand History and Architecture using AI.
    """
    return await get_temple(slug=slug, refresh=True, session=session)

@router.post("/temples/ai-fetch-wiki", response_model=TempleDetail)
async def ai_fetch_wiki_temple(req: WikiFetchRequest, session: Session = Depends(get_session)):
    """
    On-demand AI Internet Fetching:
    Fetches real temple info from Wikipedia + Wikimedia Commons, synthesizes history & architecture with AI,
    persists the temple, images, and epigraph records, and returns the full TempleDetail.
    """
    from services.ai_wiki_engine import ingest_temple_from_query_or_url
    slug = await ingest_temple_from_query_or_url(req.query_or_url, session)
    if not slug:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find or fetch a verified temple article on Wikipedia for '{req.query_or_url}'. Please check spelling or provide a direct Wikipedia link."
        )
    return await get_temple(slug=slug, session=session)

@router.get("/locations/{temple_slug}", response_model=List[InscriptionLocationDto])
@router.get("/temples/{temple_slug}/locations", response_model=List[InscriptionLocationDto])
def get_temple_locations(temple_slug: str, session: Session = Depends(get_session)):
    locs = session.exec(
        select(InscriptionLocation).where(InscriptionLocation.temple_slug == temple_slug)
    ).all()
    return [
        InscriptionLocationDto(
            id=l.id,
            templeSlug=l.temple_slug,
            inscriptionSlug=l.inscription_slug,
            label=l.label,
            area=l.area,
            description=l.description,
            mapX=l.map_x,
            mapY=l.map_y
        )
        for l in locs
    ]

@router.get("/inscriptions", response_model=List[InscriptionCard])
def get_inscriptions(
    q: Optional[str] = None, 
    temple: Optional[str] = None, 
    dynasty: Optional[str] = None, 
    ruler: Optional[str] = None, 
    district: Optional[str] = None, 
    session: Session = Depends(get_session)
):
    """
    Search inscriptions by title, identifier, ruler, dynasty, language, location, or content.
    """
    query = select(Inscription).where(Inscription.verification_status == "VERIFIED")

    if temple:
        query = query.where(Inscription.temple_slug == temple)
    if dynasty:
        query = query.where(Inscription.dynasty_slug == dynasty)
    if ruler:
        query = query.where(Inscription.ruler_slug == ruler)

    if district:
        temple_slugs_in_district = session.exec(
            select(Temple.slug).where(Temple.district_slug == district)
        ).all()
        query = query.where(Inscription.temple_slug.in_(temple_slugs_in_district))

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Inscription.title.ilike(term),
                Inscription.title_ta.ilike(term),
                Inscription.reference_id.ilike(term),
                Inscription.are_number.ilike(term),
                Inscription.sii_reference.ilike(term),
                Inscription.physical_location.ilike(term),
                Inscription.translation.ilike(term),
                Inscription.simple_explanation.ilike(term),
                Inscription.original_text.ilike(term)
            )
        )

    inscriptions = session.exec(query).all()
    
    # Batch fetch images to prevent N+1 query issue
    inscription_slugs = [i.slug for i in inscriptions]
    temple_slugs = list(set([i.temple_slug for i in inscriptions]))
    
    image_map = {}
    temple_image_map = {}
    
    if inscription_slugs or temple_slugs:
        # Fetch inscription images
        if inscription_slugs:
            ins_images = session.exec(
                select(Image).where(
                    Image.entity_type == "INSCRIPTION",
                    Image.entity_slug.in_(inscription_slugs),
                    Image.verification_status == "VERIFIED"
                )
            ).all()
            for img in ins_images:
                if img.entity_slug not in image_map:
                    image_map[img.entity_slug] = img.thumb_url if img.thumb_url else img.image_url
                    
        # Fetch fallback temple images
        if temple_slugs:
            temple_images = session.exec(
                select(Image).where(
                    Image.entity_type == "TEMPLE",
                    Image.entity_slug.in_(temple_slugs),
                    Image.verification_status == "VERIFIED"
                )
            ).all()
            for img in temple_images:
                if img.entity_slug not in temple_image_map:
                    temple_image_map[img.entity_slug] = img.thumb_url if img.thumb_url else img.image_url

    return [to_ins_card(i, session=None, image_map=image_map, temple_image_map=temple_image_map) for i in inscriptions]

@router.get("/inscriptions/{slug}", response_model=InscriptionDetail)
def get_inscription(slug: str, session: Session = Depends(get_session)):
    """
    Retrieve single verified inscription detail with full source provenance.
    """
    i = session.exec(select(Inscription).where(Inscription.slug == slug, Inscription.verification_status == "VERIFIED")).first()
    if not i:
        raise HTTPException(status_code=404, detail="No verified inscription record found in the Kalvettu archive.")

    imgs = session.exec(select(Image).where(Image.entity_type == "INSCRIPTION", Image.entity_slug == slug)).all()
    image_dtos = [ImageDto.model_validate(im) for im in imgs]

    t = session.exec(select(Temple).where(Temple.slug == i.temple_slug)).first()
    temple_card = to_temple_card(t, session) if t else None

    source = None
    if i.source_id:
        src = session.exec(select(Source).where(Source.id == i.source_id)).first()
        if src:
            source = SourceDto.model_validate(src)

    return InscriptionDetail(
        id=i.id,
        slug=i.slug,
        temple_slug=i.temple_slug,
        title=i.title,
        title_ta=i.title_ta,
        reference_id=i.reference_id,
        are_number=i.are_number,
        sii_reference=i.sii_reference,
        epigraphia_indica=i.epigraphia_indica,
        ruler_slug=i.ruler_slug,
        dynasty_slug=i.dynasty_slug,
        regnal_year=i.regnal_year,
        date_note=i.date_note,
        language=i.language,
        script=i.script,
        physical_location=i.physical_location,
        original_text=i.original_text,
        original_text_source=i.original_text_source,
        transliteration=i.transliteration,
        translation=i.translation,
        translation_source=i.translation_source,
        simple_explanation=i.simple_explanation,
        historical_significance=i.historical_significance,
        source_citation=i.source_citation,
        source_url=i.source_url,
        verified=i.verified,
        verification_status=i.verification_status,
        images=image_dtos,
        temple=temple_card,
        source=source
    )

@router.get("/dynasties", response_model=List[DynastyDto])
def get_dynasties(session: Session = Depends(get_session)):
    return [DynastyDto.model_validate(d) for d in session.exec(select(Dynasty)).all()]

@router.get("/rulers", response_model=List[RulerDto])
def get_rulers(dynasty: Optional[str] = None, session: Session = Depends(get_session)):
    if dynasty:
        rulers = session.exec(select(Ruler).where(Ruler.dynasty_slug == dynasty)).all()
    else:
        rulers = session.exec(select(Ruler)).all()
    return [RulerDto.model_validate(r) for r in rulers]

@router.get("/districts", response_model=List[DistrictDto])
def get_districts(session: Session = Depends(get_session)):
    return [DistrictDto.model_validate(d) for d in session.exec(select(District)).all()]

@router.get("/temples/{slug}/locations", response_model=List[InscriptionLocationDto])
def get_locations(slug: str, session: Session = Depends(get_session)):
    locs = session.exec(select(InscriptionLocation).where(InscriptionLocation.temple_slug == slug)).all()
    return [InscriptionLocationDto.model_validate(l) for l in locs]

@router.get("/timeline", response_model=List[TimelineEvent])
def get_timeline(session: Session = Depends(get_session)):
    events = session.exec(select(HistoricalEvent)).all()
    dtos = []
    for e in events:
        dtos.append(TimelineEvent(
            year=e.year,
            title=e.title,
            description=e.description or "",
            entity_type=e.entity_type,
            entity_slug=e.entity_slug,
            type=e.entity_type,
            related_slug=e.entity_slug,
            source_note=e.source_note
        ))
    def get_sort_key(e: TimelineEvent):
        try:
            return int(e.year)
        except ValueError:
            return 999999
    return sorted(dtos, key=get_sort_key)

@router.get("/sources/{id}", response_model=SourceDto)
def get_source(id: int, session: Session = Depends(get_session)):
    src = session.exec(select(Source).where(Source.id == id)).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found.")
    return SourceDto.model_validate(src)

@router.get("/sources", response_model=List[SourceDto])
def get_all_sources(session: Session = Depends(get_session)):
    sources = session.exec(select(Source).order_by(Source.source_priority)).all()
    return [SourceDto.model_validate(s) for s in sources]

@router.get("/search", response_model=SearchResult)
def search(q: str, session: Session = Depends(get_session)):
    """
    Global search across Temples, Inscriptions, Rulers, Dynasties, and Districts.
    """
    temple_results = get_temples(q=q, session=session)
    inscription_results = get_inscriptions(q=q, session=session)
    
    term = f"%{q.strip()}%"
    dynasties = [
        DynastyDto.model_validate(d) for d in session.exec(
            select(Dynasty).where(or_(Dynasty.name_en.ilike(term), Dynasty.name_ta.ilike(term)))
        ).all()
    ]
    rulers = [
        RulerDto.model_validate(r) for r in session.exec(
            select(Ruler).where(or_(Ruler.name_en.ilike(term), Ruler.name_ta.ilike(term)))
        ).all()
    ]
    districts = [
        DistrictDto.model_validate(d) for d in session.exec(
            select(District).where(District.name_en.ilike(term))
        ).all()
    ]

    total = len(temple_results) + len(inscription_results) + len(dynasties) + len(rulers) + len(districts)

    return SearchResult(
        temples=temple_results,
        inscriptions=inscription_results,
        dynasties=dynasties,
        rulers=rulers,
        districts=districts,
        total_matches=total
    )
