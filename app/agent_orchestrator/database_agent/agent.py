from click import command
import os
import json
import asyncio
from ratelimit import limits, sleep_and_retry
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import mysql.connector

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

def update_coinsqueezer_database(parsed_data: str) -> str:
    """Connects to the Cloud SQL Instance and inserts products or updates product prices.
    
    Args:
        parsed_data: A JSON string containing an array of products with their prices.
        
    Returns:
        A string confirming the database action status.
    """
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("CLOUD_SQL_MYSQL_INSTANCE"), 
            user=os.environ.get("CLOUD_SQL_MYSQL_USER"),
            password=os.environ.get("CLOUD_SQL_MYSQL_PASSWORD"),
            database=os.environ.get("CLOUD_SQL_MYSQL_DATABASE")
        )
        cursor = conn.cursor()
        
        # 2. Parse the incoming data
        items = json.loads(parsed_data)
        if isinstance(items, dict) and "parsed_data" in items:
            items = items["parsed_data"]
            
        for item in items:
            product_name = item.get("product_name")

            vea_price = item.get("vea_price", 0)
            mas_price = item.get("mas_price", 0)
            carrefour_price = item.get("carrefour_price", 0)

            # Check if the row exists
            cursor.execute("SELECT id FROM products WHERE name = %s", (product_name))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing row prices
                query = "UPDATE products SET price_vea = %s, price_mas = %s, price_carrefour = %s WHERE product_name = %s"
                cursor.execute(query, (vea_price, mas_price, carrefour_price, product_name))
            else:
                # Insert brand new row
                query = "INSERT INTO products (product_name, price_vea, price_mas, price_carrefour) VALUES (%s, %s, %s)"
                cursor.execute(query, (product_name, vea_price, mas_price, carrefour_price))
                
        conn.commit()
        cursor.close()
        conn.close()
        return "Database values updated successfully!"
        
    except Exception as e:
        return f"Database error encountered: {str(e)}"


database_agent = Agent(
    model='gemini-3.5-flash',
    name='database_agent',
    description='Handles parsed data for database updates',
    instruction=""" You are a database administrator

    You are in charge of database operations, inserting and updating rows in the table [products] of the database [coinsqueezer_db], utilizing the tools provided to connect to the Cloud SQL Instance and update new information that comes from the previous agents during order of execution.

    Utilize the update_coinsqueezer_database tool to pass the JSON string data and update the database.

    You will recieve a JSON object {parsed_data}, and for each object in the array, you will check each item and perform the following:

    - If the product name exists in the table, update the corresponding row with only the values for the prices of each store.

    - If the product name does not exists, insert the item as a new row in the table.

    Once finished, only respond with 'Database values updated!' to finish.
    """,
    tools=[update_coinsqueezer_database],
    before_tool_callback=rate_limit_tool_callback,
    before_model_callback=rate_limit_model_callback
)
