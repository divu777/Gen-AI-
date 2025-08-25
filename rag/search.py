# flake8: noqa
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

embeding = OpenAIEmbeddings(
    model='text-embedding-3-large'
)

# client = OpenAI(
#     base_url="https://router.huggingface.co/v1",
#     API_KEY=API_KEY
# )

client = OpenAI()


vector_db = QdrantVectorStore.from_existing_collection(
    collection_name='book',
    url='http://vectordb:6333',
    embedding=embeding
)

messages = []


while True:
    user_query = input("=====>")
    # vector similarity search
    search_results = vector_db.similarity_search(
        query=user_query
    )

    content = "\n\n".join(
        [f"Page Content: {result.page_content} \n Page Number: {result.metadata["page_label"]}\n File Source: {result.metadata["source"]}" for result in search_results])

    print(content+"------------>")
    SYSTEM_PROMPT = f'''
    #GOAL
    You are a helpful AI Agent that helps User with his queries regarding anything he might ask from the Context provided to you 

    #INSTRUCTIONS
    1) Always go through the context provided to you under the CONTEXT heading to get relevant information.
    2) Always provide user with the relevant answer with meta details like page number for better details.
    3) If no context is provided to you , reply with "Sorry the context provided was not enough for me to provide you with any answer right now" but with several variations of the same message 

    #CONTEXT
    {content}

'''

    messages.append({"role": "system", "content": SYSTEM_PROMPT})

    messages.append({"role": "user", "content": user_query})

    completion = client.chat.completions.create(
        model='gpt-4.1',
        messages=messages,
    )

    print(completion.choices[0].message.content)
    break


# have to make something like cursor , also have to make open app that has tools and the way to talk to tools and rag based on the pdf
