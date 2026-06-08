import logging
from src.app.services.langgraph_engine import lead_scoring_graph
from src.app.services.outreach_graph import outreach_graph

logger = logging.getLogger("lead-processor")

def process_lead(lead: dict) -> dict:
    try:
        result = lead_scoring_graph.invoke({"lead": lead})
        if result.get("decision") == "hot":
            logger.info(f"Lead {lead.get('email')} qualified as HOT. Triggering outreach workflow.")
            outreach_graph.invoke({"lead": lead})
        else:
            logger.info(f"Lead {lead.get('email')} categorized as COLD.")
        return result
    except Exception as e:
        logger.error(f"Failed processing engine for lead {lead.get('email')}: {str(e)}")
        raise e
