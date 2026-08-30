# from google.adk.agents.llm_agent import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from .vea_scraper_agent.agent import vea_scraper_agent
from .mas_scraper_agent.agent import mas_scraper_agent
from .carrefour_scraper_agent.agent import carrefour_scraper_agent

scraper_suborchestrator_agent = ParallelAgent(
    description='A suborchestrator that manages the subagents in change of data extraction.',
    name="parallel_scrapers",
    sub_agents=[vea_scraper_agent, mas_scraper_agent, carrefour_scraper_agent]
)
