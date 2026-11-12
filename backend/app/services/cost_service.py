import logging
from sqlalchemy.orm import Session
from backend.app.models.schema import CostRecord, Episode
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Unit costs in USD
PRICING_TABLE = {
    "openrouter_llm": 0.000003,      # ~$3.00 per 1M tokens average
    "maya3_gpu": 0.00018,            # ~$0.65/hour on serverless GPU -> ~$0.00018/sec
    "rendering_cpu_gpu": 0.00005,    # ~$0.00005/sec
    "storage_r2": 0.000015           # ~$0.015/GB-month
}

class CostService:
    @staticmethod
    def record_cost(
        db: Session,
        episode_id: str,
        service_type: str,
        units_consumed: float,
        unit_type: str
    ) -> CostRecord:
        rate = PRICING_TABLE.get(service_type, 0.0001)
        cost_usd = round(units_consumed * rate, 5)

        record = CostRecord(
            episode_id=episode_id,
            service_type=service_type,
            units_consumed=units_consumed,
            unit_type=unit_type,
            cost_usd=cost_usd
        )
        db.add(record)

        # Update episode actual cost
        episode = db.query(Episode).filter(Episode.id == episode_id).first()
        if episode:
            episode.actual_cost_usd = round(episode.actual_cost_usd + cost_usd, 5)
            db.add(episode)

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_episode_cost_summary(db: Session, episode_id: str) -> dict:
        records = db.query(CostRecord).filter(CostRecord.episode_id == episode_id).all()
        episode = db.query(Episode).filter(Episode.id == episode_id).first()
        
        breakdown = {}
        total = 0.0
        for r in records:
            breakdown[r.service_type] = breakdown.get(r.service_type, 0.0) + r.cost_usd
            total += r.cost_usd

        return {
            "episode_id": episode_id,
            "budget_limit_usd": episode.budget_limit_usd if episode else settings.DEFAULT_EPISODE_BUDGET_USD,
            "actual_cost_usd": round(total, 5),
            "breakdown": {k: round(v, 5) for k, v in breakdown.items()},
            "within_budget": total <= (episode.budget_limit_usd if episode else settings.DEFAULT_EPISODE_BUDGET_USD)
        }
