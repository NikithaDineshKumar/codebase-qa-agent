import numpy as np
import faiss
from ingestion.indexer import EMBEDDING_MODEL

def semantic_search(query: str, faiss_index: faiss.Index, chunks: list[dict], top_k: int = 10) -> list[dict]:
    """
    Performs semantic search using FAISS.
    Returns top_k chunks with their scores.
    """
    query_embedding = EMBEDDING_MODEL.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = faiss_index.search(query_embedding, top_k)

    results = []
    for rank, (idx, distance) in enumerate(zip(indices[0], distances[0])):
        if idx == -1:
            continue
        chunk = chunks[idx].copy()
        chunk["semantic_score"] = float(1 / (1 + distance))
        chunk["semantic_rank"] = rank + 1
        results.append(chunk)

    return results