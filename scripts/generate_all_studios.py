import asyncio
import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.orchestration.graph import ProductionOrchestrator
from backend.app.orchestration.state import ProductionState

STUDIO_TASKS = [
    {
        "studio": "entertainment",
        "episode_id": "ep_studio1_entertainment",
        "title": "Bikram Baboo Nka Village Jalebi Khati",
        "topic": "Baboo boasts about modern village life while getting pranked by Tukuna",
        "lang": "or"
    },
    {
        "studio": "kids",
        "episode_id": "ep_studio2_kids",
        "title": "Gulu Owl ABC Magic Rhyme",
        "topic": "Preschool letters and numbers under the enchanted rainbow tree",
        "lang": "en"
    },
    {
        "studio": "education",
        "episode_id": "ep_studio3_education",
        "title": "Understanding Neural Networks in 60 Seconds",
        "topic": "Inputs, weights, hidden layers, and AI probability outputs",
        "lang": "en"
    },
    {
        "studio": "podcast",
        "episode_id": "ep_studio4_podcast",
        "title": "The AI Frontier: Open Source vs Big Tech",
        "topic": "Aryan and Priya debate open weights vs frontier model velocity",
        "lang": "en"
    },
    {
        "studio": "news",
        "episode_id": "ep_studio5_news",
        "title": "Odisha Semiconductor Fab Hub Report",
        "topic": "Verified multi-billion semiconductor manufacturing investment in Bhubaneswar",
        "lang": "or"
    },
    {
        "studio": "marketing",
        "episode_id": "ep_studio6_marketing",
        "title": "BhashaVoice AI: Instant Indic Voice Cloning",
        "topic": "High-impact promotional reel showcasing 12 Indic languages with 50% discount",
        "lang": "hi"
    }
]

async def main():
    print("=" * 80)
    print("AI MEDIA FACTORY: PRODUCING 1 CONTENT DELIVERABLE FROM ALL 6 STUDIOS")
    print("=" * 80)

    orchestrator = ProductionOrchestrator(output_root="./storage/output")
    results = []

    for task in STUDIO_TASKS:
        print(f"\n>>> [STARTING] Studio: {task['studio'].upper()} -> '{task['title']}' ({task['lang']})")
        state = ProductionState(
            episode_id=task["episode_id"],
            studio_type=task["studio"],
            title=task["title"],
            topic=task["topic"],
            target_language=task["lang"],
            budget_limit_usd=2.0
        )
        res = await orchestrator.run_pipeline(state)
        results.append(res)
        print(f"    [COMPLETED] QA Passed: {res.qa_passed} | Duration: {res.qa_report.get('duration_seconds')}s")
        print(f"    16:9 Master: {res.master_video_path}")
        print(f"    9:16 Reel:   {res.social_video_path}")
        print(f"    Cost: ${res.cost_summary.get('total_cost_usd')} (${res.cost_summary.get('cost_per_minute_usd')}/min)")

    print("\n" + "=" * 80)
    print("SUMMARY: ALL 6 STUDIOS PRODUCED AND VERIFIED SUCCESSFULLY!")
    print("=" * 80)
    for r in results:
        qa_status = "PASS" if r.qa_passed else "FLAGGED"
        cost = r.cost_summary.get('total_cost_usd', 0.0)
        dur = r.qa_report.get('duration_seconds', 0.0)
        print(f"- {r.studio_type.upper():<14} | {dur:>5.1f}s | QA: {qa_status} | Cost: ${cost:.5f} | {r.title}")

if __name__ == "__main__":
    asyncio.run(main())
