"""模型封装：对话模型 + 向量模型（OpenAI 兼容接口）"""
import numpy as np
from openai import OpenAI
from config import (
    CHAT_API_KEY, CHAT_BASE_URL, CHAT_MODEL,
    EMBED_API_KEY, EMBED_BASE_URL, EMBED_MODEL,
)

_chat_client = None
_embed_client = None

def _chat():
    global _chat_client
    if _chat_client is None:
        if not CHAT_API_KEY:
            raise RuntimeError("请复制 .env.example 为 .env，并填写 CHAT_API_KEY")
        _chat_client = OpenAI(api_key=CHAT_API_KEY, base_url=CHAT_BASE_URL)
    return _chat_client

def _embed():
    global _embed_client
    if _embed_client is None:
        if not EMBED_API_KEY:
            raise RuntimeError("请复制 .env.example 为 .env，并填写 EMBED_API_KEY")
        _embed_client = OpenAI(api_key=EMBED_API_KEY, base_url=EMBED_BASE_URL)
    return _embed_client

def chat(messages, temperature=0.3, response_json=False):
    kwargs = dict(model=CHAT_MODEL, messages=messages, temperature=temperature)
    if response_json:
        kwargs["response_format"] = {"type": "json_object"}
    resp = _chat().chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""

def embed(texts, batch_size=32):
    """批量向量化；返回 L2 归一化 float32 矩阵（归一化后内积即余弦相似度）"""
    vecs = []
    for i in range(0, len(texts), batch_size):
        batch = [t[:4000] for t in texts[i:i + batch_size]]
        resp = _embed().embeddings.create(model=EMBED_MODEL, input=batch)
        vecs.extend(d.embedding for d in resp.data)
    arr = np.array(vecs, dtype="float32")
    arr /= (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-8)
    return arr
