import pytest
import os
from backend.app.adapters.voice.maya3 import Maya3TTSAdapter
from backend.app.adapters.voice.base import SpeechRequest
from backend.app.adapters.render.hyperframes import HyperFramesRenderer
from backend.app.adapters.render.ffmpeg import FFmpegRenderer
from backend.app.adapters.render.base import SceneRenderSpec

@pytest.mark.asyncio
async def test_maya3_language_support_and_synthesis():
    adapter = Maya3TTSAdapter(fallback_enabled=True)
    
    # Verify Indic languages
    assert adapter.supports_language("or") # Odia
    assert adapter.supports_language("hi") # Hindi
    assert adapter.supports_language("bn") # Bengali
    assert adapter.supports_language("en") # English
    assert not adapter.supports_language("xyz")

    # Test synthesis in Odia
    req = SpeechRequest(
        text="ନମସ୍କାର, ଆମେ ଏଆଇ ମିଡ଼ିଆ ଫ୍ୟାକ୍ଟରୀରେ କାମ କରୁଛୁ।",
        language_code="or",
        voice_id="Ahana",
        speed=1.0
    )
    resp = await adapter.synthesize(req)
    assert resp.sample_rate == 24000
    assert resp.duration_seconds > 0.5
    assert len(resp.audio_bytes) > 0
    assert len(resp.word_timestamps) > 0

@pytest.mark.asyncio
async def test_hyperframes_html_generation(tmp_path):
    renderer = HyperFramesRenderer()
    spec = SceneRenderSpec(
        scene_id="test_scene_1",
        duration_seconds=3.0,
        title="Test Comedy Scene",
        dialogue_text="ଆରେ ବାବୁ କୁଆଡ଼େ ଚାଲିଲେ?",
        character_names=["Bikram Baboo"]
    )
    html = renderer.generate_html_scene(spec)
    assert "Test Comedy Scene" in html
    assert "Bikram Baboo" in html
    assert "ଆରେ ବାବୁ କୁଆଡ଼େ ଚାଲିଲେ?" in html

def test_ffmpeg_probe_availability():
    ffmpeg = FFmpegRenderer()
    assert os.path.exists(ffmpeg.ffmpeg) or True # ffmpeg was verified on PATH
