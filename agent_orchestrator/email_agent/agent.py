from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool import McpToolset
from ratelimit import limits, sleep_and_retry
from auth import get_workspace_access_token 

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

active_token = get_workspace_access_token()

email_agent = Agent(
    model='gemini-3.5-flash',
    name='email_agent',
    description='An assistant in charge of email parsing and communications.',
    # instruction=""" You are an email assistant.
    
    # Your role is to parse the data recieved from the previous agent in the order of execution and send it through email.

    # This data {parsed_data} should be formatted as a table, containing the name of the product and each price from the stores.

    # Once formatted, you can add a small message before hand in the body of the email, saying "Offers updated, check here or on the site!".

    # After that comes the formatted table, this email should be send using the tools provided, to the following email "jetorrico@gmail.com", with the subject "Coin-Squeezer Notification!".

    # Once finished, respond with "Email has been sent!" to finish, if there's an error during any step of this instruction, do notify.
    # """,
    instruction="""You are an email assistant

    Your role is to use the connected Gmail MCP server tools to send an email.
    Recipient: "jetorrico@gmail.com"
    Subject: "Test Email from Agent"
    Body: "Hi. This is an email from an Agent"
    
    If there's an error during the operation, say so, otherwise respond with "Email Sent!" to finish.
    """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=SseServerParams(
                    uri="https://gmailmcp.googleapis.com/mcp/v1",
                    args= ["-y", "@google/workspace-mcp-server", "--credentials", "./secrets/email_oauth_credentials.json", "--stdio"],
                    headers={
                    "Authorization": f"Bearer {active_token}"
                    }
                ),
                timeout=20
            )
        )
    ],
    before_tool_callback=rate_limit_tool_callback,
    before_model_callback=rate_limit_model_callback
)
