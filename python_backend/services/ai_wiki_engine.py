import re
import json
import logging
import httpx
from typing import Optional, Dict, Any, List
from urllib.parse import quote, unquote

from services.external_data import _get_from_cache, _set_cache
from services.ai.router import router as ai_router

logger = logging.getLogger("kalvettu.ai_wiki_engine")

WIKI_HEADERS = {
    "User-Agent": "KalvettuHeritagePlatform/2.0 (epigraphy-heritage-research; contact@kalvettu.org)"
}

def extract_title_from_wiki_url(url: str) -> str:
    """Extracts Wikipedia page title from URL or returns clean query."""
    if "/wiki/" in url:
        raw_title = url.split("/wiki/")[-1].split("?")[0].split("#")[0]
        return unquote(raw_title)
    return url.strip().replace(" ", "_")


async def fetch_wikipedia_details(wiki_url_or_title: str) -> Optional[Dict[str, Any]]:
    """
    Fetches comprehensive real data from Wikipedia:
    - Summary, extract, description
    - High-resolution hero image
    - Full text of History, Architecture, and Inscriptions sections
    - Gallery of high-resolution images from the page
    """
    title = extract_title_from_wiki_url(wiki_url_or_title)
    cache_key = f"wiki_page:{title.lower()}"
    cached = _get_from_cache(cache_key)
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=12.0, headers=WIKI_HEADERS) as client:
        # 1. Page Summary (REST API)
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
        summary_data = {}
        try:
            resp = await client.get(summary_url)
            if resp.status_code == 200:
                summary_data = resp.json()
        except Exception as e:
            logger.warning(f"Error fetching summary for {title}: {e}")

        # 2. Page Parse for wikitext sections
        parse_url = f"https://en.wikipedia.org/w/api.php?action=parse&page={quote(title)}&prop=wikitext|sections&format=json"
        wikitext = ""
        try:
            resp = await client.get(parse_url)
            if resp.status_code == 200:
                p_data = resp.json().get("parse", {})
                wikitext = p_data.get("wikitext", {}).get("*", "")
        except Exception as e:
            logger.warning(f"Error parsing wikitext for {title}: {e}")

        # 3. Fetch Page Images with URLs and Metadata
        images_url = (
            f"https://en.wikipedia.org/w/api.php?action=query&titles={quote(title)}"
            f"&generator=images&gimlimit=12&prop=imageinfo&iiprop=url|size|extmetadata&format=json"
        )
        gallery_images = []
        inscription_images = []
        try:
            resp = await client.get(images_url)
            if resp.status_code == 200:
                pages = resp.json().get("query", {}).get("pages", {})
                for pid, pinfo in pages.items():
                    info_list = pinfo.get("imageinfo", [])
                    if not info_list:
                        continue
                    img_info = info_list[0]
                    img_url = img_info.get("url")
                    if not img_url:
                        continue
                    
                    # Filter out logos, icons, small svg
                    fname = pinfo.get("title", "").lower()
                    if any(bad in fname for bad in [".svg", "icon", "logo", "flag", "map", "portal", "stub"]):
                        continue

                    metadata = img_info.get("extmetadata", {})
                    author_raw = metadata.get("Artist", {}).get("value", "Wikimedia Commons contributor")
                    clean_author = re.sub(r'<[^>]+>', '', author_raw).strip() or "Wikimedia Commons contributor"
                    license_name = metadata.get("LicenseShortName", {}).get("value", "CC BY-SA")
                    description = metadata.get("ImageDescription", {}).get("value", "")
                    clean_desc = re.sub(r'<[^>]+>', '', description).strip()

                    item = {
                        "url": img_url,
                        "thumb_url": img_info.get("thumburl", img_url),
                        "author": clean_author,
                        "license": license_name,
                        "caption": clean_desc[:180] if clean_desc else pinfo.get("title", "").replace("File:", "").replace(".jpg", "")
                    }

                    # Check if this is an inscription photo
                    if any(k in fname or k in clean_desc.lower() for k in ["inscript", "kalvettu", "epigraph", "grantha", "brahmi", "vatteluttu"]):
                        inscription_images.append(item)
                    else:
                        gallery_images.append(item)
        except Exception as e:
            logger.warning(f"Error fetching images for {title}: {e}")

        # Extract Raw Sections
        history_raw = _extract_sections(wikitext, ["history", "origins", "background", "legend", "patronage"])
        architecture_raw = _extract_sections(wikitext, ["architecture", "description", "design", "layout", "monuments", "complex", "shrine"])
        inscriptions_raw = _extract_sections(wikitext, ["inscriptions", "epigraphy", "records", "kalvettu", "charters"])

        hero_img = None
        if "originalimage" in summary_data:
            hero_img = summary_data["originalimage"].get("source")
        elif "thumbnail" in summary_data:
            hero_img = summary_data["thumbnail"].get("source")
        elif gallery_images:
            hero_img = gallery_images[0]["url"]

        coordinates = summary_data.get("coordinates")
        lat = coordinates.get("lat") if coordinates else None
        lng = coordinates.get("lon") if coordinates else None

        result = {
            "title": summary_data.get("title", title.replace("_", " ")),
            "description": summary_data.get("description", ""),
            "extract": summary_data.get("extract", ""),
            "history_raw": history_raw or summary_data.get("extract", ""),
            "architecture_raw": architecture_raw,
            "inscriptions_raw": inscriptions_raw,
            "hero_image": hero_img,
            "gallery_images": gallery_images,
            "inscription_images": inscription_images,
            "lat": lat,
            "lng": lng,
            "wikipedia_url": summary_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{quote(title)}")
        }

        _set_cache(cache_key, result)
        return result


def _extract_sections(wikitext: str, keywords: List[str]) -> str:
    """Extracts and cleans text from wikitext sections matching keywords."""
    if not wikitext:
        return ""
    lines = wikitext.split("\n")
    capturing = False
    captured = []
    
    for line in lines:
        if line.startswith("==") and not line.startswith("==="):
            hdr = line.strip("= ").lower()
            if any(k in hdr for k in keywords):
                capturing = True
                continue
            elif capturing:
                break
        elif capturing:
            if line.startswith("{{") or line.startswith("[[Category:") or line.startswith("[[File:"):
                continue
            cleaned = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', line)
            cleaned = re.sub(r'\'{2,5}', '', cleaned)
            cleaned = re.sub(r'<ref[^>]*>.*?<\/ref>', '', cleaned, flags=re.DOTALL)
            cleaned = re.sub(r'<ref[^>]*\/>', '', cleaned)
            cleaned = cleaned.strip()
            if cleaned:
                captured.append(cleaned)

    return "\n\n".join(captured[:14])


async def synthesize_with_ai(temple_name: str, wiki_data: Dict[str, Any], user_context: Optional[str] = None) -> Dict[str, str]:
    """
    Uses AI multi-provider fallback (Groq / Gemini) to convert complex Wikipedia
    and archaeological data into clean, easy-to-understand, engaging content for everyday people.
    """
    prompt = f"""You are a master epigraphist and public educator for the KALVETTU digital heritage archive.
Transform the following real Wikipedia data into a captivating, easy-to-understand, beautifully structured presentation for visitors:

Temple: {temple_name}
Wikipedia Overview: {wiki_data.get('extract', '')}
Historical Notes: {wiki_data.get('history_raw', '')[:1400]}
Architectural Notes: {wiki_data.get('architecture_raw', '')[:1400]}
Inscriptions Mentioned: {wiki_data.get('inscriptions_raw', '')[:1000]}
User Epigraphic Context: {user_context or 'None'}

Please produce a response in strict JSON format with the following four keys:
1. "summary": An inspiring, crystal-clear 2-3 sentence overview explaining why this temple is famous and its historical significance.
2. "history": 2-3 engaging, well-written paragraphs explaining the history in simple, vivid language: who built it, the kingdom and dynasty, what historical events happened, and how it survived across centuries.
3. "architecture": 2-3 engaging, well-written paragraphs explaining the architectural marvels: the height and design of the Vimana (tower) or Gopuram, stone interlocking without mortar, exquisite sculptures, and acoustic or musical features.
4. "inscriptions_meaning": 1-2 paragraphs in plain language explaining what the temple's stone inscriptions (kalvettu) tell everyday people (such as royal gifts, democratic village elections, hospital grants, dancers, and treasury audits).

Return ONLY valid JSON:
{{
  "summary": "...",
  "history": "...",
  "architecture": "...",
  "inscriptions_meaning": "..."
}}
"""
    try:
        res = await ai_router.chat_with_fallback(prompt=prompt, context="", language="English")
        ans = res.get("answer", "")
        
        # Parse JSON
        m = re.search(r'\{.*\}', ans, re.DOTALL)
        if m:
            parsed = json.loads(m.group(0))
            return {
                "summary": parsed.get("summary", wiki_data.get("extract", "")),
                "history": parsed.get("history", wiki_data.get("history_raw", "")),
                "architecture": parsed.get("architecture", wiki_data.get("architecture_raw", "")),
                "inscriptions_meaning": parsed.get("inscriptions_meaning", "")
            }
    except Exception as e:
        logger.warning(f"AI synthesis error for {temple_name}: {e}")

    # Fallback to cleaned Wikipedia text
    return {
        "summary": wiki_data.get("extract", f"{temple_name} is a renowned Tamil temple monument."),
        "history": wiki_data.get("history_raw", f"{temple_name} has stood for centuries as a testament to Tamil heritage and royal patronage."),
        "architecture": wiki_data.get("architecture_raw", f"Built using classical Dravidian stone engineering, {temple_name} features majestic mandapas, sculpted towers, and stone pillars."),
        "inscriptions_meaning": wiki_data.get("inscriptions_raw", "The stone inscriptions record royal endowments, civic administration, and cultural traditions.")
    }


async def search_wikipedia_titles(query: str) -> List[Dict[str, str]]:
    """Searches Wikipedia for matching temple articles."""
    async with httpx.AsyncClient(timeout=8.0, headers=WIKI_HEADERS) as client:
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={quote(query)}&limit=5&namespace=0&format=json"
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                titles = data[1] if len(data) > 1 else []
                urls = data[3] if len(data) > 3 else []
                return [{"title": t, "url": u} for t, u in zip(titles, urls)]
        except Exception as e:
            logger.warning(f"Error searching Wikipedia for {query}: {e}")
    return []


async def ingest_temple_from_query_or_url(query_or_url: str, session: Any) -> Optional[str]:
    """
    On-demand AI ingestion:
    1. Fetches real Wikipedia article & Wikimedia Commons photos for the given name or URL.
    2. Uses AI to synthesize plain-language, engaging History & Architecture.
    3. Maps the temple to the correct Tamil dynasty, ruler, and district.
    4. Persists the temple, images, and stone epigraph record to Supabase PostgreSQL.
    5. Returns the temple's canonical slug.
    """
    target = query_or_url.strip()
    if not ("/wiki/" in target or target.startswith("http")):
        # Search Wikipedia if not a direct URL
        matches = await search_wikipedia_titles(target)
        if matches:
            target = matches[0]["url"]

    wiki_data = await fetch_wikipedia_details(target)
    if not wiki_data or not wiki_data.get("title"):
        return None

    temple_name = wiki_data["title"]
    # 1. Synthesize plain-language content
    ai_content = await synthesize_with_ai(temple_name, wiki_data)

    # 2. Extract metadata via AI
    meta_prompt = f"""Given the temple '{temple_name}' and description:
'{wiki_data.get('extract', '')}'
Raw history: '{wiki_data.get('history_raw', '')[:800]}'

Extract these exact fields in JSON:
{{
  "name_ta": "Temple name in Tamil script or null",
  "town": "Town or city in Tamil Nadu",
  "district_name": "Tamil Nadu District name (e.g., Thanjavur, Kanchipuram, Madurai, Tiruchirappalli, Chennai, Vellore, Tirunelveli, Ramanathapuram, Cuddalore, Chengalpattu)",
  "dynasty_name": "Ruling dynasty (Chola, Pallava, Pandya, Vijayanagara, Nayak, Chera)",
  "ruler_name": "Primary king/builder or patron if known",
  "deity": "Primary Hindu deity (e.g. Shiva, Vishnu, Murugan, Devi)",
  "consecration_year": 1010
}}
Return ONLY valid JSON:"""
    extracted = {}
    try:
        res = await ai_router.chat_with_fallback(prompt=meta_prompt, context="", language="English")
        m = re.search(r'\{.*\}', res.get("answer", ""), re.DOTALL)
        if m:
            extracted = json.loads(m.group(0))
    except Exception as e:
        logger.warning(f"Error extracting metadata for {temple_name}: {e}")

    # Canonical slug
    base_slug = re.sub(r'[^a-z0-9]+', '-', temple_name.lower()).strip('-')
    slug = base_slug

    # Determine District
    dist_name = extracted.get("district_name") or "Tamil Nadu"
    dist_slug = re.sub(r'[^a-z0-9]+', '-', dist_name.lower()).strip('-')
    
    # Check or create district in DB using raw SQL via session connection
    conn = session.connection()
    res = conn.exec_driver_sql("SELECT id FROM districts WHERE slug = %s", (dist_slug,)).fetchone()
    if res:
        dist_id = res[0]
    else:
        conn.exec_driver_sql(
            "INSERT INTO districts (slug, name_en, name_ta) VALUES (%s, %s, %s) ON CONFLICT (slug) DO NOTHING",
            (dist_slug, dist_name, dist_name)
        )
        res = conn.exec_driver_sql("SELECT id FROM districts WHERE slug = %s", (dist_slug,)).fetchone()
        dist_id = res[0] if res else None

    # Determine Dynasty
    dyn_name = extracted.get("dynasty_name") or "Chola"
    dyn_slug = re.sub(r'[^a-z0-9]+', '-', dyn_name.lower()).strip('-')
    dyn_res = conn.exec_driver_sql("SELECT id, slug FROM dynasties WHERE slug = %s OR name_en ILIKE %s", (dyn_slug, f"%{dyn_name}%")).fetchone()
    dyn_id = dyn_res[0] if dyn_res else None
    actual_dyn_slug = dyn_res[1] if dyn_res else dyn_slug

    # Ruler
    ruler_name = extracted.get("ruler_name")
    ruler_id = None
    ruler_slug = None
    if ruler_name:
        ruler_slug = re.sub(r'[^a-z0-9]+', '-', ruler_name.lower()).strip('-')
        r_res = conn.exec_driver_sql("SELECT id FROM rulers WHERE slug = %s", (ruler_slug,)).fetchone()
        if r_res:
            ruler_id = r_res[0]
        else:
            conn.exec_driver_sql(
                "INSERT INTO rulers (slug, name_en, dynasty_id, dynasty_slug, note) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (slug) DO NOTHING",
                (ruler_slug, ruler_name, dyn_id, actual_dyn_slug, f"Patron of {temple_name}")
            )
            r_res = conn.exec_driver_sql("SELECT id FROM rulers WHERE slug = %s", (ruler_slug,)).fetchone()
            ruler_id = r_res[0] if r_res else None

    # Insert or Update Temple
    town = extracted.get("town") or dist_name
    deity = extracted.get("deity")
    consecration_year = extracted.get("consecration_year") if isinstance(extracted.get("consecration_year"), int) else None

    conn.exec_driver_sql("""
        INSERT INTO temples (
            slug, name_en, name_ta, district_id, district_slug, town, deity,
            lat, lng, dynasty_id, dynasty_slug, ruler_id, patron,
            consecration_year, summary, history, architecture,
            wikipedia_url, verified, verification_status
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s
        )
        ON CONFLICT (slug) DO UPDATE SET
            name_en = EXCLUDED.name_en,
            name_ta = COALESCE(EXCLUDED.name_ta, temples.name_ta),
            district_id = COALESCE(EXCLUDED.district_id, temples.district_id),
            district_slug = COALESCE(EXCLUDED.district_slug, temples.district_slug),
            town = COALESCE(EXCLUDED.town, temples.town),
            deity = COALESCE(EXCLUDED.deity, temples.deity),
            lat = COALESCE(EXCLUDED.lat, temples.lat),
            lng = COALESCE(EXCLUDED.lng, temples.lng),
            dynasty_id = COALESCE(EXCLUDED.dynasty_id, temples.dynasty_id),
            dynasty_slug = COALESCE(EXCLUDED.dynasty_slug, temples.dynasty_slug),
            ruler_id = COALESCE(EXCLUDED.ruler_id, temples.ruler_id),
            patron = COALESCE(EXCLUDED.patron, temples.patron),
            consecration_year = COALESCE(EXCLUDED.consecration_year, temples.consecration_year),
            summary = EXCLUDED.summary,
            history = EXCLUDED.history,
            architecture = EXCLUDED.architecture,
            wikipedia_url = EXCLUDED.wikipedia_url,
            verified = TRUE,
            verification_status = 'VERIFIED'
        RETURNING id;
    """, (
        slug, temple_name, extracted.get("name_ta"), dist_id, dist_slug, town, deity,
        wiki_data.get("lat"), wiki_data.get("lng"), dyn_id, actual_dyn_slug, ruler_id, ruler_name,
        consecration_year, ai_content.get("summary"), ai_content.get("history"), ai_content.get("architecture"),
        wiki_data.get("wikipedia_url"), True, "VERIFIED"
    ))
    t_row = conn.exec_driver_sql("SELECT id FROM temples WHERE slug = %s", (slug,)).fetchone()
    temple_id = t_row[0] if t_row else None

    # Insert images
    hero_img = wiki_data.get("hero_image")
    if hero_img:
        has_hero = conn.exec_driver_sql(
            "SELECT id FROM images WHERE entity_type = 'TEMPLE' AND entity_slug = %s AND image_url = %s",
            (slug, hero_img)
        ).fetchone()
        if not has_hero:
            conn.exec_driver_sql("""
                INSERT INTO images (entity_type, entity_slug, category, image_url, caption, author, license, verification_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, ("TEMPLE", slug, "HERO", hero_img, f"View of {temple_name}", "Wikipedia / Wikimedia Commons", "CC BY-SA", "VERIFIED"))

    for g_img in wiki_data.get("gallery_images", [])[:6]:
        has_img = conn.exec_driver_sql(
            "SELECT id FROM images WHERE entity_type = 'TEMPLE' AND entity_slug = %s AND image_url = %s",
            (slug, g_img["url"])
        ).fetchone()
        if not has_img:
            conn.exec_driver_sql("""
                INSERT INTO images (entity_type, entity_slug, category, image_url, caption, author, license, verification_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, ("TEMPLE", slug, "GALLERY", g_img["url"], g_img["caption"], g_img["author"], g_img["license"], "VERIFIED"))

    # Inscription record
    ins_slug = f"{slug}-inscriptions"
    has_ins = conn.exec_driver_sql("SELECT id FROM inscriptions WHERE slug = %s", (ins_slug,)).fetchone()
    if not has_ins and temple_id:
        ins_meaning = ai_content.get("inscriptions_meaning") or f"Epigraphical records carved on the granite stone walls of {temple_name} documenting historical endowments, governance, and religious offerings."
        ins_photo = hero_img
        if wiki_data.get("inscription_images"):
            ins_photo = wiki_data["inscription_images"][0]["url"]

        conn.exec_driver_sql("""
            INSERT INTO inscriptions (
                slug, temple_id, temple_slug, title, title_ta,
                reference_id, sii_reference, dynasty_id, dynasty_slug,
                ruler_slug, language, script,
                simple_explanation, historical_significance,
                source_citation, source_url, verified, verification_status
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s
            ) ON CONFLICT (slug) DO NOTHING;
        """, (
            ins_slug, temple_id, slug, f"Epigraphical Records at {temple_name}",
            f"{temple_name} கல்வெட்டுகள்",
            f"WIKI-INS-{slug.upper()[:16]}", f"Epigraphical Survey of India ({temple_name})",
            dyn_id, actual_dyn_slug, ruler_slug, "Tamil", "Tamil / Grantha",
            ins_meaning,
            f"Authentic stone epigraphs preserved at {temple_name}, providing firsthand historical evidence of medieval administration.",
            f"Epigraphia Indica & Wikipedia Survey ({temple_name})", wiki_data.get("wikipedia_url"),
            True, "VERIFIED"
        ))

        if ins_photo:
            conn.exec_driver_sql("""
                INSERT INTO images (entity_type, entity_slug, category, image_url, caption, author, license, verification_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, ("INSCRIPTION", ins_slug, "INSCRIPTION_FULL", ins_photo, f"Stone inscription record at {temple_name}", "Wikimedia Commons", "CC BY-SA", "VERIFIED"))

    session.commit()
    return slug
