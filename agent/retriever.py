"""检索器：FAISS 余弦检索（向量已归一化，内积即余弦）"""
import json
import faiss
import numpy as np
from config import CORPUS_PATH, VECTOR_PATH
from .llm import embed

class Retriever:
    def __init__(self):
        if not (CORPUS_PATH.exists() and VECTOR_PATH.exists()):
            raise RuntimeError("知识库为空：请先把学校文件放入 data/raw，再运行 python scripts/ingest.py")
        self.chunks = [
            json.loads(line)
            for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.vectors = np.load(str(VECTOR_PATH))
        self.index = faiss.IndexFlatIP(self.vectors.shape[1])
        self.index.add(self.vectors)

    def search(self, query, k=8):
        if not self.chunks:
            return []
        qv = embed([query])
        k = min(k, len(self.chunks))
        scores, ids = self.index.search(qv, k)
        hits = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            chunk = self.chunks[int(idx)]
            hits.append({
                "score": float(score),
                "id": chunk["id"],
                "source": chunk["source"],
                "section": chunk.get("section", ""),
                "text": chunk["text"],
            })
        return hits
