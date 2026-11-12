import io
import math
import wave
import struct
import httpx
import logging
from typing import List
from backend.app.adapters.voice.base import BaseVoiceProvider, SpeechRequest, SpeechResponse, WordTimestamp
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_INDIC_LANGS = {
    "or": "Odia",
    "hi": "Hindi",
    "bn": "Bengali",
    "as": "Assamese",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "pa": "Punjabi",
    "ta": "Tamil",
    "te": "Telugu",
    "en": "English",
}

class Maya3TTSAdapter(BaseVoiceProvider):
    """
    Adapter for Maya2 Native (pip package `maya3`).
    Supports 12 Indian languages natively with 24kHz audio synthesis.
    """

    def __init__(self, api_base: str = None, fallback_enabled: bool = True):
        self.api_base = api_base or settings.MAYA3_API_BASE
        self.fallback_enabled = fallback_enabled

    def supports_language(self, language_code: str) -> bool:
        return language_code.lower() in SUPPORTED_INDIC_LANGS

    async def synthesize(self, request: SpeechRequest) -> SpeechResponse:
        lang = request.language_code.lower()
        if not self.supports_language(lang):
            raise ValueError(f"Language '{lang}' is not supported by Maya3. Supported: {list(SUPPORTED_INDIC_LANGS.keys())}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "input": request.text,
                    "model": "maya-research/maya2-native",
                    "voice": request.voice_id,
                    "language": lang,
                    "speed": request.speed,
                }
                if request.reference_audio_url:
                    payload["reference_audio"] = request.reference_audio_url

                response = await client.post(f"{self.api_base}/audio/speech", json=payload)
                if response.status_code == 200:
                    audio_bytes = response.content
                    duration = self._calculate_wav_duration(audio_bytes)
                    words = self._estimate_word_timestamps(request.text, duration)
                    return SpeechResponse(
                        audio_bytes=audio_bytes,
                        format="wav",
                        sample_rate=24000,
                        duration_seconds=duration,
                        word_timestamps=words
                    )
                else:
                    logger.warning(f"Maya3 API returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Maya3 API connection failed ({e}). Checking fallback mode...")

        if self.fallback_enabled:
            return self._generate_simulated_audio(request)
        raise RuntimeError(f"Maya3 TTS service at {self.api_base} is unavailable.")

    def _estimate_word_timestamps(self, text: str, total_duration: float) -> List[WordTimestamp]:
        words = [w.strip() for w in text.split() if w.strip()]
        if not words:
            return []
        word_dur = total_duration / len(words)
        result = []
        for i, word in enumerate(words):
            result.append(WordTimestamp(
                word=word,
                start_seconds=round(i * word_dur, 2),
                end_seconds=round((i + 1) * word_dur, 2)
            ))
        return result

    def _calculate_wav_duration(self, wav_bytes: bytes) -> float:
        try:
            with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / float(rate)
        except Exception:
            return 3.0

    def _generate_simulated_audio(self, request: SpeechRequest) -> SpeechResponse:
        """
        Generates standard 24kHz mono PCM WAV tones with speech-like harmonic modulation
        for seamless local development and tests without requiring an active 12GB GPU.
        """
        words = [w.strip() for w in request.text.split() if w.strip()]
        num_words = max(len(words), 1)
        # Average reading speed: ~0.45s per word in Indic languages
        duration = max(num_words * 0.45 / request.speed, 1.2)
        sample_rate = 24000
        total_samples = int(sample_rate * duration)

        pitch_freq = 150.0 * request.pitch  # Base fundamental frequency
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1) # mono
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(sample_rate)
            
            raw_data = bytearray()
            for s in range(total_samples):
                t = s / sample_rate
                # Harmonic speech envelope modulation
                env = 0.5 * (1.0 + math.sin(2 * math.pi * 3.5 * t))
                val = int(14000 * env * (0.6 * math.sin(2 * math.pi * pitch_freq * t) + 
                                         0.4 * math.sin(2 * math.pi * pitch_freq * 2 * t)))
                val = max(-32767, min(32767, val))
                raw_data.extend(struct.pack('<h', val))
            wf.writeframes(raw_data)

        audio_bytes = buf.getvalue()
        word_timestamps = self._estimate_word_timestamps(request.text, duration)

        return SpeechResponse(
            audio_bytes=audio_bytes,
            format="wav",
            sample_rate=sample_rate,
            duration_seconds=round(duration, 2),
            word_timestamps=word_timestamps
        )
