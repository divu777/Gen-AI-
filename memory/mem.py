# flake8: noqa
from mem0 import Memory
import os 
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 

config = {
    "version": "v1.1",
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4.1", "api_key": OPENAI_API_KEY}
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "api_key": OPENAI_API_KEY
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "vectordb",
            "port": "6333"
        }
    },
    "graph_store":{
        "provider":"neo4j",
        "config":{
            "url":"bolt://neo4j:7687",
            "username":"neo4j",
            "password":"divakar-jaiswal-6S3dkjnsdfsdj243424#$%%sdjdj"
        }
    }
}
messages=[]
mem_client = Memory.from_config(config)


while True:
    user_query = input("---->")

    related_memeoris = mem_client.search(query=user_query,user_id='divakar')
    print(related_memeoris)
    
    memeories = [f"ID: {mem.get("id")}, Memories: {mem.get("memory")} " for mem in related_memeoris.get("results")]
    print(memeories)

    SYSTEM_PROMPT = F'''
        So you are a powerfull helping agent , you provide insightful answers to user based on the query and past memories related 
        to them. 
        
        PAST MEMORIES
        {related_memeoris}
        '''

    messages.append({'role':"system","content":SYSTEM_PROMPT})
    messages.append({"role":"user","content":user_query})

    response = client.chat.completions.create(
        model='gpt-4.1',
        messages=messages
    )

    print(response.choices[0].message.content);

    mem_client.add(messages=[*messages,{"role":"assistant","content":response.choices[0].message.content}],user_id='divakar')


