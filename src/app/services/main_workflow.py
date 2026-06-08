from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.app.workers.scraping_worker import run_scraping_job
from src.app.workers.lead_processor import process_lead
from src.app.core.database import SessionLocal
from src.app.models.lead import Lead

class WorkflowState(TypedDict):
    query: str
    results_count: int

def scrape_and_ingest(state: WorkflowState) -> WorkflowState:
    # 1. Scrape from Google Maps and save to RDS
    count = run_scraping_job(state["query"])
    state["results_count"] = count
    return state

def process_and_outreach(state: WorkflowState) -> WorkflowState:
    # 2. Fetch the new leads and run them through LangGraph scoring/outreach
    db = SessionLocal()
    try:
        new_leads = db.query(Lead).filter(Lead.status == "new").all()
        for lead in new_leads:
            lead_data = {
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "source": lead.source
            }
            process_lead(lead_data)
            lead.status = "processed"
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return state

def build_graph():
    builder = StateGraph(WorkflowState)
    builder.add_node("scrape", scrape_and_ingest)
    builder.add_node("process", process_and_outreach)
    builder.set_entry_point("scrape")
    builder.add_edge("scrape", "process")
    builder.add_edge("process", END)
    return builder.compile()

workflow = build_graph()
