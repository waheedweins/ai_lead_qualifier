import logging
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

# 1. Define your State structure
class AgentState(TypedDict):
    score: Annotated[int, operator.add]
    query: str
    results: List[dict]

logger = logging.getLogger("lead-engine.services.langgraph_engine")

# 2. Your node function
def score_lead(state: AgentState):
    logger.info(f"Scoring lead for query: {state.get('query')}")
    # Example logic: add 10 to the score
    return {"score": 10}

# 3. Build the graph
def build_graph():
    # Initialize the graph with the state schema
    graph = StateGraph(AgentState)

    # Add the node with a unique name that doesn't conflict with state keys
    graph.add_node("scoring_node", score_lead)
    
    # Define the flow
    graph.set_entry_point("scoring_node")
    graph.add_edge("scoring_node", END)

    # Compile the graph
    return graph.compile()

# 4. Global graph instance for your service
try:
    lead_scoring_graph = build_graph()
    logger.info("LangGraph initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize LangGraph: {e}")
    lead_scoring_graph = None
