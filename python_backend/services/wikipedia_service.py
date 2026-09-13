import re
import httpx
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import quote
from services.external_data import validate_external_url, _get_from_cache, _set_cache
from services.ai.router import router as ai_router

logger = logging.getLogger("kalvettu.wikipedia")

WIKI_HEADERS = {
    "User-Agent": "KalvettuHeritagePlatform/2.0 (Tamil temple epigraphy research; contact@kalvettu.org)"
}

async def fetch_wikipedia_temple_data(temple_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches article summary, sections, images, and content from Wikipedia for a given temple.
    """
    cache_key = f"wiki_temple:{temple_name.lower().strip()}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    clean_name = temple_name.replace("Temple", "").replace("Kovil", "").replace("Koil", "").strip()
    search_queries = [
        f"{clean_name} Temple",
        clean_name,
        temple_name
    ]

    async with httpx.AsyncClient(timeout=10.0, headers=WIKI_HEADERS) as client:
        page_title = None

        # 1. Search for page title
        for query in search_queries:
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(query)}&format=json&srlimit=3"
            try:
                resp = await client.get(search_url)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("query", {}).get("search", [])
                    if results:
                        page_title = results[0]["title"]
                        break
            except Exception as e:
                logger.warning(f"Wikipedia search failed for '{query}': {e}")

        if not page_title:
            page_title = clean_name.replace(" ", "_")

        # 2. Fetch Page Summary
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(page_title)}"
        summary_data = {}
        try:
            resp = await client.get(summary_url)
            if resp.status_code == 200:
                summary_data = resp.json()
        except Exception as e:
            logger.warning(f"Wikipedia summary fetch failed for '{page_title}': {e}")

        # 3. Fetch Full Sections Text
        parse_url = f"https://en.wikipedia.org/w/api.php?action=parse&page={quote(page_title)}&prop=sections|wikitext&format=json"
        raw_sections = []
        wikitext = ""
        try:
            resp = await client.get(parse_url)
            if resp.status_code == 200:
                p_data = resp.json().get("parse", {})
                raw_sections = p_data.get("sections", [])
                wikitext = p_data.get("wikitext", {}).get("*", "")
        except Exception as e:
            logger.warning(f"Wikipedia parse failed for '{page_title}': {e}")

        # Extract History & Architecture text segments
        history_text = _extract_section_text(wikitext, ["history", "origins", "background", "patronage"])
        architecture_text = _extract_section_text(wikitext, ["architecture", "description", "design", "layout", "monuments"])
        inscriptions_text = _extract_section_text(wikitext, ["inscriptions", "epigraphy", "records", "kalvettu"])

        image_url = None
        if "originalimage" in summary_data:
            image_url = summary_data["originalimage"].get("source")
        elif "thumbnail" in summary_data:
            image_url = summary_data["thumbnail"].get("source")

        result = {
            "title": summary_data.get("title", page_title),
            "description": summary_data.get("description", ""),
            "extract": summary_data.get("extract", ""),
            "history_raw": history_text or summary_data.get("extract", ""),
            "architecture_raw": architecture_text,
            "inscriptions_raw": inscriptions_text,
            "image_url": image_url,
            "wikipedia_url": summary_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{quote(page_title)}")
        }

        _set_cache(cache_key, result)
        return result


def _extract_section_text(wikitext: str, keywords: List[str]) -> str:
    """
    Extracts plain-text from wikitext sections matching specified keywords.
    """
    if not wikitext:
        return ""
    
    lines = wikitext.split("\n")
    capturing = False
    captured_lines = []
    
    for line in lines:
        if line.startswith("==") and not line.startswith("==="):
            header = line.strip("= ").lower()
            if any(k in header for k in keywords):
                capturing = True
                continue
            elif capturing:
                break
        elif capturing:
            # Skip templates and internal categories
            if line.startswith("{{") or line.startswith("[[Category:") or line.startswith("[[File:"):
                continue
            cleaned = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', line) # [[link|text]] -> text
            cleaned = re.sub(r'\'{2,5}', '', cleaned) # bold/italic markup
            cleaned = re.sub(r'<ref[^>]*>.*?<\/ref>', '', cleaned, flags=re.DOTALL) # references
            cleaned = re.sub(r'<ref[^>]*\/>', '', cleaned)
            cleaned = cleaned.strip()
            if cleaned:
                captured_lines.append(cleaned)

    return "\n\n".join(captured_lines[:15]) # Limit to ~15 paragraphs


async def explain_temple_with_ai(temple_name: str, raw_wiki: Dict[str, Any]) -> Dict[str, str]:
    """
    Uses AI multi-provider fallback to present temple history, architecture, and inscriptions
    in an engaging, easy-to-understand manner for everyday visitors and history enthusiasts.
    """
    prompt = f"""You are a master epigraphist and storyteller for the KALVETTU digital heritage platform.
Explain the following Tamil temple to everyday modern readers in an engaging, crystal-clear, and historically accurate manner:

Temple Name: {temple_name}
Wikipedia Overview: {raw_wiki.get('extract', '')}
Raw History Data: {raw_wiki.get('history_raw', '')[:1200]}
Raw Architecture Data: {raw_wiki.get('architecture_raw', '')[:1200]}
Raw Inscriptions Data: {raw_wiki.get('inscriptions_raw', '')[:1000]}

Produce four distinct sections in simple, easy-to-understand, vivid English (no academic jargon):

1. SUMMARY: A 2-3 sentence inspiring introduction explaining what makes this monument unique.
2. EASY_HISTORY: 2-3 engaging paragraphs explaining who built it, the kingdom and dynasty, why it was created, and how it stood through time.
3. EASY_ARCHITECTURE: 2-3 engaging paragraphs explaining the architectural wonders: the soaring tower (Vimana/Gopuram), stone interlocking, sculptures, and layout.
4. EASY_INSCRIPTIONS: 1-2 paragraphs explaining what the stone inscriptions (kalvettu) reveal to us today (e.g. royal gifts, temple dancers, bronze artisans, village self-government).

Return your response in clean JSON format:
{{
  "summary": "...",
  "history": "...",
  "architecture": "...",
  "inscriptions_significance": "..."
}}
"""
    try:
        res = await ai_router.chat_with_fallback(prompt=prompt, context="", language="English")
        content = res.get("answer", "")
        
        # Extract JSON from AI response
        import json
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                return {
                    "summary": parsed.get("summary", raw_wiki.get("extract", "")),
                    "history": parsed.get("history", raw_wiki.get("history_raw", "")),
                    "architecture": parsed.get("architecture", raw_wiki.get("architecture_raw", "")),
                    "inscriptions_significance": parsed.get("inscriptions_significance", "")
                }
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"AI explanation fallback failed: {e}")

    # Fallback to cleaned Wikipedia text
    return {
        "summary": raw_wiki.get("extract", f"{temple_name} is an ancient monument renowned for its architecture and inscriptions."),
        "history": raw_wiki.get("history_raw", f"{temple_name} has stood for centuries as a testament to Tamil temple heritage."),
        "architecture": raw_wiki.get("architecture_raw", f"Built using classical Dravidian stone engineering, {temple_name} features majestic mandapas and stone carvings."),
        "inscriptions_significance": raw_wiki.get("inscriptions_raw", "The temple's stone inscriptions record historical donations, local governance, and royal patronages.")
    }
