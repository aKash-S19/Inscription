import httpx
import json
from typing import Dict, Any
from config import settings
from .base_provider import BaseAIProvider

class CerebrasProvider(BaseAIProvider):
    @property
    def name(self) -> str:
        return "Cerebras (Qwen-3.8-27b / Gemma-4-31b)"

    @property
    def is_available(self) -> bool:
        return bool(settings.CEREBRAS_API_KEY)

    async def chat(self, prompt: str, system_instruction: str, timeout: float = 12.0) -> str:
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.CEREBRAS_API_KEY}",
            "Content-Type": "application/json",
        }
        models_to_try = ["qwen-3.8-27b", "gemma-4-31b", "gpt-oss-120b"]
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
        raise RuntimeError(f"Cerebras failed: {last_err}")

    async def translate(self, text: str, target_language: str, timeout: float = 12.0) -> Dict[str, Any]:
        system_instruction = (
            f"You are an expert epigraphist translating Tamil and Sanskrit (Grantha) temple inscriptions into {target_language}. "
            "Never invent missing text. Return strict JSON with fields: 'detected_language', 'detected_script', 'translation', 'explanation', 'important_terms', 'historical_context'."
        )
        prompt = f"Inscription Text:\n{text}\n\nReturn JSON only."
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.CEREBRAS_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "qwen-3.8-27b",
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
