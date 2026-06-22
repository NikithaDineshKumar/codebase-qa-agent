import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from ingestion.cloner import clone_repo
from ingestion.parser import parse_repo
from ingestion.indexer import build_index, load_index
from retrieval.semantic import semantic_search
from retrieval.keyword import keyword_search
from retrieval.fusion import reciprocal_rank_fusion
from generation.answer import generate_answer

load_dotenv()

app = FastAPI(title="Codebase Q&A Agent", version="1.0.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for loaded indexes
index_store = {
    "faiss_index": None,
    "bm25_index": None,
    "chunks": None,
    "repo_url": None,
}

# ---------- Request Models ----------

class IngestRequest(BaseModel):
    github_url: str

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

# ---------- Routes ----------

@app.get("/")
def root():
    return {"message": "Codebase Q&A Agent is running"}


@app.post("/ingest")
def ingest_repo(request: IngestRequest):
    """
    Clones a GitHub repo, parses it with AST,
    builds FAISS + BM25 indexes.
    """
    try:
        # Clone repo
        repo_path = clone_repo(request.github_url)

        # Parse repo into chunks
        chunks = parse_repo(repo_path)

        if not chunks:
            raise HTTPException(status_code=400, detail="No code chunks found in repo")

        # Build indexes
        metadata = build_index(chunks)

        # Load into memory
        faiss_index, bm25_index, chunks = load_index()
        index_store["faiss_index"] = faiss_index
        index_store["bm25_index"] = bm25_index
        index_store["chunks"] = chunks
        index_store["repo_url"] = request.github_url

        return {
            "status": "success",
            "repo_url": request.github_url,
            "total_chunks": metadata["total_chunks"],
            "message": f"Successfully indexed {metadata['total_chunks']} code chunks",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query_codebase(request: QueryRequest):
    """
    Answers a natural language question about the indexed codebase.
    Uses hybrid retrieval (FAISS + BM25) with RRF fusion.
    """
    if index_store["faiss_index"] is None:
        raise HTTPException(status_code=400, detail="No repo indexed yet. Please call /ingest first.")

    try:
        # Hybrid retrieval
        semantic_results = semantic_search(
            request.question,
            index_store["faiss_index"],
            index_store["chunks"],
            top_k=10,
        )

        keyword_results = keyword_search(
            request.question,
            index_store["bm25_index"],
            index_store["chunks"],
            top_k=10,
        )

        # RRF fusion
        fused_results = reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            top_k=request.top_k,
        )

        # Generate answer
        result = generate_answer(request.question, fused_results)

        return {
            "status": "success",
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"],
            "total_chunks_used": result["total_chunks_used"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
def get_status():
    """Returns current index status."""
    return {
        "indexed": index_store["faiss_index"] is not None,
        "repo_url": index_store["repo_url"],
        "total_chunks": len(index_store["chunks"]) if index_store["chunks"] else 0,
    }