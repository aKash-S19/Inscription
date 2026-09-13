import time
import httpx
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
import ipaddress

# Cache storage: key -> (timestamp, data)
_CACHE: Dict[str, tuple[float, Any]] = {}
CACHE_TTL = 3600 # 1 hour
MAX_CACHE_SIZE = 1000

def _prune_cache_if_needed(now: float):
    if len(_CACHE) < MAX_CACHE_SIZE:
        return
    # Remove expired keys first
    expired = [k for k, (ts, _) in _CACHE.items() if now - ts >= CACHE_TTL]
    for k in expired:
        _CACHE.pop(k, None)
    # If still above capacity, drop oldest 25% of items
    if len(_CACHE) >= MAX_CACHE_SIZE:
        sorted_keys = sorted(_CACHE.keys(), key=lambda k: _CACHE[k][0])
        for k in sorted_keys[:MAX_CACHE_SIZE // 4]:
            _CACHE.pop(k, None)

def _get_from_cache(key: str) -> Optional[Any]:
    if key in _CACHE:
        ts, data = _CACHE[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _CACHE[key]
    return None

def _set_cache(key: str, data: Any):
    now = time.time()
    _prune_cache_if_needed(now)
    _CACHE[key] = (now, data)

# SSRF Protection: Allowed domains
ALLOWED_EXTERNAL_DOMAINS = {
    "commons.wikimedia.org",
    "upload.wikimedia.org",
    "en.wikipedia.org",
    "wikipedia.org",
    "www.wikidata.org",
    "query.wikidata.org",
    "asi.nic.in",
    "whc.unesco.org",
    "archive.org"
}

def validate_external_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("https", "http"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
            
        # Reject localhost and local IPs
        if hostname in ("localhost", "127.0.0.1", "::1"):
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                return False
        except ValueError:
            pass # It is a domain name
            
        # Ensure domain is in allowed list or subdomain of allowed
        for allowed in ALLOWED_EXTERNAL_DOMAINS:
            if hostname == allowed or hostname.endswith("." + allowed):
                return True
        return False
    except Exception:
        return False

# 1. Wikimedia Commons Image Service
async def search_wikimedia_images(temple_name: str, limit: int = 6) -> List[Dict[str, Any]]:
    cache_key = f"commons:{temple_name}:{limit}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{temple_name} temple",
        "gsrnamespace": 6, # File namespace
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": 800,
        "format": "json",
    }
    headers = {"User-Agent": "KalvettuHeritageArchive/1.0 (epigraphy-heritage-research)"}

    results = []
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page in pages.items():
                    info_list = page.get("imageinfo", [])
                    if not info_list:
                        continue
                    info = info_list[0]
                    metadata = info.get("extmetadata", {})
                    
                    artist = metadata.get("Artist", {}).get("value", "")
                    # strip html tags from artist if any
                    import re
                    clean_artist = re.sub('<[^<]+?>', '', artist).strip() or "Wikimedia Commons contributor"
                    
                    license_name = metadata.get("LicenseShortName", {}).get("value", "CC BY-SA")
                    license_url = metadata.get("LicenseUrl", {}).get("value", "")
                    desc = metadata.get("ImageDescription", {}).get("value", "")
                    clean_desc = re.sub('<[^<]+?>', '', desc).strip() or page.get("title", "")
                    
                    image_url = info.get("url")
                    thumb_url = info.get("thumburl") or image_url
                    
                    if image_url and (image_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))):
                        results.append({
                            "title": page.get("title"),
                            "image_url": image_url,
                            "thumb_url": thumb_url,
                            "width": info.get("width"),
                            "height": info.get("height"),
                            "author": clean_artist[:100],
                            "license": license_name[:50],
                            "license_url": license_url,
                            "commons_url": info.get("descriptionurl"),
                            "caption": clean_desc[:200]
                        })
    except Exception as e:
        print(f"Wikimedia fetch notice: {e}")

    # Fallback to Wikipedia Page Image if Wikimedia Commons has few/no results
    if len(results) < limit:
        wiki_url = "https://en.wikipedia.org/w/api.php"
        wiki_params = {
            "action": "query",
            "prop": "pageimages|pageterms",
            "titles": f"{temple_name} temple",
            "format": "json",
            "pithumbsize": 800
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(wiki_url, params=wiki_params, headers=headers)
                if resp.status_code == 200:
                    pages = resp.json().get("query", {}).get("pages", {})
                    for page_id, page in pages.items():
                        if page_id == "-1": continue
                        thumb = page.get("thumbnail", {})
                        img_url = thumb.get("source")
                        if img_url:
                            desc = page.get("terms", {}).get("description", [page.get("title")])[0]
                            results.append({
                                "title": page.get("title"),
                                "image_url": img_url,
                                "thumb_url": img_url,
                                "width": thumb.get("width"),
                                "height": thumb.get("height"),
                                "author": "Wikipedia",
                                "license": "CC BY-SA",
                                "license_url": "",
                                "commons_url": f"https://en.wikipedia.org/wiki/?curid={page_id}",
                                "caption": desc
                            })
        except Exception as e:
            print(f"Wikipedia fetch notice: {e}")

    _set_cache(cache_key, results)
    return results

# 2. Wikidata Integration Service
async def lookup_wikidata_temple(query: str) -> Optional[Dict[str, Any]]:
    cache_key = f"wikidata:{query}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "limit": 3,
        "format": "json"
    }
    headers = {"User-Agent": "KalvettuHeritageArchive/1.0 (epigraphy-heritage-research)"}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                search_res = data.get("search", [])
                for item in search_res:
                    desc = item.get("description", "").lower()
                    if "temple" in desc or "hindu" in desc or "monument" in desc:
                        result = {
                            "qid": item.get("id"),
                            "label": item.get("label"),
                            "description": item.get("description"),
                            "url": f"https://www.wikidata.org/wiki/{item.get('id')}"
                        }
                        _set_cache(cache_key, result)
                        return result
    except Exception as e:
        print(f"Wikidata lookup notice: {e}")

    _set_cache(cache_key, None)
    return None
