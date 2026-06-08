from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    lead: dict
    score: int
    decision: str

def score_lead(state: AgentState) -> AgentState:
    lead = state["lead"]
    email = lead.get("email", "")
    score = 50
    if "gmail" in email:
        score += 20
    if lead.get("phone"):
        score += 10
    if lead.get("name"):
        score += 10
    state["score"] = score
    return state

def decide(state: AgentState) -> AgentState:
    state["decision"] = "hot" if state["score"] >= 70 else "cold"
    return state

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("score", score_lead)
    graph.add_node("decide", decide)
    graph.set_entry_point("score")
    graph.add_edge("score", "decide")
    graph.add_edge("decide", END)
    return graph.compile()

lead_scoring_graph = build_graph()
