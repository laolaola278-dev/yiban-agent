# 重点插件用法片段 — 易班百事通智能体

> 所有路径相对项目根目录 `yiban-agent/`，Python ≥ 3.10。示例均可直接复制运行，挂载点已对齐现有文件 `backend_api.py`、`scripts/ingest.py` 与 kotaemon 前端。

---

## 1. ragas — 把「防幻觉」变成可量化的评测分数

**仓库**：https://github.com/vibrantlabsai/ragas　**许可**：Apache-2.0

```bash
pip install "ragas>=0.2" datasets
```

最小可运行示例（先用本地模型跑通，避免评测本身烧 DeepSeek 额度）：

```python
# scripts/eval_ragas.py
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

data = {
    "question":    ["高职单招的报名条件是什么？"],
    "answer":      ["考生须为应届高中毕业生……"],   # 来自 backend_api.py 的回答
    "contexts":    [["条款A原文……", "条款B原文……"]],  # 来自 FAISS 召回的条款级切片
    "ground_truth":["应届高中毕业生可报名……"],      # 人工标注的标准答案
}
ds = Dataset.from_dict(data)
result = evaluate(ds, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
print(result)
result.to_pandas().to_csv("eval_results/ragas.csv", index=False)
```

挂到本项目：在 `scripts/eval.py`（现有评测脚本）里 import 本文件的 `run_eval()`，把 `answer/contexts` 直接取自 `backend_api.py` 的 `format_reply()` 返回值和检索器返回的条款列表。建议评测时把 ragas 的 LLM 换成 OpenAI 兼容网关：`evaluate(..., llm=LangchainLLMWrapper(...))`，指向 `http://127.0.0.1:8010/v1`，这样_score 与线上同源。

## 2. FlagEmbedding / bge-reranker — 在召回后加二阶段精排

**仓库**：https://github.com/FlagOpen/FlagEmbedding　**许可**：MIT（本项目 bge-m3 同源）

```bash
pip install -U FlagEmbedding
```

把精排封装成统一函数，落点 `scripts/rerank.py`：

```python
# scripts/rerank.py
from FlagEmbedding import FlagReranker

_reranker = FlagReranker("BAAI/bge-reranker-base", use_fp16=True)  # CPU 可改 False

def rerank(query: str, chunks: list[str], top_k: int = 5) -> list[tuple[str, float]]:
    pairs = [[query, c] for c in chunks]
    scores = _reranker.compute_score(pairs, normalize=True)
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
```

挂到本项目：`scripts/ingest.py` 的检索阶段把 FAISS top-20 召回结果传给 `rerank()`，取 top-5 再交给 `backend_api.py` 的 `format_reply()` 组 prompt。这样引用溯源里显示的条款就是精排后的高相关条款，直接压低幻觉率。若部署机无 GPU，把模型换成 `BAAI/bge-reranker-base` 并设 `use_fp16=False`，或用下方 FlashRank 的纯 CPU 方案。

CPU 兜底（FlashRank）：

```bash
pip install flashrank
```
```python
from flashrank import Ranker, RerankRequest
ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="./model_cache")
hits = ranker.rerank(RerankRequest(query=q, passages=[{"id":i,"text":c} for i,c in enumerate(chunks)]))
top5 = [h["text"] for h in hits[:5]]
```

## 3. python-pptx — 把一次问答/评测自动导出成答辩页

**仓库**：https://github.com/scanny/python-pptx　**许可**：MIT

```bash
pip install python-pptx
```

最小可运行示例，落点 `scripts/export_answer_ppt.py`：

```python
# scripts/export_answer_ppt.py
from pptx import Presentation
from pptx.util import Inches, Pt

def export(qa_list: list[dict], out="答辩演示.pptx"):
    prs = Presentation()
    for item in qa_list:               # item = {question, answer, citations}
        slide = prs.slides.add_slide(prs.slide_layouts[1])  # 标题+正文
        slide.shapes.title.text = item["question"]
        body = slide.placeholders[1].text_frame
        body.text = item["answer"]
        for line in item["citations"]:  # 引用溯源逐条列出
            p = body.add_paragraph()
            p.text = "· " + line
            p.level = 1
    prs.save(out)
```

挂到本项目：`qa_list` 由 `scripts/eval.py` 的测试集问答 + `backend_api.py` 返回的 `citations` 字段组装。答辩前跑一次，把「典型问题 + 模型回答 + 引用条款」批量生成幻灯片，和 `zouchenzhen/thesis-defense-pptx-skill` 的中文模板合并即可定稿。

## 4. Opik — 给问答链路加 trace，答辩现场可展示

**仓库**：https://github.com/comet-ml/opik　**许可**：Apache-2.0

```bash
pip install opik
opik configure   # 填自托管地址；无服务时可用本地模式
```
```python
# backend_api.py
from opik import track

@track(name="rag_query")
def format_reply(question: str, contexts: list[str]) -> str:
    ...  # 现有逻辑不动
    return answer
```

挂到本项目：只加装饰器，不改业务逻辑。每次问答自动记录 question / contexts / answer / 耗时，Opik UI 里按 trace 查看「检索→精排→生成」各段耗时，作为答辩「系统可观测性」的证据页。

## 5. promptfoo — 提示词/网关回归测试

**仓库**：https://github.com/promptfoo/promptfoo　**许可**：MIT

```bash
npx promptfoo@latest init   # 生成 promptfooconfig.yaml
npx promptfoo eval
```

```yaml
# promptfooconfig.yaml
providers:
  - id: http://127.0.0.1:8010/v1
    config:
      model: deepseek-chat
prompts:
  - "请回答：{{question}}"
tests:
  - vars: {question: "学费是多少？"}
    assert:
      - type: contains
        value: "元"
```

挂到本项目：把现有 20 条测试问答写进 `tests:`，每次改意图路由或澄清追问提示词后跑 `npx promptfoo eval`，防止改 A 功能破坏 B 功能。

## 6. gradio-pdf — 引用溯源可视化

**仓库**：https://github.com/freddyaboulton/gradio-pdf　**许可**：MIT

```bash
pip install gradio-pdf
```
```python
import gradio as gr
from gradio_pdf import PDF

with gr.Blocks() as demo:
    with gr.Row():
        ans = gr.Textbox(label="智能体回答")
        src = PDF(label="命中条款原文", height=600)
```

挂到本项目：在 kotaemon 前端（Gradio 4.44）的回复区旁边加 `PDF()` 组件，`src.value` 绑定检索器命中的原始 PDF 条款页路径，评委可边看回答边翻原文，引用溯源从文字变成可交互证据。

## 7. mermaid-py / termaid — 架构图随代码更新

**仓库**：https://github.com/ouhammmourachid/mermaid-py 、https://github.com/fasouto/termaid　**许可**：MIT

```bash
pip install mermaid-py termaid
```
```python
import mermaid as md
g = md.graph("graph LR; A[FAISS召回] --> B[bge-reranker精排] --> C[DeepSeek生成] --> D[引用溯源]")
g.save("docs/rag_flow.svg")
```

挂到本项目：把 RAG 链路、意图路由、防幻觉兜底三张图写成 Python 常量，`docs/` 自动生成 svg，README 与答辩 PPT 直接引用，避免手绘图与实现不一致。

---

> 依赖冲突提示：ragas 与 opik 对 `langchain` 版本敏感，建议用同一个 venv 并在 `requirements-rag-eval.txt` 单独锁定评测依赖；开发/答辩环境用 CPU 时优先 FlashRank + bge-reranker-base(use_fp16=False) 组合。