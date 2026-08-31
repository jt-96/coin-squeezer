import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from ratelimit import limits, sleep_and_retry
from typing import Literal
from pydantic import BaseModel, Field
from .mas_sites_list import mas_sites

class ScrapItem(BaseModel):
    product_name: str = Field(description="The name of the product.")
    product_price: str = Field(description="The current price of the product.")
    product_store: Literal["MasOnline"] = Field(default="MasOnline", description="The store from where the product comes from.")

class ScrapCollection(BaseModel):
    products: list[ScrapItem] = Field(default=list, description="List of Products")

@sleep_and_retry
@limits(calls=4, period=60)
def safe_rate_limit_trigger():
    pass

@sleep_and_retry
@limits(calls=5, period=60)
def safe_model_limit_trigger():
    pass

async def init_agent_callback(callback_context):
    callback_context.state["allowed_mas_sites"] = mas_sites

async def rate_limit_tool_callback(tool, args, tool_context):
    await asyncio.to_thread(safe_rate_limit_trigger)
    return None

async def rate_limit_model_callback(callback_context, llm_request):
    await asyncio.to_thread(safe_model_limit_trigger)
    return None

mas_scraper_agent = Agent(

    model='gemini-3.5-flash',
    name='mas_scraper_agent',
    description='A web scraper that extracts names and prices from the MasOnline Supermarket site',
    instruction=""" You are a web scraper and data extrator specialist.
    Your job is to scrap the contents of websites, and obtain the name and price of each of the links provided in {allowed_mas_sites} using the tools available.
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
    output_schema=ScrapCollection,
    output_key="mas_result_data",
    before_agent_callback=init_agent_callback,
    before_tool_callback=rate_limit_tool_callback,
    before_model_callback=rate_limit_model_callback
)