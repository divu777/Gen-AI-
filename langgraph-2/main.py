# flake8: noqa
from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()


llm = init_chat_model(model_provider='openai', model='gpt-4.1')


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chat_node(state: State):

    print(state)
    print("============")
    response = llm.invoke(state['messages'])
    print(response)
    print("===========")

    return {
        'messages': [response]
    }


graph_builder = StateGraph(State)

graph_builder.add_node('chat_node', chat_node)

graph_builder.add_edge(START, 'chat_node')
graph_builder.add_edge('chat_node', END)



DB_URL='mongodb://admin:admin@mongodb:27017'
    


while True:
    query = input("------>")
    with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
        # Ususally this is done in seperate function and the graph is returned if its not compiled already doing that in the 
        # main funtion is bad
        graph = graph_builder.compile(checkpointer=checkpointer)
        
        config = {
            "configurable":{
                "thread_id":"2"
            }
        }


        _state: State = {
            "messages": [{"role": "user", "content": query}]
        }

        response = graph.invoke(_state,config)

        print(response)
