import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.core.database import get_db, engine, Base
from backend.app.models.schema import Brand, Character, VoiceProfile, Project, Episode, ProductionJob
from backend.app.schemas.api import BrandCreate, CharacterCreate, EpisodeCreateRequest, ProductionRunResponse
from backend.app.orchestration.graph import ProductionOrchestrator
from backend.app.orchestration.state import ProductionState

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

api_router = APIRouter()
orchestrator = ProductionOrchestrator()

@api_router.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Media Factory API", "version": "1.0.0"}

@api_router.get("/studios")
def list_studios():
    return [
        {
            "id": "entertainment",
            "name": "Entertainment Studio",
            "description": "Odia regional & village comedy, animated sitcoms, episodic sketches.",
            "render_engine": "HyperFrames + GSAP",
            "primary_language": "or",
            "status": "active"
        },
        {
            "id": "kids",
            "name": "Kids & Children's Content",
            "description": "Nursery rhymes, alphabet/numbers, moral stories, child safety gates.",
            "render_engine": "HyperFrames + Motion Pack",
            "primary_language": "or",
            "status": "active"
        },
        {
            "id": "education",
            "name": "Education & Tutorials",
            "description": "Tech tutorials, AI explainers, animated presentations, quizzes.",
            "render_engine": "Remotion",
            "primary_language": "en",
            "status": "ready"
        },
        {
            "id": "podcast",
            "name": "AI Podcast Studio",
            "description": "Multi-speaker virtual hosts, audio mixing, waveform audiograms.",
            "render_engine": "FFmpeg + Remotion",
            "primary_language": "en",
            "status": "ready"
        },
        {
            "id": "news",
            "name": "News & Documentaries",
            "description": "Fact-checking research, verified citations, ticker tapes.",
            "render_engine": "Remotion + FFmpeg",
            "primary_language": "hi",
            "status": "ready"
        },
        {
            "id": "marketing",
            "name": "Marketing & Ads",
            "description": "Product ads, promotional reels, kinetic typography.",
            "render_engine": "HyperFrames / Remotion",
            "primary_language": "en",
            "status": "ready"
        }
    ]

@api_router.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    brands = db.query(Brand).all()
    if not brands:
        # Seed default regional brand
        default_brand = Brand(
            id=str(uuid.uuid4()),
            name="Mo Gaon Comedy (Odia Entertainment)",
            slug="mo-gaon-comedy",
            primary_language="or",
            target_audience="Regional Odisha family & youth audience",
            visual_guidelines={"color_primary": "#fca311", "style": "2D cartoon comedy"}
        )
        db.add(default_brand)
        db.commit()
        db.refresh(default_brand)
        brands = [default_brand]
    return brands

@api_router.post("/brands")
def create_brand(payload: BrandCreate, db: Session = Depends(get_db)):
    brand = Brand(**payload.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@api_router.get("/characters")
def get_characters(brand_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Character)
    if brand_id:
        query = query.filter(Character.brand_id == brand_id)
    chars = query.all()
    if not chars:
        # Seed recurring characters
        brands = db.query(Brand).all()
        target_brand_id = brands[0].id if brands else str(uuid.uuid4())
        c1 = Character(
            id=str(uuid.uuid4()),
            brand_id=target_brand_id,
            name="Bikram Baboo",
            role="lead",
            bio="The pompous, talkative village head who acts grand but gets easily outwitted.",
            personality="Humorous, arrogant yet lovable, dramatic gestures."
        )
        c2 = Character(
            id=str(uuid.uuid4()),
            brand_id=target_brand_id,
            name="Tukuna",
            role="sidekick",
            bio="The sharp-witted village youth who loves puncturing Baboo's ego.",
            personality="Sarcastic, relaxed, quick-tongued."
        )
        c3 = Character(
            id=str(uuid.uuid4()),
            brand_id=target_brand_id,
            name="Gulu Owl",
            role="kids_host",
            bio="The friendly wise owl who teaches preschool rhymes and numbers.",
            personality="Gentle, encouraging, musical."
        )
        db.add_all([c1, c2, c3])
        db.commit()
        chars = [c1, c2, c3]
    return chars

@api_router.post("/production/run", response_model=ProductionRunResponse)
async def run_production(payload: EpisodeCreateRequest, db: Session = Depends(get_db)):
    """
    Triggers an autonomous production pipeline run.
    """
    episode_id = f"ep_{uuid.uuid4().hex[:8]}"

    init_state = ProductionState(
        episode_id=episode_id,
        studio_type=payload.studio_type,
        title=payload.title,
        topic=payload.brief or payload.title,
        target_language=payload.target_language,
        budget_limit_usd=payload.budget_limit_usd
    )

    # Execute orchestrator pipeline
    final_state = await orchestrator.run_pipeline(init_state)

    total_dur = sum(s.duration_seconds for s in final_state.scenes)

    return ProductionRunResponse(
        episode_id=final_state.episode_id,
        status=final_state.status,
        title=final_state.title,
        studio_type=final_state.studio_type,
        language=final_state.target_language,
        master_video_path=final_state.master_video_path,
        social_video_path=final_state.social_video_path,
        duration_seconds=round(total_dur, 2),
        total_cost_usd=final_state.cost_summary.get("total_cost_usd", 0.0),
        qa_passed=final_state.qa_passed,
        qa_report=final_state.qa_report,
        cost_summary=final_state.cost_summary,
        logs=final_state.logs
    )
