import logging
from src.app.services.langgraph_engine import lead_scoring_graph

logger = logging.getLogger("lead-engine.ai-service")


class AIService:
    def score_lead(self, lead: dict) -> dict:
        """
        Scores a lead using LangGraph. Returns a safe default if the engine is unavailable.
        """
        if lead_scoring_graph is None:
            logger.error("LangGraph engine failed to initialize — returning default score.")
            return {"score": 0, "decision": "cold", "reason": "AI scoring unavailable"}

        try:
            result = lead_scoring_graph.invoke({
                "lead": lead,
                "score": 0,
                "query": "",
                "results": [],
                "decision": "",
            })
            return result
        except Exception as e:
            logger.error(f"LangGraph scoring failed for lead {lead.get('email')}: {e}")
            return {"score": 0, "decision": "cold", "reason": "AI scoring unavailable"}
