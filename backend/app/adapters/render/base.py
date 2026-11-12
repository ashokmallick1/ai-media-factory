from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SceneRenderSpec(BaseModel):
    scene_id: str
    duration_seconds: float
    resolution: tuple[int, int] = (1920, 1080)
    fps: int = 30
    title: str = ""
    background_color: str = "#1A1A24"
    audio_path: Optional[str] = None
    character_names: List[str] = Field(default_factory=list)
    dialogue_text: str = ""
    visual_elements: List[Dict[str, Any]] = Field(default_factory=list)

class RenderOutput(BaseModel):
    scene_id: str
    output_path: str
    duration_seconds: float
    file_size_bytes: int
    resolution: tuple[int, int]
    render_time_seconds: float

class BaseRenderEngine(ABC):
    @abstractmethod
    async def render_scene(self, spec: SceneRenderSpec, output_dir: str) -> RenderOutput:
        """Render a single scene to an MP4 video file."""
        pass
