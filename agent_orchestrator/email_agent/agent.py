import os
import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters
from ratelimit import limits, sleep_and_retry

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

GOOGLE_USER_EMAIL_SENDER = os.environ.get("GOOGLE_USER_EMAIL_SENDER")
GOOGLE_USER_EMAIL_DESTINATION = os.environ.get("GOOGLE_USER_EMAIL_DESTINATION")

email_agent = Agent(
    model='gemini-3.5-flash',
    name='email_agent',
    description='An assistant in charge of email parsing and communications.',
    instruction=f"""You are an email assistant

    Your role is to parse the data recieved from the previous agent in the order of execution and send it through email, using the connected MCP tool.

    This data {{parsed_data}} should be formatted as a table, containing the name of the product and each price from the stores.

    From: {GOOGLE_USER_EMAIL_SENDER}
    Recipient: {GOOGLE_USER_EMAIL_DESTINATION}
    Subject: "Coin Squeezer Notification!"
    Body: "There are new offers to check! *PARSED TABLE GOES HERE*"
    
    If there's an error during the operation, say so, otherwise respond with "Email Sent!" to finish.
    """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["workspace-mcp", "--tools", "gmail"],
                    env={
                        "GOOGLE_OAUTH_CLIENT_ID": os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
                        "GOOGLE_OAUTH_CLIENT_SECRET": os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
                    }
                ),
                timeout=30,
            ),
            tool_filter=["send_gmail_message"],
        )
    ],
    before_tool_callback=rate_limit_tool_callback,
    before_model_callback=rate_limit_model_callback
)
