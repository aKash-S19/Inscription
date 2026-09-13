import sys
import json
import urllib.request
import urllib.parse
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:5173"

def log(msg):
    print(msg, flush=True)

def test_request(name, path, method="GET", body=None, headers=None, timeout=30):
    url = f"{BASE_URL}{path}"
    headers = headers or {}
    data = None
    if body:
        data = json.dumps(body).encode('utf-8')
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if "application/json" in content_type:
                res = json.loads(raw.decode('utf-8'))
            else:
                res = raw.decode('utf-8')
            log(f"[PASS] {name} (Status: {resp.status})")
            return res
    except urllib.error.HTTPError as e:
        log(f"[FAIL] {name} (HTTP {e.code}): {e.read().decode('utf-8', errors='ignore')}")
        return None
    except Exception as e:
        log(f"[FAIL] {name}: {e}")
        return None

log("==================================================")
log("KALVETTU E2E SYSTEM INTEGRATION TEST VIA VITE PROXY")
log("==================================================")

# 1. HTML Frontend Shell
html = test_request("Vite Shell Index HTML", "/")
if html and "KALVETTU" in html:
    log("  -> Confirmed HTML contains KALVETTU branding & title")

# 2. Temples Proxy
temples = test_request("Fetch All Temples", "/api/temples")
if temples:
    log(f"  -> Returned {len(temples)} verified temples")

# 3. English Search
thanjavur = test_request("Search Temple in English ('Thanjavur')", "/api/temples?q=Thanjavur")
if thanjavur and len(thanjavur) > 0:
    log(f"  -> Found: {thanjavur[0]['nameEn']}")

# 4. Tamil Search
tamil_query = urllib.parse.quote("தஞ்சாவூர்")
tamil_res = test_request("Search Temple in Tamil ('தஞ்சாவூர்')", f"/api/temples?q={tamil_query}")
if tamil_res and len(tamil_res) > 0:
    log(f"  -> Found via Tamil script: {tamil_res[0]['nameEn']} ({tamil_res[0]['nameTa']})")

# 5. Empty/Unknown Search
empty_res = test_request("Search Unknown Temple ('Atlantis')", "/api/temples?q=Atlantis")
if empty_res == []:
    log("  -> Returned empty array (triggers 'No verified temple record found' UI state)")

# 6. Search Inscription by Title
silver = test_request("Search Inscription by Title ('silver vessels')", "/api/inscriptions?q=silver%20vessels")
if silver and len(silver) > 0:
    log(f"  -> Found Inscription: '{silver[0]['title']}' ({silver[0]['slug']})")

# 7. Inscription Detail
ins_slug = silver[0]['slug'] if silver else "brihadisvara-rajaraja-silver-vessels"
ins_detail = test_request(f"Fetch Inscription Detail ('{ins_slug}')", f"/api/inscriptions/{ins_slug}")
if ins_detail:
    log(f"  -> Verified Status: {ins_detail.get('verificationStatus')}")
    log(f"  -> Source Citation: {ins_detail.get('sourceCitation')}")
    log(f"  -> SII Reference: {ins_detail.get('siiReference')}")

# 8. Locations for Interactive Map
locs = test_request("Fetch Temple Schematic Locations", "/api/locations/brihadisvara-thanjavur")
if locs:
    log(f"  -> Found {len(locs)} in-temple schematic markers")

# 9. Timeline Events
timeline = test_request("Fetch Historical Timeline", "/api/timeline")
if timeline:
    log(f"  -> Found {len(timeline)} chronological events")

# 10. Ask the Archive (AI RAG)
rag_body = {
    "messages": [{"role": "user", "content": "What did Kundavai donate to the Thanjavur temple?"}],
    "language": "English"
}
rag_res = test_request("Ask the Archive RAG Endpoint", "/api/ai/ask", method="POST", body=rag_body, timeout=30)
if rag_res:
    log(f"  -> Provider Used: {rag_res.get('provider_used')}")
    log(f"  -> Sources Cited: {len(rag_res.get('sources', []))} authoritative sources")
    log(f"  -> Answer snippet: {rag_res.get('answer')[:120]}...")

# 11. Translate Kalvettu
trans_body = {
    "text": "ஸ்வஸ்திஸ்ரீ கோப்பரகேசரிவன்மரான உடையார் ஸ்ரீராஜராஜதேவர்க்கு",
    "target_language": "English"
}
trans_res = test_request("Translate Inscription Endpoint", "/api/ai/translate", method="POST", body=trans_body, timeout=30)
if trans_res:
    log(f"  -> Detected Script: {trans_res.get('detected_script')}")
    log(f"  -> Translation: {trans_res.get('translation')}")

# 12. Ingest AI Draft (Zero-Trust)
ingest_body = {
    "temple_name": "Brihadisvara Temple",
    "text": "ஸ்வஸ்திஸ்ரீ திருபுவனச் சக்கரவர்த்திகள் கோனேரின்மைகொண்டான்",
    "notes": "Field survey notes on south wall"
}
ingest_res = test_request("Add Kalvettu Draft Ingestion", "/api/ai/ingest", method="POST", body=ingest_body, timeout=30)
if ingest_res:
    log(f"  -> Title: {ingest_res.get('title')}")
    log(f"  -> Verification Status: {ingest_res.get('verification_status')} (Verified = False)")
    log(f"  -> Status Message: {ingest_res.get('status_message')}")

log("==================================================")
log("ALL 12 END-TO-END INTEGRATION TESTS COMPLETE!")
log("==================================================")
