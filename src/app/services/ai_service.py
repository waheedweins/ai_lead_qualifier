from src.app.services.langgraph_engine import lead_scoring_graph

class AIService:
    def score_lead(self, lead: dict) -> dict:
        return lead_scoring_graph.invoke({"lead": lead})
