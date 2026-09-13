from sqlmodel import Session, select, or_, text
from typing import List, Dict, Any, Tuple
from database import engine
from models import Temple, Inscription, Source
from schemas import SourceCitation

def search_verified_context(query: str, limit: int = 5) -> Tuple[str, List[SourceCitation], List[str], List[str]]:
    """
    Retrieves verified archive records from Supabase PostgreSQL to ground RAG.
    Returns: (context_string, source_citations, related_temples, related_inscriptions)
    """
    q_words = [w.strip() for w in query.lower().split() if len(w.strip()) > 2]
    
    with Session(engine) as session:
        # 1. Match Inscriptions
        # Use full-text search or ILIKE on title, translation, simple_explanation, ruler_slug, dynasty_slug
        matched_inscriptions: List[Inscription] = []
        
        # Priority: match title or reference ID first
        for word in q_words[:3]:
            stmt = select(Inscription).where(
                Inscription.verification_status == "VERIFIED",
                or_(
                    Inscription.title.ilike(f"%{word}%"),
                    Inscription.translation.ilike(f"%{word}%"),
                    Inscription.simple_explanation.ilike(f"%{word}%"),
                    Inscription.ruler_slug.ilike(f"%{word}%"),
                    Inscription.dynasty_slug.ilike(f"%{word}%"),
                    Inscription.temple_slug.ilike(f"%{word}%"),
                    Inscription.physical_location.ilike(f"%{word}%")
                )
            ).limit(limit)
            results = session.exec(stmt).all()
            for r in results:
                if r.id not in [m.id for m in matched_inscriptions]:
                    matched_inscriptions.append(r)
        
        # If specific query matches nothing, include top verified records as context
        if not matched_inscriptions:
            matched_inscriptions = session.exec(
                select(Inscription).where(Inscription.verification_status == "VERIFIED").limit(4)
            ).all()

        # 2. Match Temples
        matched_temples: List[Temple] = []
        for word in q_words[:3]:
            stmt = select(Temple).where(
                Temple.verification_status == "VERIFIED",
                or_(
                    Temple.name_en.ilike(f"%{word}%"),
                    Temple.name_ta.ilike(f"%{word}%"),
                    Temple.alternate_names.ilike(f"%{word}%"),
                    Temple.town.ilike(f"%{word}%"),
                    Temple.deity.ilike(f"%{word}%")
                )
            ).limit(3)
            results = session.exec(stmt).all()
            for t in results:
                if t.id not in [m.id for m in matched_temples]:
                    matched_temples.append(t)

        if not matched_temples:
            matched_temples = session.exec(
                select(Temple).where(Temple.verification_status == "VERIFIED").limit(3)
            ).all()

        # 3. Assemble Context & Citations
        citations: List[SourceCitation] = []
        related_temples: List[str] = [t.name_en for t in matched_temples]
        related_inscriptions: List[str] = [i.title for i in matched_inscriptions]

        context_blocks = ["[VERIFIED TEMPLES]"]
        for t in matched_temples:
            t_block = (
                f"- Temple: {t.name_en} (Tamil: {t.name_ta or 'N/A'})\n"
                f"  Town/District: {t.town or 'Unknown'}, {t.district_slug}\n"
                f"  Dynasty: {t.dynasty_slug}, Patron: {t.patron or 'Unknown'}\n"
                f"  Consecration: ≈ {t.consecration_year or 'Unknown'} CE\n"
                f"  Summary: {t.summary or t.history or 'N/A'}\n"
            )
            context_blocks.append(t_block)

        context_blocks.append("\n[VERIFIED INSCRIPTIONS]")
        for i in matched_inscriptions:
            i_block = (
                f"- Title: {i.title} (Ref: {i.reference_id or i.sii_reference or 'N/A'})\n"
                f"  Temple: {i.temple_slug}, Ruler: {i.ruler_slug or 'N/A'}, Dynasty: {i.dynasty_slug or 'N/A'}\n"
                f"  Regnal Year / Date: {i.regnal_year or i.date_note or 'N/A'}\n"
                f"  Physical Location: {i.physical_location or 'N/A'}\n"
                f"  Translation: {i.translation or 'Translation not available'}\n"
                f"  Meaning/Significance: {i.simple_explanation or i.historical_significance or 'N/A'}\n"
                f"  Primary Source Citation: {i.source_citation}\n"
            )
            context_blocks.append(i_block)
            
            # Extract source
            if i.source_id:
                src = session.exec(select(Source).where(Source.id == i.source_id)).first()
                if src:
                    citations.append(SourceCitation(
                        institution=src.institution,
                        publication=src.publication,
                        reference=src.reference,
                        url=src.url
                    ))
            elif i.source_citation:
                citations.append(SourceCitation(
                    institution="Archaeological Survey of India / Published Epigraphy",
                    reference=i.source_citation,
                    url=i.source_url
                ))

        # Deduplicate citations by reference
        seen_refs = set()
        dedup_citations = []
        for c in citations:
            if c.reference not in seen_refs:
                seen_refs.add(c.reference)
                dedup_citations.append(c)

        context_str = "\n".join(context_blocks)
        return context_str, dedup_citations, related_temples, related_inscriptions
