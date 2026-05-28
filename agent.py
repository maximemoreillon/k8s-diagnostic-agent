from langchain.agents import create_agent
from tools import (
    list_namespaces,
    list_pods,
    describe_pod,
    get_pod_logs,
    list_deployments,
    describe_deployment,
    list_events,
    get_node_status,
    list_services,
)
from dotenv import load_dotenv

load_dotenv()


tools = [
    list_namespaces,
    list_pods,
    describe_pod,
    get_pod_logs,
    list_deployments,
    describe_deployment,
    list_events,
    get_node_status,
    list_services,
]

agent = create_agent(
    "openai:gpt-5.4",
    tools=tools,
    system_prompt="You are a kubernetes diagnostic agent and have access to various tools to help answer the user's questions. You can only see the past 20 messages (10 user, 10 assistant) of your interaction with the user",
)


if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "Is there a namesapce called 'moreillon'?"}
            ]
        },
    )

    print(result["messages"][-1].content_blocks)
