import os
import sys

# ensure project root on PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.db_client import DBClient

db = DBClient()

def list_collections() -> list[str]:
    """All Chroma collection names."""
    return db.list_collections()

def get_collection_stats(coll_name: str) -> dict:
    """Return total count and embedding dimension."""
    col = db.get_or_create_collection(coll_name)
    cnt = col.count()
    dim = None
    try:
        sample = col.get(limit=1, include=["embeddings"])
        emb = sample.get("embeddings", [[]])[0][0]
        # list or numpy array
        dim = len(emb) if hasattr(emb, "__len__") else getattr(emb, "shape", [None])[0]
    except Exception:
        pass
    return {"count": cnt, "dimensions": dim}

def get_all_records(
    coll_name: str,
    page: int = 1,
    limit: int = 10,
    filters=None,
    include_fields=None
) -> dict:
    """
    Paginate through documents in `coll_name`.
    include_fields may include "documents","metadatas","embeddings", etc.
    """
    col = db.get_or_create_collection(coll_name)
    total = col.count()

    # sanitize page/limit
    page = max(1, page)
    limit = max(1, limit)
    offset = (page - 1) * limit

    # default to docs+meta if nothing specified
    if not include_fields:
        include_fields = ["documents", "metadatas"]
    # remove any unsupported includes
    safe_inc = [f for f in include_fields if f not in ("uris", "data")]

    # fetch exactly this page
    data = col.get(
        limit=limit,
        offset=offset,
        include=safe_inc
    )

    docs = data.get("documents", [])
    metas = data.get("metadatas", [])
    embs = data.get("embeddings", [])

    records = []
    for idx, doc in enumerate(docs):
        rec = {"id": offset + idx}

        if "documents" in safe_inc:
            rec["document"] = doc

        if "metadatas" in safe_inc and idx < len(metas):
            md = metas[idx]
            rec["metadata"] = md
            if isinstance(md, dict) and "answer" in md:
                rec["answer"] = md["answer"]

        if "embeddings" in safe_inc and idx < len(embs):
            emb = embs[idx]
            # numpy → list, list stays list
            rec["embedding"] = emb.tolist() if hasattr(emb, "tolist") else emb

        records.append(rec)

    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        "records": records,
        "page": page,
        "total_pages": total_pages,
        "total_records": total,
        "limit": limit,
        "included_fields": safe_inc
    }

def search_by_similarity(
    coll_name: str,
    query: str,
    limit: int = 5,
    include_fields=None
) -> dict:
    """
    Semantic‐search `query` in `coll_name`, return docs, metas, distances.
    """
    col = db.get_or_create_collection(coll_name)

    if not include_fields:
        include_fields = ["documents", "metadatas", "distances"]
    safe_inc = [f for f in include_fields if f not in ("uris", "data")]
    if "distances" not in safe_inc:
        safe_inc.append("distances")

    res = col.query(
        query_texts=[query],
        n_results=int(limit),
        include=safe_inc
    )

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    ids   = res.get("ids", [[]])[0]

    results = []
    for i, doc in enumerate(docs):
        item = {
            "id": ids[i] if ids else i,
            "document": doc,
            "distance": dists[i],
            "score": 1.0 - float(dists[i])
        }
        if metas and i < len(metas):
            md = metas[i]
            item["metadata"] = md
            if "answer" in md:
                item["answer"] = md["answer"]
        results.append(item)

    return {
        "query": query,
        "results": results,
        "count": len(results),
        "included_fields": safe_inc
    }
