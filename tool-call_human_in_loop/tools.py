# flake8: noqa
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph.message import add_messages
from langgraph.graph import START, END, StateGraph
from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode , tools_condition
import requests


load_dotenv()

@tool()
def get_weather(city: str):
    ''' This is the function that returns the weather condition of the city that was provided to it through paramaters '''
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."

    return "Something went wrong"



llm = init_chat_model(model_provider='openai', model='gpt-4.1')
tools = [get_weather]

llm_with_tools = llm.bind_tools(tools=tools)




def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatnode(state: State):
    response = llm_with_tools.invoke(state['messages'])

    return {
        "messages": [response]
    }

tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node('chatnode', chatnode)
graph_builder.add_node("tools",tool_node)
graph_builder.add_edge(START, 'chatnode')
graph_builder.add_conditional_edges('chatnode',tools_condition)
graph_builder.add_edge('tools','chatnode')
graph_builder.add_edge('chatnode', END)

DB_URL = 'mongodb://admin:admin@mongodb:27017'


def main():
    query = input("----->")

    with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
        graph = compile_graph_with_checkpointer(checkpointer)

        config = {
            "configurable": {
                "thread_id": "7"
            }
        }
        _state = State(
            messages=[{'role': 'user', "content": query}]
        )

        for events in graph.stream(_state,stream_mode='values', config=config):
            if 'messages' in events:
                events['messages'][-1].pretty_print()
                



main()
