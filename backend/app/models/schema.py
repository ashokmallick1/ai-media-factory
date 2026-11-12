import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Brand(Base):
    __tablename__ = "brands"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    primary_language = Column(String(10), default="or")
    target_audience = Column(String(200), nullable=True)
    visual_guidelines = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="brand", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="brand", cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50), default="lead")
    bio = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    visual_specs = Column(JSON, default=dict) # e.g. color palette, head shape, clothing
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("Brand", back_populates="characters")
    voice_profiles = relationship("VoiceProfile", back_populates="character", cascade="all, delete-orphan")

class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    character_id = Column(String(36), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False) # 'or', 'hi', 'bn', 'en'
    provider = Column(String(50), default="maya3")     # 'maya3', 'elevenlabs', 'mock'
    voice_id = Column(String(100), nullable=False)
    reference_sample_url = Column(String(500), nullable=True)
    pitch_modifier = Column(Float, default=1.0)
    speed_modifier = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    character = relationship("Character", back_populates="voice_profiles")

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    studio_type = Column(String(50), nullable=False) # 'entertainment', 'kids', 'education', 'podcast', 'news', 'marketing'
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("Brand", back_populates="projects")
    episodes = relationship("Episode", back_populates="project", cascade="all, delete-orphan")

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    episode_number = Column(Integer, default=1)
    title = Column(String(200), nullable=False)
    brief = Column(Text, nullable=True)
    master_language = Column(String(10), default="or")
    status = Column(String(50), default="draft") # 'draft', 'scripted', 'voice_ready', 'rendered', 'qa_approved'
    budget_limit_usd = Column(Float, default=2.0)
    actual_cost_usd = Column(Float, default=0.0)
    final_video_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="episodes")
    scenes = relationship("Scene", back_populates="episode", cascade="all, delete-orphan", order_by="Scene.scene_index")
    jobs = relationship("ProductionJob", back_populates="episode", cascade="all, delete-orphan")
    cost_records = relationship("CostRecord", back_populates="episode", cascade="all, delete-orphan")

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    episode_id = Column(String(36), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False)
    scene_index = Column(Integer, nullable=False)
    heading = Column(String(200), nullable=True)
    action_description = Column(Text, nullable=True)
    duration_seconds = Column(Float, default=5.0)
    renderer_type = Column(String(50), default="hyperframes") # 'hyperframes', 'remotion', 'ffmpeg'
    visual_spec = Column(JSON, default=dict)
    rendered_video_url = Column(String(500), nullable=True)
    status = Column(String(50), default="pending") # 'pending', 'rendering', 'rendered', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)

    episode = relationship("Episode", back_populates="scenes")
    dialogues = relationship("DialogueLine", back_populates="scene", cascade="all, delete-orphan", order_by="DialogueLine.line_index")

class DialogueLine(Base):
    __tablename__ = "dialogue_lines"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False)
    character_id = Column(String(36), ForeignKey("characters.id", ondelete="SET NULL"), nullable=True)
    line_index = Column(Integer, nullable=False)
    language_code = Column(String(10), default="or")
    dialogue_text = Column(Text, nullable=False)
    audio_asset_url = Column(String(500), nullable=True)
    word_timestamps = Column(JSON, default=list)
    duration_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    scene = relationship("Scene", back_populates="dialogues")

class ProductionJob(Base):
    __tablename__ = "production_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    episode_id = Column(String(36), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False)
    job_type = Column(String(50), nullable=False) # 'script_gen', 'tts_batch', 'scene_render', 'assembly', 'qa'
    status = Column(String(50), default="queued") # 'queued', 'running', 'completed', 'failed'
    progress_percent = Column(Float, default=0.0)
    cost_usd = Column(Float, default=0.0)
    logs = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    episode = relationship("Episode", back_populates="jobs")

class CostRecord(Base):
    __tablename__ = "cost_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    episode_id = Column(String(36), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False)
    service_type = Column(String(50), nullable=False) # 'openrouter_llm', 'maya3_gpu', 'rendering_cpu_gpu', 'storage_r2'
    units_consumed = Column(Float, nullable=False)
    unit_type = Column(String(50), nullable=False)     # 'tokens', 'gpu_seconds', 'audio_seconds'
    cost_usd = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    episode = relationship("Episode", back_populates="cost_records")
