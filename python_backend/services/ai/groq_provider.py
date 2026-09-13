import httpx
import json
from typing import Dict, Any
from config import settings
from .base_provider import BaseAIProvider

class GroqProvider(BaseAIProvider):
    @property
    def name(self) -> str:
        return "Groq (Qwen-3.6-27b)"

    @property
    def is_available(self) -> bool:
        return bool(settings.GROQ_API_KEY)

    async def chat(self, prompt: str, system_instruction: str, timeout: float = 12.0) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        
        models_to_try = ["qwen/qwen3.6-27b", "openai/gpt-oss-120b", "groq/compound"]
        last_err = None
        for model in models_to_try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1024,
            }
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                    last_err = f"Status {resp.status_code}: {resp.text}"
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"Groq failed: {last_err}")

    async def translate(self, text: str, target_language: str, timeout: float = 12.0) -> Dict[str, Any]:
        system_instruction = (
            f"You are an expert epigraphist translating Tamil and Sanskrit (Grantha) temple inscriptions into {target_language}. "
            "Never invent missing text. Return strict JSON with fields: 'detected_language', 'detected_script', 'translation', 'explanation', 'important_terms', 'historical_context'."
        )
        prompt = f"Inscription Text:\n{text}\n\nReturn JSON only."
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "qwen/qwen3.6-27b",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            return json.loads(raw_text)
