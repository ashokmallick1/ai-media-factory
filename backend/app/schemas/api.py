from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class BrandCreate(BaseModel):
    name: str
    slug: str
    primary_language: str = "or"
    target_audience: Optional[str] = None
    visual_guidelines: Dict[str, Any] = Field(default_factory=dict)

class CharacterCreate(BaseModel):
    brand_id: str
    name: str
    role: str = "lead"
    bio: Optional[str] = None
    personality: Optional[str] = None
    visual_specs: Dict[str, Any] = Field(default_factory=dict)

class EpisodeCreateRequest(BaseModel):
    brand_id: str
    studio_type: str = "entertainment" # 'entertainment', 'kids', 'education', 'podcast', 'news', 'marketing'
    title: str
    brief: Optional[str] = None
    target_language: str = "or"
    budget_limit_usd: float = 2.0

class ProductionRunResponse(BaseModel):
    episode_id: str
    status: str
    title: str
    studio_type: str
    language: str
    master_video_path: Optional[str] = None
    social_video_path: Optional[str] = None
    duration_seconds: float
    total_cost_usd: float
    qa_passed: bool
    qa_report: Dict[str, Any]
    cost_summary: Dict[str, Any]
    logs: List[str]
