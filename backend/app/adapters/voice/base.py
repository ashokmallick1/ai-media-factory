from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, AsyncGenerator
from pydantic import BaseModel, Field

class WordTimestamp(BaseModel):
    word: str
    start_seconds: float
    end_seconds: float

class SpeechRequest(BaseModel):
    text: str
    language_code: str = "or"  # 'or', 'hi', 'bn', 'en', 'te', 'ta', etc.
    voice_id: str = "Ahana"
    reference_audio_url: Optional[str] = None
    pitch: float = 1.0
    speed: float = 1.0

class SpeechResponse(BaseModel):
    audio_bytes: bytes
    format: str = "wav"
    sample_rate: int = 24000
    duration_seconds: float
    word_timestamps: List[WordTimestamp] = Field(default_factory=list)

class BaseVoiceProvider(ABC):
    @abstractmethod
    async def synthesize(self, request: SpeechRequest) -> SpeechResponse:
        """Synthesize speech and return audio bytes with duration and alignment."""
        pass

    @abstractmethod
    def supports_language(self, language_code: str) -> bool:
        """Check if provider supports the given language code."""
        pass
