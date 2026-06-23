import logging
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Optional
import operator

logger = logging.getLogger("lead-engine.services.langgraph_engine")


class AgentState(TypedDict):
    lead: dict                           # the lead dict being scored
    score: Annotated[int, operator.add]  # accumulates across nodes
    query: str
    results: List[dict]
    decision: str                        # "hot" or "cold" — read by lead_processor.py


def score_lead(state: AgentState) -> dict:
    """
    Scores a lead using simple heuristics and sets a decision.
    Replace the body with an LLM call for production-quality scoring.
    """
    lead = state.get("lead", {})
    logger.info(f"Scoring lead: {lead.get('email', 'unknown')}")

    score = 0

    if lead.get("phone"):
        score += 30        # reachable via WhatsApp
    if lead.get("email") and "placeholder" not in lead.get("email", ""):
        score += 30        # real email address
    if lead.get("address"):
        score += 20        # has a physical location
    if lead.get("name"):
        score += 10        # named business
    if lead.get("title") or lead.get("source"):
        score += 10        # has category/source info

    decision = "hot" if score >= 50 else "cold"
    logger.info(f"Lead {lead.get('email')} scored {score} → decision: {decision}")

    return {"score": score, "decision": decision}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("scoring_node", score_lead)
    graph.set_entry_point("scoring_node")
    graph.add_edge("scoring_node", END)
    return graph.compile()


try:
    lead_scoring_graph = build_graph()
    logger.info("LangGraph initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize LangGraph: {e}")
    lead_scoring_graph = None
