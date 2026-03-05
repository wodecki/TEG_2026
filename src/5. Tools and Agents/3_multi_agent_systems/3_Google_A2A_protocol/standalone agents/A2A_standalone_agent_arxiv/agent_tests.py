from agent import Agent
from dotenv import load_dotenv
load_dotenv()

agent = Agent()
sessionID = "session_12345"

query = "Find papers on quantum computing"
response = agent.invoke(query, sessionID)
print(response)