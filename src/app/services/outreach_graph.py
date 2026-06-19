import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END

logger = logging.getLogger("lead-engine.outreach")


class OutreachState(TypedDict):
    lead: dict
    channel: str


def choose_channel(state: OutreachState) -> OutreachState:
    lead = state["lead"]
    state["channel"] = "whatsapp" if lead.get("phone") else "email"
    return state


def send_outreach(state: OutreachState) -> OutreachState:
    lead = state["lead"]
    message = f"Hi {lead.get('name', 'there')}, We help businesses grow with AI automation."

    if state["channel"] == "whatsapp":
        # Lazy import avoids crashing at startup when WhatsApp creds are missing
        from src.app.services.whatsapp_service import WhatsAppService
        try:
            svc = WhatsAppService()
            svc.send_message(phone=lead["phone"], message=message)
        except Exception as e:
            logger.error(f"WhatsApp outreach failed for {lead.get('phone')}: {e}")
    else:
        from src.app.services.email_service import EmailService
        try:
            svc = EmailService()
            svc.send_email(recipient=lead["email"], subject="AI Growth Opportunity", content=message)
        except Exception as e:
            logger.error(f"Email outreach failed for {lead.get('email')}: {e}")

    return state


def build_graph():
    graph = StateGraph(OutreachState)
    graph.add_node("choose_channel", choose_channel)
    graph.add_node("send_outreach", send_outreach)
    graph.set_entry_point("choose_channel")
    graph.add_edge("choose_channel", "send_outreach")
    graph.add_edge("send_outreach", END)
    return graph.compile()


outreach_graph = build_graph()
