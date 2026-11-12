import pytest
import os
from backend.app.orchestration.graph import ProductionOrchestrator
from backend.app.orchestration.state import ProductionState

@pytest.mark.asyncio
async def test_full_pipeline_odia_comedy(tmp_path):
    orchestrator = ProductionOrchestrator(output_root=str(tmp_path))
    state = ProductionState(
        episode_id="ep_test_odia_comedy",
        studio_type="entertainment",
        title="Bikram Baboo Village Comedy",
        topic="Village market arrival and hilarious sweet shop incident",
        target_language="or",
        budget_limit_usd=2.0
    )

    final_state = await orchestrator.run_pipeline(state)

    assert final_state.status == "completed"
    assert final_state.qa_passed is True
    assert final_state.master_video_path is not None
    assert os.path.exists(final_state.master_video_path)
    assert final_state.social_video_path is not None
    assert os.path.exists(final_state.social_video_path)
    
    # Check QA probe results
    qa = final_state.qa_report
    assert qa.get("passed") is True
    assert qa.get("duration_seconds", 0) > 8.0
    assert qa.get("video_codec") == "h264"
    assert qa.get("audio_codec") == "aac"

    # Check production economics
    cost = final_state.cost_summary
    assert cost.get("within_budget") is True
    assert cost.get("total_cost_usd") < 0.20
    assert cost.get("cost_per_minute_usd") <= 0.20

@pytest.mark.asyncio
async def test_full_pipeline_kids_rhyme(tmp_path):
    orchestrator = ProductionOrchestrator(output_root=str(tmp_path))
    state = ProductionState(
        episode_id="ep_test_kids_rhyme",
        studio_type="kids",
        title="Gulu Owl Star Counting",
        topic="Preschool counting numbers 1 and 2",
        target_language="en",
        budget_limit_usd=1.5
    )

    final_state = await orchestrator.run_pipeline(state)
    assert final_state.status == "completed"
    assert final_state.qa_passed is True
    assert os.path.exists(final_state.master_video_path)
