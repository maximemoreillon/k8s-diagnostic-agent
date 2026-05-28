from dotenv import load_dotenv

load_dotenv()

from agent import agent

result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "Is there a namesapce called 'moreillon'?"}
        ]
    },
)

print(result["messages"][-1].content_blocks)
