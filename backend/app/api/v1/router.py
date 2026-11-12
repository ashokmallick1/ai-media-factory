import os
import json
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db, engine, Base
from backend.app.models.schema import Brand, Character, VoiceProfile, Project, Episode, ProductionJob
from backend.app.schemas.api import BrandCreate, CharacterCreate, EpisodeCreateRequest, ProductionRunResponse
from backend.app.orchestration.graph import ProductionOrchestrator
from backend.app.orchestration.state import ProductionState
from backend.app.orchestration.localization import ModeALocalizationEngine

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
            "primary_language": "en",
            "status": "active"
        },
        {
            "id": "education",
            "name": "Education & Tutorials",
            "description": "Tech tutorials, AI explainers, animated presentations, quizzes.",
            "render_engine": "Remotion",
            "primary_language": "en",
            "status": "active"
        },
        {
            "id": "podcast",
            "name": "AI Podcast Studio",
            "description": "Multi-speaker virtual hosts, audio mixing, waveform audiograms.",
            "render_engine": "FFmpeg + Remotion",
            "primary_language": "en",
            "status": "active"
        },
        {
            "id": "news",
            "name": "News & Documentaries",
            "description": "Fact-checking research, verified citations, ticker tapes.",
            "render_engine": "Remotion + FFmpeg",
            "primary_language": "or",
            "status": "active"
        },
        {
            "id": "marketing",
            "name": "Marketing & Ads",
            "description": "Product ads, promotional reels, kinetic typography.",
            "render_engine": "HyperFrames / Remotion",
            "primary_language": "hi",
            "status": "active"
        }
    ]

@api_router.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    brands = db.query(Brand).all()
    if not brands:
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
        c4 = Character(
            id=str(uuid.uuid4()),
            brand_id=target_brand_id,
            name="Dr. Bhasha",
            role="educator",
            bio="AI researcher and computer scientist explaining complex concepts simply.",
            personality="Authoritative, crisp, visionary."
        )
        c5 = Character(
            id=str(uuid.uuid4()),
            brand_id=target_brand_id,
            name="Aryan",
            role="podcast_host",
            bio="Co-host of The AI Frontier podcast, inquisitive and dynamic.",
            personality="Conversational, enthusiastic."
        )
        c6 = Character(
            id=str(uuid.uuid4()),
            brand_id=target_brand_id,
            name="Priya",
            role="podcast_host",
            bio="Tech analyst reviewing AI benchmarks and industry shifts.",
            personality="Analytical, sharp, eloquent."
        )
        db.add_all([c1, c2, c3, c4, c5, c6])
        db.commit()
        chars = [c1, c2, c3, c4, c5, c6]
    return chars

@api_router.get("/episodes")
def list_episodes():
    """
    Returns all generated video deliverables across the 6 production studios
    formatted for instant streaming in the YouTube-like player.
    """
    output_dir = "./storage/output"
    if not os.path.exists(output_dir):
        return []

    meta_map = {
        "ep_studio1_entertainment": {
            "title": "Bikram Baboo Nka Village Jalebi Khati",
            "studio_type": "entertainment",
            "language": "or",
            "channel_name": "Mo Gaon Comedy Studio",
            "description": "Bikram Baboo struts into the village market boasting about his grand arrival, only for Tukuna to reveal everyone was lining up for free jalebis at the cinema hall! Authentic Odia village humor with Maya3 native speech.",
            "views": "3.8K views",
            "duration": 16.8
        },
        "ep_studio2_kids": {
            "title": "Gulu Owl ABC Magic Rhyme",
            "studio_type": "kids",
            "language": "en",
            "channel_name": "Little Friends Cartoon Studio",
            "description": "Join Gulu the friendly wise owl under the enchanted rainbow tree as we sing, dance, and count twinkling stars together! Built with preschool safety gates.",
            "views": "12.4K views",
            "duration": 14.3
        },
        "ep_studio3_education": {
            "title": "Understanding Neural Networks in 60 Seconds",
            "studio_type": "education",
            "language": "en",
            "channel_name": "AI Explainer Academy",
            "description": "How do artificial brains actually learn? A rapid visual breakdown of inputs, weights, hidden layers, and AI probability outputs by Dr. Bhasha.",
            "views": "8.1K views",
            "duration": 18.1
        },
        "ep_studio4_podcast": {
            "title": "The AI Frontier: Open Source vs Big Tech Debate",
            "studio_type": "podcast",
            "language": "en",
            "channel_name": "AI Frontier Podcast",
            "description": "Aryan and Priya debate open weights vs frontier model velocity. Are open-source reasoning models moving faster than Big Tech labs?",
            "views": "5.6K views",
            "duration": 18.1
        },
        "ep_studio5_news": {
            "title": "Odisha Semiconductor Fab Hub Report",
            "studio_type": "news",
            "language": "or",
            "channel_name": "Odisha Factual Newsroom",
            "description": "Verified breaking report: State clears multi-billion semiconductor fab project in Bhubaneswar, creating over 20,000 engineering jobs.",
            "views": "19.2K views",
            "duration": 16.9
        },
        "ep_studio6_marketing": {
            "title": "BhashaVoice AI: Instant Indic Voice Cloning",
            "studio_type": "marketing",
            "language": "hi",
            "channel_name": "BhashaAI Brand Lab",
            "description": "High-impact promotional reel showcasing 12 Indic languages with 50% launch discount. Instant zero-shot voice cloning for creators.",
            "views": "45.1K views",
            "duration": 16.8
        },
        "ep_odia_pilot_01": {
            "title": "Bikram Baboo Village Comedy (Pilot)",
            "studio_type": "entertainment",
            "language": "or",
            "channel_name": "Mo Gaon Comedy Studio",
            "description": "Pilot episode of Bikram Baboo's comedic village antics in authentic Odia dialogue.",
            "views": "2.1K views",
            "duration": 16.8
        }
    }

    episodes = []
    for ep_id in sorted(os.listdir(output_dir)):
        ep_path = os.path.join(output_dir, ep_id)
        if not os.path.isdir(ep_path):
            continue

        master_file = None
        social_file = None
        for f in os.listdir(ep_path):
            if f.startswith("master_16x9") and f.endswith(".mp4"):
                master_file = f
            elif f.startswith("social_9x16") and f.endswith(".mp4"):
                social_file = f

        if master_file:
            meta_file = os.path.join(ep_path, "metadata.json")
            meta = None
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as mf:
                        meta = json.load(mf)
                except Exception:
                    pass

            if not meta:
                meta = meta_map.get(ep_id, {
                    "title": ep_id.replace("_", " ").title(),
                    "studio_type": "entertainment",
                    "language": "or",
                    "channel_name": "AI Media Factory",
                    "description": "Autonomously produced episode by AI Media Factory OS.",
                    "views": "1.2K views",
                    "duration": 15.0
                })

            localized_map = meta.get("localized_versions", {})
            for f in os.listdir(ep_path):
                if f.startswith("master_16x9_") and f.endswith(".mp4"):
                    lang = f.replace("master_16x9_", "").replace(".mp4", "")
                    if lang not in localized_map:
                        soc = f"social_9x16_{lang}.mp4"
                        localized_map[lang] = {
                            "master_video_url": f"/media/output/{ep_id}/{f}",
                            "social_video_url": f"/media/output/{ep_id}/{soc}" if os.path.exists(os.path.join(ep_path, soc)) else f"/media/output/{ep_id}/{f}"
                        }

            orig_lang = meta.get("language", "or")
            all_langs = list(dict.fromkeys([orig_lang] + list(localized_map.keys()) + meta.get("available_languages", [])))

            episodes.append({
                "id": ep_id,
                "title": meta.get("title", ep_id),
                "studio_type": meta.get("studio_type", "entertainment"),
                "language": orig_lang,
                "available_languages": all_langs,
                "channel_name": meta.get("channel_name", "AI Media Factory"),
                "description": meta.get("description", ""),
                "views": meta.get("views", "1.5K views"),
                "duration": meta.get("duration", 15.0),
                "master_video_url": f"/media/output/{ep_id}/{master_file}",
                "social_video_url": f"/media/output/{ep_id}/{social_file}" if social_file else f"/media/output/{ep_id}/{master_file}",
                "localized_versions": localized_map
            })

    return episodes

@api_router.post("/episodes/{episode_id}/localize")
async def localize_episode(episode_id: str, target_language: str = Query(..., regex="^(or|hi|bn|en|te|ta)$")):
    """
    Mode A Localization: Reuses approved visual video stream, synthesizes
    culturally adapted dialogue tracks with Maya3 Indic TTS, and replaces the master audio.
    """
    engine = ModeALocalizationEngine()
    try:
        res = await engine.localize_episode(episode_id, target_language)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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

    final_state = await orchestrator.run_pipeline(init_state)
    total_dur = sum(s.duration_seconds for s in final_state.scenes)

    # Save metadata.json for instant UI playback
    ep_dir = os.path.join("./storage/output", episode_id)
    if os.path.exists(ep_dir):
        ch_names = {
            "entertainment": "Mo Gaon Comedy Studio",
            "kids": "Little Friends Cartoon Studio",
            "education": "AI Explainer Academy",
            "podcast": "AI Frontier Podcast",
            "news": "Odisha Factual Newsroom",
            "marketing": "BhashaAI Brand Lab"
        }
        meta_payload = {
            "id": episode_id,
            "title": final_state.title,
            "studio_type": final_state.studio_type,
            "language": final_state.target_language,
            "available_languages": [final_state.target_language, "hi", "en", "or"],
            "channel_name": ch_names.get(final_state.studio_type, "AI Media Factory"),
            "description": final_state.topic,
            "views": "New Release",
            "duration": round(total_dur, 1),
            "master_video_url": f"/media/output/{episode_id}/{os.path.basename(final_state.master_video_path)}" if final_state.master_video_path else "",
            "social_video_url": f"/media/output/{episode_id}/{os.path.basename(final_state.social_video_path)}" if final_state.social_video_path else "",
            "localized_versions": {}
        }
        with open(os.path.join(ep_dir, "metadata.json"), "w", encoding="utf-8") as mf:
            json.dump(meta_payload, mf, indent=2, ensure_ascii=False)

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
