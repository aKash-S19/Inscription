import json
from typing import Dict, Any
from config import settings
from .base_provider import BaseAIProvider
from google import genai
from google.genai import types

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self._client = None

    @property
    def name(self) -> str:
        return "Google Gemini (3.6-flash)"

    @property
    def is_available(self) -> bool:
        return bool(settings.KALVETTU_AI_GEMINI_KEY)

    def _get_client(self):
        if self._client is None and settings.KALVETTU_AI_GEMINI_KEY:
            self._client = genai.Client(api_key=settings.KALVETTU_AI_GEMINI_KEY)
        return self._client

    async def chat(self, prompt: str, system_instruction: str, timeout: float = 15.0) -> str:
        client = self._get_client()
        full_prompt = f"{system_instruction}\n\nUSER QUESTION / QUERY:\n{prompt}"
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=full_prompt
        )
        return response.text

    async def translate(self, text: str, target_language: str, timeout: float = 15.0) -> Dict[str, Any]:
        client = self._get_client()
        prompt = f"""
You are an expert epigraphist translating Tamil and Sanskrit (Grantha) temple inscriptions into {target_language}.
Never invent missing text. If text is unclear or damaged, note it accurately.

INSCRIPTION TEXT:
{text}

Return strictly a JSON object with:
"detected_language": "...",
"detected_script": "...",
"translation": "...",
"explanation": "...",
"important_terms": ["..."],
"historical_context": "..."
"""
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        try:
            return json.loads(response.text)
        except Exception:
            return {
                "detected_language": "Tamil",
                "detected_script": "Tamil",
                "translation": response.text,
                "explanation": "Extracted translation",
                "important_terms": [],
                "historical_context": ""
            }

    async def vision_extract(self, image_bytes: bytes, mime_type: str, prompt: str, timeout: float = 20.0) -> Dict[str, Any]:
        client = self._get_client()
        extract_prompt = f"""
You are an epigraphic OCR and inscription specialist. Analyze this photograph of a stone inscription (kalvettu).
{prompt}

IMPORTANT ARCHAEOLOGICAL RULES:
1. AI transcription is a DRAFT and must NEVER be presented as authoritative fact without human epigraphist verification.
2. If the stone surface is eroded, illegible, or blurry, state: "Unable to reliably read this inscription image."
3. Return strictly a JSON object with these fields:
"title": "Descriptive title of inscription or draft topic",
"language": "Detected language (e.g. Tamil / Sanskrit)",
"script": "Detected script (e.g. Tamil / Grantha / Vatteluttu)",
"original_text": "Draft transcription of visible characters (empty if illegible)",
"translation": "Draft English translation",
"simple_explanation": "Plain language summary of content",
"historical_significance": "Historical context or probable dynasty/period",
"ruler": "Named king or patron if visible, else 'Not visible'",
"confidence": "High / Medium / Low / Illegible",
"notes": "Epigraphic notes on script condition and erosion"
"""
        contents = [
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            extract_prompt
        ]
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        try:
            return json.loads(response.text)
        except Exception as e:
            return {
                "title": "Draft Inscription Extraction",
                "language": "Tamil",
                "script": "Tamil",
                "original_text": "",
                "translation": "Unable to reliably parse response JSON.",
                "simple_explanation": str(e),
                "historical_significance": "",
                "ruler": "Not visible",
                "confidence": "Low",
                "notes": "Error during automated parsing."
            }
