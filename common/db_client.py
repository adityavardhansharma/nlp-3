import os, json, chromadb
from chromadb.api.types import EmbeddingFunction
from sentence_transformers import SentenceTransformer
from common.config import CHROMA_DIR, BI_ENCODER_MODEL

class STEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model: SentenceTransformer):
        self.model = model
    def __call__(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True)

class DBClient:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            os.makedirs(CHROMA_DIR, exist_ok=True)
            cls._instance.client = chromadb.PersistentClient(path=CHROMA_DIR)
            cls._instance.embedder = SentenceTransformer(BI_ENCODER_MODEL)
        return cls._instance

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=STEmbeddingFunction(self.embedder),
        )

    def ingest_jsonl(self, path: str, name: str, document_field="instruction"):
        col = self.get_or_create_collection(name)
        if col.count() > 0:
            return col
        ids, docs, metas = [], [], []
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                obj = None
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                doc = obj.get(document_field)
                if not doc:
                    continue
                meta = {}
                for k, v in obj.items():
                    if k == "response":
                        meta["answer"] = v
                    elif k == "common_misspellings":
                        continue
                    else:
                        meta[k] = v if isinstance(v, (str, int, float, bool, list)) or v is None else str(v)
                # preserve common_misspellings as JSON string
                raw = obj.get("common_misspellings", {})
                meta["common_misspellings"] = json.dumps(raw, ensure_ascii=False)
                ids.append(str(i))
                docs.append(doc)
                metas.append(meta)
        if ids:
            col.add(ids=ids, documents=docs, metadatas=metas)
        return col

    def list_collections(self):
        return [c.name for c in self.client.list_collections()]
