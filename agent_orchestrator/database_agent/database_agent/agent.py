import asyncio
from ratelimit import limits, sleep_and_retry
from google.adk.agents.llm_agent import Agent

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

    You are in charge of database operations, inserting and updating rows in a specified table, utilizing the tools provided to update new information that comes from the previous agents during order of execution.

    You will recieve a JSON object {parsed_data}, and iterate for each object in the array, and insert each object into a row in the database provided.

    It is imperative that you check if the record already exists by checking the product name, if so, only update the values of the product prices of each store.

    Once finished, respond with 'Database values updated!' to finish and proceed to the next agent.
    """,
    before_tool_callback=rate_limit_tool_callback,
    before_model_callback=rate_limit_model_callback
)
