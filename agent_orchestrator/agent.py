from google.adk.agents.sequential_agent import SequentialAgent
from .scraper_suborchestrator.agent import scraper_suborchestrator_agent
from .data_parser_agent.agent import data_parser_agent
from .database_agent.agent import database_agent
from .email_agent.agent import email_agent

root_agent = SequentialAgent(
    description='Relays work to subagents and pass their result to the next agent.',
    name="pipeline",
    sub_agents=[scraper_suborchestrator_agent, data_parser_agent, database_agent, email_agent]
)
