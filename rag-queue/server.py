from fastapi import FastAPI, Query
from .connection import queue
from .worker import handle_query
app = FastAPI()


@app.get("/")
def root():
    return {"hello": "mihika"}


@app.get("/query")
def query_chat(query: str = Query(..., description="Chat Message")):
    jobid = queue.enqueue(handle_query, query)
    return {
        "quer": query,
        "jobid": jobid.id
        }
    
