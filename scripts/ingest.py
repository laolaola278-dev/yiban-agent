"""文档入库：解析(pdf/docx/txt/md) -> 切片 -> 向量化 -> 落盘 corpus.jsonl + vectors.npy"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pdfplumber
from docx import Document

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from config import RAW_DIR, CORPUS_PATH, VECTOR_PATH, CHUNK_MIN, CHUNK_MAX
from agent.llm import embed

HEAD_RE = re.compile(r"^([一二三四五六七八九十]+、|\d+(\.\d+)+|[（(][一二三四五六七八九十]+[)）])")

def iter_paras_docx(path):
    doc = Document(str(path))
    section = ""
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        name = getattr(p.style, "name", "") or ""
        if name.startswith("Heading") or name == "Title" or HEAD_RE.match(t):
            section = t
        yield t, section

def iter_paras_pdf(path):
    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            txt = page.extract_text() or ""
            for line in txt.split("\n"):
                para = line.strip()
                if para:
                    yield para, "第{}页".format(i)

def iter_paras_txt(path):
    txt = path.read_text(encoding="utf-8", errors="ignore")
    section = ""
    for line in txt.split("\n"):
        para = line.strip()
        if not para:
            continue
        if HEAD_RE.match(para):
            section = para
        yield para, section

ITERS = {
    ".docx": iter_paras_docx,
    ".pdf": iter_paras_pdf,
    ".txt": iter_paras_txt,
    ".md": iter_paras_txt,
}

def chunk_file(path):
    ext = path.suffix.lower()
    if ext not in ITERS:
        return []
    buf, buf_src, chunks = "", "", []
    for para, section in ITERS[ext](path):
        if buf and (section != buf_src or len(buf) + len(para) > CHUNK_MAX):
            chunks.append({"text": buf, "section": buf_src})
            buf = ""
        if not buf:
            buf_src = section
        buf = (buf + "\n" + para).strip()
        if len(buf) >= CHUNK_MIN:
            chunks.append({"text": buf, "section": buf_src})
            buf = ""
    if buf:
        chunks.append({"text": buf, "section": buf_src})
    for c in chunks:
        c["source"] = path.name
    return chunks

def main():
    CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    files = [f for f in sorted(RAW_DIR.rglob("*"))
             if f.is_file() and f.suffix.lower() in ITERS]
    chunks = []
    for f in files:
        cs = chunk_file(f)
        chunks.extend(cs)
        print("{} -> {} 片".format(f.name, len(cs)))
    if not chunks:
        print("data/raw 下没有可用文档（支持 pdf/docx/txt/md），请先放入文件。")
        return
    print("向量化中，共 {} 片...".format(len(chunks)))
    vecs = embed([c["text"] for c in chunks])
    np.save(str(VECTOR_PATH), vecs)
    with open(CORPUS_PATH, "w", encoding="utf-8") as out:
        for i, c in enumerate(chunks):
            out.write(json.dumps({"id": i, **c}, ensure_ascii=False) + "\n")
    print("完成：{} 个切片，向量维度 {}。输出：{} 与 {}".format(
        len(chunks), vecs.shape[1], CORPUS_PATH.name, VECTOR_PATH.name))

if __name__ == "__main__":
    main()
