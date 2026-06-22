import os
import pickle
import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# Load embedding model once
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings(texts: list[str]) -> np.ndarray:
    """Generate embeddings for a list of texts."""
    embeddings = EMBEDDING_MODEL.encode(texts, show_progress_bar=True)
    return np.array(embeddings).astype("float32")

def build_index(chunks: list[dict], index_dir: str = "indexes") -> dict:
    """
    Builds FAISS vector index and BM25 keyword index from chunks.
    Saves both indexes to disk.
    Returns index metadata.
    """
    os.makedirs(index_dir, exist_ok=True)

    texts = [chunk["content"] for chunk in chunks]

    print("Building FAISS index...")
    embeddings = get_embeddings(texts)
    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)

    print("Building BM25 index...")
    tokenized_texts = [text.lower().split() for text in texts]
    bm25_index = BM25Okapi(tokenized_texts)

    # Save indexes
    faiss.write_index(faiss_index, os.path.join(index_dir, "faiss.index"))

    with open(os.path.join(index_dir, "bm25.pkl"), "wb") as f:
        pickle.dump(bm25_index, f)

    with open(os.path.join(index_dir, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"Indexes saved to {index_dir}/")
    print(f"Total indexed chunks: {len(chunks)}")

    return {
        "total_chunks": len(chunks),
        "index_dir": index_dir,
        "dimension": dimension,
    }


def load_index(index_dir: str = "indexes") -> tuple:
    """
    Loads FAISS index, BM25 index, and chunks from disk.
    Returns (faiss_index, bm25_index, chunks)
    """
    faiss_index = faiss.read_index(os.path.join(index_dir, "faiss.index"))

    with open(os.path.join(index_dir, "bm25.pkl"), "rb") as f:
        bm25_index = pickle.load(f)

    with open(os.path.join(index_dir, "chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)

    return faiss_index, bm25_index, chunks