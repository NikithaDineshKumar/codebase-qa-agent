def reciprocal_rank_fusion(
    semantic_results: list[dict],
    keyword_results: list[dict],
    top_k: int = 5,
    k: int = 60
) -> list[dict]:
    """
    Combines semantic and keyword search results using
    Reciprocal Rank Fusion (RRF).
    RRF score = 1 / (k + rank)
    Higher score = better result.
    """
    scores = {}
    chunk_map = {}

    # Score from semantic results
    for rank, chunk in enumerate(semantic_results):
        key = (chunk["file_path"], chunk["start_line"])
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        chunk_map[key] = chunk

    # Score from keyword results
    for rank, chunk in enumerate(keyword_results):
        key = (chunk["file_path"], chunk["start_line"])
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        chunk_map[key] = chunk

    # Sort by RRF score descending
    sorted_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    fused_results = []
    for key in sorted_keys[:top_k]:
        chunk = chunk_map[key].copy()
        chunk["rrf_score"] = round(scores[key], 6)
        fused_results.append(chunk)

    return fused_results