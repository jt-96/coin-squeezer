from google.adk.agents.llm_agent import Agent
from .scraper_suborchestrator.agent import scraper_suborchestrator_agent

root_agent = Agent(
    model='gemini-3.5-flash',
    name='orchestrator_agent',
    description='Relays work to subagents and obtains their result',
    instruction=""" You are an orchestrator specialist
    
    Your job is to make sure that the sub-orchestrator and sub-agents you manage complete their work in the specified order.

    When called, you can perform a run of your agents and orchestrators, there's no need to recieve any type of information before proceeding.
    """,
    sub_agents=[scraper_suborchestrator_agent]
)
