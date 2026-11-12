from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SceneData(BaseModel):
    scene_index: int
    heading: str
    action: str
    character_name: str
    dialogue_text: str
    duration_seconds: float = 4.0
    audio_path: Optional[str] = None
    rendered_video_path: Optional[str] = None

class ProductionState(BaseModel):
    episode_id: str
    studio_type: str = "entertainment" # 'entertainment', 'kids', etc.
    title: str = ""
    topic: str = ""
    target_language: str = "or"
    budget_limit_usd: float = 2.0
    status: str = "initialized"
    
    # Pipeline stages
    script_content: str = ""
    scenes: List[SceneData] = Field(default_factory=list)
    master_video_path: Optional[str] = None
    social_video_path: Optional[str] = None
    
    # QA & Costs
    qa_passed: bool = False
    qa_report: Dict[str, Any] = Field(default_factory=dict)
    cost_summary: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
