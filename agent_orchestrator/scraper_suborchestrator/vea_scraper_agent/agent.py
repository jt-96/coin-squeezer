from google.adk.agents.llm_agent import Agent

vea_scraper_agent = Agent(
    model='gemini-3.5-flash',
    name='vea_scraper_agent',
    description='A web scraper that extracts values from the Vea Supermarket site',
    instruction=""" You are a web scraper and data extrator specialist.

    Your job is to scrap the contents of websites, and obtain the name and price of each of the items provided in that list of sites.

    
    """,
)
