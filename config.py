"""全局配置：模型、路径、检索参数"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ---------- 对话模型 ----------
CHAT_API_KEY = os.getenv("CHAT_API_KEY", "")
CHAT_BASE_URL = os.getenv("CHAT_BASE_URL", "https://api.deepseek.com")
CHAT_MODEL = os.getenv("CHAT_MODEL", "deepseek-chat")

# ---------- 向量模型 ----------
EMBED_API_KEY = os.getenv("EMBED_API_KEY", "")
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "https://api.siliconflow.cn/v1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = int(os.getenv("EMBED_DIM", "1024"))

# ---------- 路径 ----------
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CORPUS_PATH = DATA_DIR / "corpus" / "corpus.jsonl"
VECTOR_PATH = DATA_DIR / "corpus" / "vectors.npy"
CALENDAR_PATH = DATA_DIR / "calendar.json"
TESTSET_PATH = BASE_DIR / "eval" / "testset.jsonl"

# ---------- 检索参数 ----------
TOP_K = 8                # 召回条数
SCORE_THRESHOLD = 0.40   # 余弦相似度低于该值视为知识库未覆盖 -> 兜底
CHUNK_MIN = 300          # 切片最小字符数
CHUNK_MAX = 600          # 切片最大字符数

# ---------- 二阶段精排（FlagEmbedding/bge-reranker，可选）----------
USE_RERANK = os.getenv("USE_RERANK", "0") == "1"   # .env 里设 USE_RERANK=1 开启
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
RETRIEVE_TOP_K = 20      # 召回条数（精排前）
RERANK_TOP_N = 5         # 精排后送给大模型的条数
