from src.app.services.langgraph_engine import lead_scoring_graph
import logging

logger = logging.getLogger("lead-engine.ai-service")


class AIService:
    def score_lead(self, lead: dict) -> dict:
        try:
            return lead_scoring_graph.invoke({"lead": lead})
        except Exception as e:
            logger.error(f"LangGraph scoring failed for lead {lead.get('email')}: {e}")
            raise
