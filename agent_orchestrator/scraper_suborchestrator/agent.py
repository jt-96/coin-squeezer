# from google.adk.agents.llm_agent import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from .vea_scraper_agent.agent import vea_scraper_agent

scraper_suborchestrator_agent = ParallelAgent(
    # model='gemini-3.5-flash',
    # name='scraper_suborchestrator',
    # description='A orchestrator that manages the scrapers work and data',
    # instruction=""" You are an orchestrator of subagents
    
    # Your main job is to manage and control the work of your scrapers subagents, reporting when their job is complete to relay the data obtained by the scrapers to the next step of the specified order of execution.
    # """,
    name="parallel_scrapers",
    sub_agents=[vea_scraper_agent]
)
