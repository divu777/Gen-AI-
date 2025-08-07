from dotenv import load_dotenv
import os
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from pathlib import Path
load_dotenv()

API_KEY= os.getenv("API_KEY");

client  = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_KEY
)

print(__file__)
file_path  = Path(__file__).parent / "book.pdf"

loader = PyPDFLoader(file_path=file_path)


docs = loader.load()

# chunking of text
text_split = RecursiveCharacterTextSplitter(chunk_size=1000,
    chunk_overlap=400)

split_docs = text_split.split_documents(documents=docs)



#embedding 

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

##vector db 

qdrant  = QdrantVectorStore.from_documents(
    documents=split_docs,
    collection_name = 'book',
    embedding=embeddings,
    url = "http://localhost:6333"
)   

print("Done with indexing the doc")