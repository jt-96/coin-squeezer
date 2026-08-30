import os
import asyncio
from ratelimit import limits, sleep_and_retry
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

@sleep_and_retry
@limits(calls=4, period=60)
def safe_rate_limit_trigger():
    pass

@sleep_and_retry
@limits(calls=5, period=60)
def safe_model_limit_trigger():
    pass

async def rate_limit_tool_callback(tool, args, tool_context):
    await asyncio.to_thread(safe_rate_limit_trigger)
    return None

async def rate_limit_model_callback(callback_context, llm_request):
    await asyncio.to_thread(safe_model_limit_trigger)
    return None


database_agent = Agent(
    model='gemini-3.5-flash',
    name='database_agent',
    description='Handles parsed data for database updates',
    instruction=""" You are a database administrator

    You are in charge of database operations, inserting and updating rows in the table [products] of the database [coinsqueezer_db], utilizing the tools provided to connect to the Cloud SQL Instance and update new information that comes from the previous agents during order of execution.

    You will recieve a JSON object {parsed_data}, and for each object in the array, you will check each item and perform the following:

    - If the product name of the current item exists in the table, update the corresponding row with only the values for the prices of each store.

    - If the product name does not exists, insert the item as a new row in the table.

    Once finished, respond with 'Database values updated!' to finish.
    """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args= ["-y", "@toolbox-sdk/server", "--prebuilt=cloud-sql-mysql", "--stdio"],
                    env= {
                        "CLOUD_SQL_MYSQL_PROJECT": os.environ.get("CLOUD_SQL_MYSQL_PROJECT"),
                        "CLOUD_SQL_MYSQL_REGION": os.environ.get("CLOUD_SQL_MYSQL_REGION"),
                        "CLOUD_SQL_MYSQL_INSTANCE": os.environ.get("CLOUD_SQL_MYSQL_INSTANCE"),
                        "CLOUD_SQL_MYSQL_DATABASE": os.environ.get("CLOUD_SQL_MYSQL_DATABASE"),
                        "CLOUD_SQL_MYSQL_USER": os.environ.get("CLOUD_SQL_MYSQL_USER"),
                        "CLOUD_SQL_MYSQL_PASSWORD": os.environ.get("CLOUD_SQL_MYSQL_PASSWORD"),
                    },
                ),
                timeout=20
            )
        )
    ],
    before_tool_callback=rate_limit_tool_callback,
    before_model_callback=rate_limit_model_callback
)
