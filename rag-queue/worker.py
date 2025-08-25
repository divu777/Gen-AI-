# flake8: noqa
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAI
import json
embedding = OpenAIEmbeddings(model='text-embedding-3-large')

vectordb= QdrantVectorStore.from_existing_collection(    
    collection_name='book_queue',
    embedding=embedding,
    url='http://vectordb:6333'
) 

client  = OpenAI()


def handle_query(query: str):
    print("This is your query "+query+"\n\n\n");
    similiar_docs = vectordb.similarity_search(query=query);
    messages=[]

    SYSTEM_PROMPT= '''
    #IDENTITY
    You are Agentic Helper of User, you help user solve there query based on the Context Provided to you and help user navigate to that page for further knowledge.
    
    #INSTRUCTION
    1. Always Read the avalible Context for better framing of the answer under the Context heading.
    2. You should Always Respond from the Context provided to you, nothing from your own knowledge.
    3. If you are not able to find the answer based on the user query, reply with I don't have enough context to Help you write now. Also changing this response so it does not get repetative
    
    #CONTEXT
    Here is the Related Documents Context Provided to you. 
    {similiar_docs}
    
    #OUTPUT FORMAT
    INPUT - What is the FS module?.
    OUTPUT - {{"output":"FS module is the file system module that is provided in javascript to read and write information synchornously and asynchronously."}}
    
    INPUT - what is my name?
    OUTPUT - {{"output":"I am sorry, i can't help you with this query because it does not come under my knowledge scope.}}
    
    **IMPORTANT**
    Always return output in valid JSON , no markdown , no xml and triple backslashes    
    '''
    
    messages.append({"role":"system","content":SYSTEM_PROMPT})
    
    messages.append({"role":"user","content":query});
    
    completion = client.chat.completion.create(
        model='gpt-4o',
        messages=messages,
        response_format = {"type":"json_object"}
    )
    
    response = completion.choices[0].message.content
     
    response_object = json.load(response);
    
    if(response_object["output"]):
        print(response_object["output"])
    