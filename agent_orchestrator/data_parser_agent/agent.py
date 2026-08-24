import asyncio
from google.adk.agents.llm_agent import Agent
from pydantic import BaseModel, Field
from ratelimit import limits, sleep_and_retry

class ParsedItem(BaseModel):
    product_name: str = Field(description="The name of the product.")
    vea_price: int = Field(description="The current price of the product in Vea Supermarket.")
    mas_price: int = Field(description="The current price of the product in MasOnline Supermarket.")
    carrefour_price: int = Field(description="The current price of the product in Carrefour Supermarket.")

class ParsedCollection(BaseModel):
    parsed_products: list[ParsedItem] = Field(default=list, description="List of parsed products.")

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

data_parser_agent = Agent(
    model='gemini-3.5-flash',
    name='data_parser_agent',
    description='Parses information recieved in a specified manner',
    instruction=""" You are a data parser specialist
    
    Your role is to parse the data obtained from previous agents in the specified format, so it can be used for the next agent during the order of execution.

    The dataset that you will used is split into 3 parts:

    - {vea_result_data} for Vea Supermarket.

    - {mas_result_data} for MasOnline Supermarket.

    - {carrefour_result_data} for Carrefour Supermarket.

    You will return a list of products, each product will contain the name and price from each store.

    In case of ambiguity between the data sets, you should find the relation in the naming from each product in order to return a single product entry that contains all three prices.

    Once finished parsing, the final result will be saved in the output_key {parsed_data}.
    """,
    output_schema=ParsedCollection,
    output_key="parsed_data",
    before_tool_callback=rate_limit_tool_callback,
    before_model_callback=rate_limit_model_callback
)
