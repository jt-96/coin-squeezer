import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=4, period=60)
def safe_rate_limit_trigger():
    pass

async def rate_limit_callback(callback_context):
    await asyncio.to_thread(safe_rate_limit_trigger)

vea_scraper_agent = Agent(
    model='gemini-3.5-flash',
    name='vea_scraper_agent',
    description='A web scraper that extracts values from the Vea Supermarket site',
    # instruction=""" You are a web scraper and data extrator specialist.

    # Your job is to scrap the contents of websites, and obtain the name and price of each of the items provided in that list of sites using the tools provided.

    
    # """,
    instruction=""" You are a web scraper and data extractor specialist

    Your job is to scrap the contents of websites, and obtain the name and price of a link provided to you, using the tools available.

    Only extract text content, ignore raw scripts, tags, stylesheets, or heavy HTML templates.
    
    """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "chrome-devtools-mcp@latest", "--headless"]
                )
            )
        )
    ],
    before_agent_callback=rate_limit_callback
)