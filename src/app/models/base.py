# Import the central declarative base
from src.app.core.database import Base

# Explicitly import all models here so Alembic's target_metadata can discover them
from src.app.models.lead import Lead
from src.app.models.agent_run import AgentRun
