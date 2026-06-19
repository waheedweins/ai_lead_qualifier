import logging
from src.app.services.langgraph_engine import lead_scoring_graph
from src.app.services.outreach_graph import outreach_graph

logger = logging.getLogger("lead-engine.lead-processor")


def process_lead(lead: dict) -> dict:
    """
    Runs a lead through the LangGraph scoring pipeline.
    If the lead is HOT, triggers the outreach graph.
    """
    try:
        result = lead_scoring_graph.invoke({"lead": lead})
        decision = result.get("decision")

        if decision == "hot":
            logger.info(f"Lead {lead.get('email')} qualified as HOT. Triggering outreach.")
            outreach_graph.invoke({"lead": lead})
        else:
            logger.info(f"Lead {lead.get('email')} categorised as COLD. No outreach sent.")

        return result
    except Exception as e:
        logger.error(f"Lead processing failed for {lead.get('email')}: {e}", exc_info=True)
        raise
