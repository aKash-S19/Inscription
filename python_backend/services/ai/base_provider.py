from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class BaseAIProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier"""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider API key is configured"""
        pass

    @abstractmethod
    async def chat(self, prompt: str, system_instruction: str, timeout: float = 12.0) -> str:
        """Generate text completion from grounded prompt"""
        pass

    @abstractmethod
    async def translate(self, text: str, target_language: str, timeout: float = 12.0) -> Dict[str, Any]:
        """Translate and explain an inscription"""
        pass

    async def vision_extract(self, image_bytes: bytes, mime_type: str, prompt: str, timeout: float = 20.0) -> Dict[str, Any]:
        """Multimodal OCR extraction (supported by vision-capable models)"""
        raise NotImplementedError(f"{self.name} does not support vision OCR.")
