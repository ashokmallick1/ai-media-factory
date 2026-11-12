import asyncio
import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.orchestration.graph import ProductionOrchestrator
from backend.app.orchestration.state import ProductionState

async def main():
    print("="*70)
    print("AI MEDIA FACTORY: PILOT EPISODE PRODUCTION RUNNER")
    print("="*70)
    
    orchestrator = ProductionOrchestrator(output_root="./storage/output")
    
    # Run Studio 1: Odia Regional Comedy Episode
    print("\n>>> Launching Studio 1: Original Odia Animated Comedy Episode...")
    odia_state = ProductionState(
        episode_id="ep_odia_pilot_01",
        studio_type="entertainment",
        title="Bikram Baboo Village Comedy (Episode 1)",
        topic="Village market arrival and hilarious sweet shop incident",
        target_language="or",
        budget_limit_usd=2.0
    )
    res_odia = await orchestrator.run_pipeline(odia_state)
    print(f"Status: {res_odia.status} | QA Passed: {res_odia.qa_passed}")
    print(f"Master 16:9 Video: {res_odia.master_video_path}")
    print(f"Social 9:16 Video: {res_odia.social_video_path}")
    print(f"Total Cost: ${res_odia.cost_summary.get('total_cost_usd')} (${res_odia.cost_summary.get('cost_per_minute_usd')}/min)")
    
    print("\n" + "="*70)
    print("PRODUCTION COMPLETED SUCCESSFULLY!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
