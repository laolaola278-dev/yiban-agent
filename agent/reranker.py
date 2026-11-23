"""二阶段精排：FAISS 召回 -> bge-reranker 精排 -> top-N 送大模型

装了 FlagEmbedding 才生效（pip install FlagEmbedding），否则自动降级为原始召回顺序。
开启方式：.env 里 USE_RERANK=1；召回/精排条数在 config.py 调。
"""
import config

_MODEL = None
_UNAVAILABLE = False

def _get_model():
    global _MODEL, _UNAVAILABLE
    if _UNAVAILABLE:
        return None
    if _MODEL is None:
        try:
            from FlagEmbedding import FlagReranker
            _MODEL = FlagReranker(config.RERANK_MODEL, use_fp16=False)
        except Exception as e:
            print("[reranker] 未安装或加载失败，降级为原始检索顺序：", str(e)[:100])
            _UNAVAILABLE = True
            return None
    return _MODEL

def rerank(query, hits, top_n=None):
    """hits: retriever.search 返回的 [{score,source,section,text}...]；
    返回精排后的 hits（按 rerank 分数降序），失败则原样返回前 top_n 条。"""
    n = top_n or config.RERANK_TOP_N
    model = _get_model()
    if model is None or not hits:
        return hits[:n]
    try:
        pairs = [[query, h["text"]] for h in hits]
        scores = model.compute_score(pairs)
        if hasattr(scores, "tolist"):
            scores = scores.tolist()
        for h, s in zip(hits, scores):
            h["rerank_score"] = round(float(s), 4)
        ranked = sorted(hits, key=lambda h: h.get("rerank_score", 0), reverse=True)
        return ranked[:n]
    except Exception as e:
        print("[reranker] 精排失败，降级：", str(e)[:100])
        return hits[:n]
