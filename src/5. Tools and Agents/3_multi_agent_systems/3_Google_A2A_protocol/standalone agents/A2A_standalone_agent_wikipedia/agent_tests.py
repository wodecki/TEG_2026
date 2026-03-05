from agent import WikipediaAgent
from dotenv import load_dotenv
load_dotenv()

agent = WikipediaAgent()
sessionID = "session_12345"

query = "Tell me abaout Adam Mickiewicz"
response = agent.invoke(query, sessionID)
print(response)