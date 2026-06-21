import logging
from src.app.services.langgraph_engine import lead_scoring_graph

logger = logging.getLogger("lead-engine.ai-service")

class AIService:
    def score_lead(self, lead: dict) -> dict:
        """
        Scores a lead using LangGraph. Returns a default score if the engine fails.
        """
        try:
            return lead_scoring_graph.invoke({"lead": lead})
        except Exception as e:
            logger.error(f"LangGraph scoring failed for lead {lead.get('email')}: {e}")
            # Graceful degradation: return a default score instead of raising an error
            return {"score": 0, "reason": "AI scoring unavailable"}
