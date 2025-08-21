# flake8: noqa
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import START , END , StateGraph
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode , tools_condition
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import interrupt , Command
import json

load_dotenv()

llm = init_chat_model(model_provider='openai',model='gpt-4.1');

class State(TypedDict):
    messages : Annotated[list,add_messages]
    
@tool()
def human_help(query:str):
    """ this is the tool that can be called whenever human assistance is needed to the user. """
    response = interrupt({
        "query":query
    })
    return response["data"]
    
tools = [human_help]

    
llm_with_tools = llm.bind_tools(tools=tools)


def chatnode(state:State):
    response = llm_with_tools.invoke(state["messages"]);
    return {
        "messages":[response]
    }
    
tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)
graph_builder.add_node('chatnode',chatnode)
graph_builder.add_node('tools',tool_node)
graph_builder.add_edge(START,'chatnode')
graph_builder.add_conditional_edges('chatnode',tools_condition)
graph_builder.add_edge('tools','chatnode')




def graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)


DB_URL='mongodb://admin:admin@mongodb:27017'


def main1():
    query = input("----->")
    with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
        graph = graph_with_checkpointer(checkpointer=checkpointer)
        
        config={
            "configurable":{
                "thread_id":"11"
            }
        }
        
        _state:State = {
            'messages':[{'role':'user',"content":query}]
        }
        
        for events in graph.stream(_state,stream_mode='values',config=config):
            if 'messages' in events:
                events["messages"][-1].pretty_print()
    
main1()


def main2():
    with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
        
        graph = graph_with_checkpointer(checkpointer=checkpointer)
        
        config = {
            "configurable":{
                "thread_id":"11"
            }
        }
        
        state = graph.get_state(config=config)
        
        last_message = state.values['messages'][-1]
        
        tool_call = last_message.additional_kwargs.get('tool_calls',[])
        
        user_query = None
        
        for call in tool_call:
            if call.get("function",{}).get("name") == "human_help":
                args = call["function"].get("arguments","{}")
                try:
                    args_dict = json.loads(args)
                    user_query = args_dict.get("query")
                except json.JSONDecodeError:
                    print("Failed to get the user query")
        print("User has the query ",user_query)
        
        solution = input("----->")
        
        resume_command = Command(resume={"data":solution})
        
        for event in graph.stream(resume_command,config,stream_mode='values'):
            if 'messages' in event:
                event['messages'][-1].pretty_print()
        
#main2()