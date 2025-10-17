from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import redis
import json
from datetime import datetime

# ------------------ Import your modules ------------------
from run_redis import enqueue_url
from get_response import get_response

# ------------------ Redis Setup ------------------
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
FAISS_FILE = "faiss_index.idx"

# ------------------ FastAPI Init ------------------
app = FastAPI(
    title="RAG + Redis URL Pipeline API",
    description="API for ingesting URLs and querying knowledge via RAG",
    version="1.0.0"
)

# ------------------ Request Models ------------------
class URLRequest(BaseModel):
    urls: List[str]

class QueryRequest(BaseModel):
    query: str

# ------------------ API Endpoints ------------------

@app.post("/ingest_url")
def ingest_url(request: URLRequest):
    """
    Enqueue one or more URLs into the Redis queue.
    """
    try:
        for url in request.urls:
            enqueue_url(url)
        return {"message": f"✅ {len(request.urls)} URLs enqueued successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_endpoint(request: QueryRequest):
    """
    Generate a response to the user query using the RAG pipeline.
    """
    print(f"🔍 Received query: {request.query}")
    response = get_response(request.query)
    return {"query": request.query, "response": response}

# ------------------ Health Check ------------------
@app.get("/")
def root():
    return {"message": "RAG + Redis API is running 🚀"}
