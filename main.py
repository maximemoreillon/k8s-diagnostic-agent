from dotenv import load_dotenv
import chainlit as cl
from agent import agent

load_dotenv()


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):

    history = cl.user_session.get("history")

    history.append({"role": "user", "content": message.content})

    # NOTE: Limit to 10 message pair
    # NOTE: ainvoke is async
    result = await agent.ainvoke({"messages": history[-20:]})

    response = result["messages"][-1].content

    history.append({"role": "assistant", "content": response})

    await cl.Message(content=response).send()
