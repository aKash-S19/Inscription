import logging
from typing import List, Dict, Any, Optional
from .base_provider import BaseAIProvider
from .groq_provider import GroqProvider
from .cerebras_provider import CerebrasProvider
from .openrouter_provider import OpenRouterProvider
from .gemini_provider import GeminiProvider

logger = logging.getLogger("kalvettu.ai")

SYSTEM_GROUNDING_INSTRUCTION = """
You are an expert AI assistant for the KALVETTU digital heritage archive (Tamil Temple Inscriptions).

CRITICAL EPIGRAPHIC RULES:
1. Ground your answer ONLY in the VERIFIED ARCHIVE CONTEXT provided below.
2. Do NOT invent or hallucinate inscriptions, titles, rulers, dynasties, consecration dates, archaeological references (like SII or ARE numbers), translations, or historical events.
3. If the provided verified context does not contain enough information to answer the question, explicitly state:
   "The available verified records in the Kalvettu archive do not contain enough information to answer this."
4. Clearly distinguish between:
   - verified archaeological records and cited sources
   - plain-language AI explanation
   - unavailable information
5. Always cite the primary epigraphic publication (e.g. South Indian Inscriptions, ARE, Epigraphia Indica) when quoting a record.
"""

class AIRouter:
    def __init__(self):
        # Configure ordered providers
        self.providers: List[BaseAIProvider] = [
            GroqProvider(),
            CerebrasProvider(),
            OpenRouterProvider(),
            GeminiProvider()
        ]

    def get_available_providers(self) -> List[BaseAIProvider]:
        return [p for p in self.providers if p.is_available]

    async def chat_with_fallback(self, prompt: str, context: str, language: str = "English") -> Dict[str, Any]:
        """Execute chat query down the fallback chain"""
        system_inst = f"{SYSTEM_GROUNDING_INSTRUCTION}\nLanguage to answer in: {language}\n\n[VERIFIED ARCHIVE CONTEXT]:\n{context}"
        
        available = self.get_available_providers()
        if not available:
            return {
                "answer": "No AI API keys are configured. Based on database search:\n" + context[:500],
                "provider": "local_database_fallback"
            }

        last_error = None
        for provider in available:
            try:
                logger.info(f"Attempting query with provider: {provider.name}")
                ans = await provider.chat(prompt=prompt, system_instruction=system_inst, timeout=12.0)
                if ans and ans.strip():
                    return {
                        "answer": ans.strip(),
                        "provider": provider.name
                    }
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}. Moving to next fallback provider.")
                last_error = e
                continue

        # If all providers fail: return safe grounded database response
        fallback_msg = (
            "All external AI providers are currently unreachable. "
            "Here is the verified information retrieved directly from the Kalvettu database:\n\n"
        )
        if context.strip():
            fallback_msg += context
        else:
            fallback_msg += "No matching verified records were found in the database."

        return {
            "answer": fallback_msg,
            "provider": f"local_database_fallback (All providers failed: {last_error})"
        }

    async def translate_with_fallback(self, text: str, target_language: str = "English") -> Dict[str, Any]:
        """Execute translation query down the fallback chain"""
        available = self.get_available_providers()
        
        for provider in available:
            try:
                res = await provider.translate(text=text, target_language=target_language, timeout=12.0)
                if res and isinstance(res, dict) and "translation" in res:
                    res["provider_used"] = provider.name
                    return res
            except Exception as e:
                logger.warning(f"Translation provider {provider.name} failed: {e}. Falling back.")
                continue

        return {
            "detected_language": "Tamil / Grantha",
            "detected_script": "Tamil",
            "translation": "Translation service is currently unavailable.",
            "explanation": "Unable to contact translation providers. Please refer to cited published volumes.",
            "target_language": target_language,
            "important_terms": [],
            "provider_used": "offline_fallback"
        }

    async def vision_extract(self, image_bytes: bytes, mime_type: str, prompt: str) -> Dict[str, Any]:
        """Vision OCR extraction (using Gemini or fallback)"""
        gemini = next((p for p in self.providers if isinstance(p, GeminiProvider) and p.is_available), None)
        if not gemini:
            return {
                "title": "Manual Review Required",
                "language": "Tamil",
                "script": "Tamil",
                "original_text": "",
                "translation": "Vision model is not configured. Please enter transcription manually.",
                "simple_explanation": "Gemini API key is required for image OCR extraction.",
                "historical_significance": "",
                "ruler": "Unknown",
                "confidence": "None",
                "notes": "No vision provider configured."
            }

        try:
            res = await gemini.vision_extract(image_bytes=image_bytes, mime_type=mime_type, prompt=prompt)
            res["provider_used"] = gemini.name
            return res
        except Exception as e:
            return {
                "title": "OCR Extraction Failed",
                "language": "Tamil",
                "script": "Tamil",
                "original_text": "",
                "translation": "Unable to reliably read this inscription image.",
                "simple_explanation": f"Vision analysis error: {e}",
                "historical_significance": "",
                "ruler": "Not visible",
                "confidence": "Low",
                "notes": "Image could not be processed."
            }

router = AIRouter()
