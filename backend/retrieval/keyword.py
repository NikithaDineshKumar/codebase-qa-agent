from rank_bm25 import BM25Okapi

def keyword_search(query: str, bm25_index: BM25Okapi, chunks: list[dict], top_k: int = 10) -> list[dict]:
    """
    Performs keyword search using BM25.
    Returns top_k chunks with their scores.
    """
    tokenized_query = query.lower().split()
    scores = bm25_index.get_scores(tokenized_query)

    # Get top_k indices sorted by score
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    results = []
    for rank, idx in enumerate(top_indices):
        if scores[idx] == 0:
            continue
        chunk = chunks[idx].copy()
        chunk["bm25_score"] = float(scores[idx])
        chunk["bm25_rank"] = rank + 1
        results.append(chunk)

    return results