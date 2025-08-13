from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

# path of the book
bookPath = Path(__file__).parent/"book.pdf"

loader = PyPDFLoader(file_path=bookPath)
docs = loader.load()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

split_docs = text_splitter.split_documents(documents=docs)

embedding = OpenAIEmbeddings(model='text-embedding-3-large')

vectorDB = QdrantVectorStore(
    collection_name='book_queue',
    documents=split_docs,
    embedding=embedding,
    url="http://vectordb:6333"
)