from google.adk.apps import App
from .agent_orchestrator.agent import root_agent

app = App(
    root_agent=root_agent,
    name="app",
)
