from google.adk.agents.llm_agent import Agent

data_parser_agent = Agent(
    model='gemini-3.5-flash',
    name='data_parser_agent',
    description='Parses information recieved in a specified manner',
    instruction=""" You are a data parser
    
    Your role is to parse the data obtained from other agents in a specified format, so it can be used for the next agent during the order of execution.
    """,
)
