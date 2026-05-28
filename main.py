from dotenv import load_dotenv
import chainlit as cl
from agent import agent

load_dotenv()


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message.content}]}
    )
    await cl.Message(content=result["messages"][-1].content).send()
