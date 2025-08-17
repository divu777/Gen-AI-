# flake8: noqa
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

API_KEY = os.getenv("API_KEY")


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_KEY
)

class State(TypedDict):
    user_query: str | None
    is_coding_question: bool | None
    llm_response: str | None
    coding_accuracy: str | None

graph_builder = StateGraph(State)

class ClassifyResponseType(BaseModel):
    is_coding_question : bool
    

class CodeResponseType(BaseModel):
    code:str

class SimpleResponseType(BaseModel):
    output:str
    

def classify_node(state:State):
    user_query = state['user_query']
    
    SYSTEN_PROMPT= '''
    You are an intelligent classifier agent which based on the user query give the response in boolean if the asked user query
    is a coding related question or not.
    '''
    
    response = client.chat.completions.parse(
        model='deepseek-ai/DeepSeek-V3:fireworks-ai',
        messages = [
            {'role':'system',"content":SYSTEN_PROMPT},
            {"role":"user","content":user_query}
        ],
        response_format = ClassifyResponseType
    )
    
    
    output = response.choices[0].message.content;
    print(output)
    
    jsonresponse = json.loads(output)
    print(jsonresponse["is_coding_question"])
    
    state['is_coding_question']=jsonresponse['is_coding_question']
    
    return state
    
def route_node(state:State)->Literal['coding_node','simple_node']:
    
    coding_question = state['is_coding_question']
    
    if(coding_question):
        return 'coding_node'

    return 'simple_node'  
      
    
    
def coding_node(state:State):
    user_query= state["user_query"];
    
    SYSTEM_PROMPT='''
    You are code generator agent that based on the user query write code snippet only. If asked anything else except that you respond with I couldn't help you with this query, and use 
    different alternatives of this message so it doesn't sound repetative and generic
    '''
    
    
    response = client.chat.completions.parse(
        model='deepseek-ai/DeepSeek-V3:fireworks-ai',
        messages=[
            {'role':'system','content':SYSTEM_PROMPT},
            {'role':'user',"content":user_query}
        ],
        response_format=CodeResponseType
    )
    
    code_response = response.choices[0].message.content;
    
    jsonresponse = json.loads(code_response)
    
    print(jsonresponse['code'])
    
    state['llm_response']=jsonresponse['code']
    
    
    return state
    
    
    
    
def simple_node(state:State):
    user_query= state["user_query"];
    
    SYSTEM_PROMPT='''
    You are code generator agent that based on the user query write code snippet only. If asked anything else except that you respond with I couldn't help you with this query, and use 
    different alternatives of this message so it doesn't sound repetative and generic
    '''
    
    
    response = client.chat.completions.parse(
        model='deepseek-ai/DeepSeek-V3:fireworks-ai',
        messages=[
            {'role':'system','content':SYSTEM_PROMPT},
            {'role':'user',"content":user_query}
        ]
    )
    
    simple_response = response.choices[0].message.content;
    
    print(simple_response);
    
    state['llm_response']=simple_response
    
    return state



graph_builder.add_node('classify_node',classify_node);
graph_builder.add_node('route_node',route_node);
graph_builder.add_node('coding_node',coding_node);
graph_builder.add_node('simple_node',simple_node);

graph_builder.add_edge(START,"classify_node");
graph_builder.add_conditional_edges("classify_node",route_node);
graph_builder.add_edge('simple_node',END);
graph_builder.add_edge('coding_node',END);


graph = graph_builder.compile()


while True:
    user = input("---->");
    
    _state:State= {
        "user_query":user,
        'coding_accuracy':None,
        "is_coding_question":None,
        "llm_response":None
    }
    
    
    response = graph.invoke(_state)
    
    print(response);