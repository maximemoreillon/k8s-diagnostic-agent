from langchain.agents import create_agent
from tools import list_namespaces

agent = create_agent(
    "openai:gpt-5.4",
    tools=[list_namespaces],
    system_prompt="You are a kubernetes diagnostic agent and have access to various tools to help answer the user's questions",
)
