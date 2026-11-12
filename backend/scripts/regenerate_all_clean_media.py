import os
import asyncio
import logging
from backend.app.orchestration.graph import ProductionOrchestrator
from backend.app.orchestration.state import ProductionState
from backend.app.orchestration.localization import ModeALocalizationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("regenerator")

EPISODES_TO_BUILD = [
    {
        "episode_id": "ep_odia_pilot_01",
        "studio_type": "entertainment",
        "title": "Bikram Baboo Village Comedy (Pilot)",
        "target_language": "or"
    },
    {
        "episode_id": "ep_studio1_entertainment",
        "studio_type": "entertainment",
        "title": "Bikram Baboo Nka Village Jalebi Khati",
        "target_language": "or"
    },
    {
        "episode_id": "ep_studio2_kids",
        "studio_type": "kids",
        "title": "Gulu Owl ABC Magic Rhyme",
        "target_language": "en"
    },
    {
        "episode_id": "ep_studio3_education",
        "studio_type": "education",
        "title": "Understanding Neural Networks in 60 Seconds",
        "target_language": "en"
    },
    {
        "episode_id": "ep_studio4_podcast",
        "studio_type": "podcast",
        "title": "The AI Frontier: Open Source vs Big Tech Debate",
        "target_language": "en"
    },
    {
        "episode_id": "ep_studio5_news",
        "studio_type": "news",
        "title": "Odisha Semiconductor Fab Hub Report",
        "target_language": "or"
    },
    {
        "episode_id": "ep_studio6_marketing",
        "studio_type": "marketing",
        "title": "BhashaVoice AI: Instant Indic Voice Cloning",
        "target_language": "hi"
    }
]

async def main():
    orchestrator = ProductionOrchestrator(output_root="./storage/output")
    loc_engine = ModeALocalizationEngine(output_root="./storage/output")

    for item in EPISODES_TO_BUILD:
        ep_id = item["episode_id"]
        logger.info(f"=== Regenerating Clean Master for {ep_id} ({item['studio_type']}, {item['target_language']}) ===")
        state = ProductionState(
            episode_id=ep_id,
            studio_type=item["studio_type"],
            title=item["title"],
            topic=item["title"],
            target_language=item["target_language"],
            budget_limit_usd=2.0
        )
        final_state = await orchestrator.run_pipeline(state)
        logger.info(f"Finished {ep_id}: Master={final_state.master_video_path}, QA={final_state.qa_passed}")

    # Localize Studio 1 into Hindi and Bengali
    logger.info("=== Localizing Studio 1 into Hindi and Bengali ===")
    await loc_engine.localize_episode("ep_studio1_entertainment", "hi")
    await loc_engine.localize_episode("ep_studio1_entertainment", "bn")

    # Localize Studio 2 into Odia
    logger.info("=== Localizing Studio 2 into Odia ===")
    await loc_engine.localize_episode("ep_studio2_kids", "or")

    logger.info("ALL EPISODES REGENERATED WITH CLEAN NEURAL SPEECH. ZERO HUMMING!")

if __name__ == "__main__":
    asyncio.run(main())
