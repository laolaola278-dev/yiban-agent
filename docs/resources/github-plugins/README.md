# GitHub 插件采集清单 — 易班百事通智能体

> 采集时间：2026-11-18　|　数据源：GitHub Search / Repos API　|　原始 JSON：`raw_github_data.json`

## 按本项目现状的推荐结论

本项目已有「FAISS + bge-m3 + DeepSeek + OpenAI 兼容网关 + kotaemon/Gradio」完整链路，**缺口在评测量化、精排提效、答辩 PPT 三处**。因此最高优先级是 ① `ragas`（把防幻觉做成可量化的评测分数）② `FlagEmbedding/bge-reranker`（在现有召回后加二阶段精排，直接提升引用命中率）③ `python-pptx` 生态（把问答与评测自动导出成答辩材料）。可视化与 kotaemon 主题类作为体验加分备选。下表按「最推荐 → 备选」排序，同组内亦按推荐度排列。

筛选口径：star 高或明显对口 + 近 12 个月内有更新（个别稳定基础库除外并已标注）+ 许可明确（MIT/Apache 优先）+ 可直接配合 Python / OpenAI 兼容 / Gradio / pptx 技术栈。

## 一、RAG 评测与可观测（答辩硬指标，最高优先级）

| 名称 | GitHub 直链 | Star 数 | 语言 | 许可 | 最近更新 | 本项目怎么用（步骤 / 挂载点） |
|---|---|---:|---|---|---|---|
| ragas | [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas) | 16,361 | Python | Apache-2.0 | 2026-11-14 | 装 pip install ragas。新建 scripts/eval_ragas.py：从 backend_api.py 的检索+DeepSeek 生成结果构造 Dataset(question/answer/contexts/ground_truth)，evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])。把输出写进现有评测脚本的汇总表，作为防幻觉兜底的量化证据。 |
| opik | [comet-ml/opik](https://github.com/comet-ml/opik) | 23,448 | Java(Python SDK) | Apache-2.0 | 2026-11-18 | pip install opik，opik configure 填本地/自托管地址。在 backend_api.py 的 format_reply 与检索函数上加 @track(name="rag_query")，自动记录每次问答的 query、召回 contexts、DeepSeek 回答与耗时；用 Opik UI 出评测看板，答辩现场展示 trace 链路。 |
| promptfoo | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 27,401 | TypeScript | MIT | 2026-11-18 | npx promptfoo init 生成 promptfooconfig.yaml，providers 指向 http://127.0.0.1:8010/v1（OpenAI 兼容网关），assert 里写 RAG 断言与相似度阈值；npx promptfoo eval 批量回归意图路由与澄清追问的提示词改动。 |
| evalscope | [modelscope/evalscope](https://github.com/modelscope/evalscope) | 3,710 | Python | Apache-2.0 | 2026-11-18 | pip install evalscope。用其自定义数据集评测 bge-m3 / DeepSeek 兼容端点，跑出中文语义与生成质量分数；与 ragas 结果并列放进答辩「评测」页，强调中文场景覆盖。 |
| RagaAI-Catalyst | [raga-ai-hub/RagaAI-Catalyst](https://github.com/raga-ai-hub/RagaAI-Catalyst) | 16,191 | Python | Apache-2.0 | 2026-02-11 | pip install ragaai-catalyst，接入现有 FAISS 检索器做离线 RAG 评测；其预置的 context adherence / toxicity 指标可直接复用，CI 里定时跑并保存报告。 |

## 二、Rerank 精排（直接提升引用溯源质量）

| 名称 | GitHub 直链 | Star 数 | 语言 | 许可 | 最近更新 | 本项目怎么用（步骤 / 挂载点） |
|---|---|---:|---|---|---|---|
| FlagEmbedding | [FlagOpen/FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) | 12,344 | Python | MIT | 2026-10-27 | 本项目的 bge-m3 就出自该仓库，直接 pip install -U FlagEmbedding。在检索链路里加二阶段精排：FAISS/bge-m3 召回 top-20 → FlagReranker("BAAI/bge-reranker-base", use_fp16=True).compute_score([[q,c]...]) → 取 top-5 再送 DeepSeek。落点 scripts/ingest.py 新增 rerank() 并由 backend_api.py 调用，可显著降幻觉、提升引用命中率。 |
| sentence-transformers | [huggingface/sentence-transformers](https://github.com/huggingface/sentence-transformers) | 19,291 | Python | Apache-2.0 | 2026-11-17 | pip install sentence-transformers。CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2").predict([(q,c),...]) 做轻量精排，CPU 也能跑；作为 FlagReranker 的备选实现，封装成统一的 rerank.py 接口方便切换。 |
| infinity | [michaelfeil/infinity](https://github.com/michaelfeil/infinity) | 2,988 | C++ | MIT | 2026-11-12 | pip install infinity 或 docker 起 infinity_emb --model BAAI/bge-reranker-base，它原生暴露 OpenAI 兼容的 /v1/rerank 与 /v1/embeddings；让 backend_api.py 通过现有 OpenAI 兼容客户端直接调用，把精排独立成服务，答辩时可单独演示吞吐。 |
| rerankers | [AnswerDotAI/rerankers](https://github.com/AnswerDotAI/rerankers) | 1,643 | Python | Apache-2.0 | 2025-12-20 | pip install rerankers。一行 Reranker("bge-reranker-v2-m3").rank(q, docs, k=5) 统一多种后端，适合在 scripts/ingest.py 做 A/B 对比不同 rerank 模型对引用溯源的影响。 |
| FlashRank | [PrithivirajDamodaran/FlashRank](https://github.com/PrithivirajDamodaran/FlashRank) | 1,016 | Python | Apache-2.0 | 2026-07-11 | pip install flashrank，Ranker(model_name="ms-marco-MiniLM-L-12-v2").rerank(RerankRequest(query=q, passages=docs))。纯 CPU 毫秒级，作为无 GPU 答辩环境的兜底精排方案。 |
| fastembed | [qdrant/fastembed](https://github.com/qdrant/fastembed) | 3,301 | Python | Apache-2.0 | 2026-11-17 | pip install fastembed。TextEmbedding / TextCrossEncoder 本地推理，可替换 bge-m3 的 embedding 步骤做轻量基线对比，接口简洁便于写进实验对照页。 |

## 三、PPT / 答辩材料自动化

| 名称 | GitHub 直链 | Star 数 | 语言 | 许可 | 最近更新 | 本项目怎么用（步骤 / 挂载点） |
|---|---|---:|---|---|---|---|
| ppt-master | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | 78,050 | Python | MIT | 2026-11-17 | MIT、Python、近期极活跃。按其 README 起服务，输入「易班百事通项目介绍/技术架构/创新点/评测结果」大纲一键生成 pptx；生成后用 python-pptx 二次替换校徽、配色与参赛 Logo，作为答辩初稿提效。 |
| python-pptx | [scanny/python-pptx](https://github.com/scanny/python-pptx) | 3,590 | Python | MIT | 2024-08-07 | pip install python-pptx（事实标准库，更新慢但 API 稳定）。新建 scripts/export_answer_ppt.py：Presentation() 逐页写入「问题 / 命中条款 / 引用来源 / 回答」，把 backend_api.py 的一次问答自动导出成答辩演示页；注意它最后 push 于 2024-08，属稳定为王的基础依赖。 |
| Office-PowerPoint-MCP-Server | [GongRzhe/Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server) | 1,863 | Python | MIT | 2025-12-31 | MIT、Python。作为 MCP Server 接进 Agent，让智能体在对话里直接「生成答辩 PPT」；若后续把 kotaemon 换成本地 Agent，这是最低成本的 PPT 工具挂载方案。 |
| thesis-defense-pptx-skill | [zouchenzhen/thesis-defense-pptx-skill](https://github.com/zouchenzhen/thesis-defense-pptx-skill) | 282 | Python | Apache-2.0 | 2026-11-09 | Apache-2.0、Python、2026-11 更新，专做答辩 PPT 模板。直接复用其版式与 python-pptx 模板变量，把项目背景/技术栈/评测数据填进去，产出符合中文答辩审美的定稿。 |
| GordenPPTSkill | [GordenSun/GordenPPTSkill](https://github.com/GordenSun/GordenPPTSkill) | 4,148 | Python | NOASSERTION | 2026-06-22 | PPT 生成技能仓库，star 高、2026-06 更新；许可为 NOASSERTION，落地前按其 LICENSE 文件确认再集成。可作为「大纲→幻灯片」的参考实现，复制其提示词结构与分页逻辑到本项目的答辩材料生成脚本。 |

## 四、可视化与前端增强

| 名称 | GitHub 直链 | Star 数 | 语言 | 许可 | 最近更新 | 本项目怎么用（步骤 / 挂载点） |
|---|---|---:|---|---|---|---|
| gradio-pdf | [freddyaboulton/gradio-pdf](https://github.com/freddyaboulton/gradio-pdf) | 45 | JavaScript | MIT | 2025-11-26 | pip install gradio-pdf。在 kotaemon 前端(Gradio 4.44)里加一个 PDF 查看组件，side-by-side 展示「回答」与「命中的原始条款 PDF 页」，把引用溯源做成可视化亮点，评委一眼看到依据。 |
| termaid | [fasouto/termaid](https://github.com/fasouto/termaid) | 583 | Python | MIT | 2026-11-18 | pip install termaid。把 RAG 架构图、意图路由流程图用 Mermaid 维护，termaid 在终端实时渲染校验；生成的 .mmd 可嵌入 README 与答辩 PPT，避免手绘图。 |
| mermaid-py | [ouhammmourachid/mermaid-py](https://github.com/ouhammmourachid/mermaid-py) | 177 | Python | MIT | 2026-11-16 | pip install mermaid-py。在 Python 里用链式 API 生成 mermaid 图代码，集成进 docs 自动生成流程：检索链路/防幻觉兜底流程图随代码更新自动重绘。 |
| intel-gradio-theme | [intel/intel-gradio-theme](https://github.com/intel/intel-gradio-theme) | 4 | Python | Apache-2.0 | 2026-01-26 | Apache-2.0、Python、2026-01 更新。作为 kotaemon Gradio 主题备选，with gr.Blocks(theme=...) 接入；若现用主题不满意，可快速 A/B 一版更克制的科技风 UI。 |

## 五、kotaemon 生态参考

| 名称 | GitHub 直链 | Star 数 | 语言 | 许可 | 最近更新 | 本项目怎么用（步骤 / 挂载点） |
|---|---|---:|---|---|---|---|
| kotaemon | [Cinnamon/kotaemon](https://github.com/Cinnamon/kotaemon) | 25,917 | Python | Apache-2.0 | 2026-07-14 | 当前前端基线（已在用，Apache-2.0）。关注其 Extensions/Discussions 的插件机制：把我们的 bge-m3+FAISS 检索器与 rerank 封装成自定义 retriever，按其扩展点注册，替换默认 RAG 管线，让前端直接复用自研后端。 |
| kotaemon-gradio-theme | [lone17/kotaemon-gradio-theme](https://github.com/lone17/kotaemon-gradio-theme) | 43 | Python | — | 2024-04-13 | 专为 kotaemon 定制的 Gradio 主题，star 少、2024-04 后未更新且无明确 license。当作配色灵感参考即可，取其色板思路应用到现有前端主题。 |

## 采集限制与失败项

- GitHub 未认证 API 限速：核心 60 次/小时、搜索 10 次/分钟；采集途中 `RAG evaluation` 查询触发 403，等待重置后由 `rag evaluation dashboard` 等查询补齐，数据完整。
- `python-openxml/python-pptx`、`microsoft/FlagEmbedding`、`BAAI/bge-reranker` 三个直链返回 404；实际规范仓库为 `scanny/python-pptx` 与 `FlagOpen/FlagEmbedding`，`Qdrant/fastembed` 已重定向为小写 `qdrant/fastembed`，均已用规范仓库核验。
- 部分仓库 license 为 `NOASSERTION` 或空（如 GordenPPTSkill、kotaemon-gradio-theme），清单中已逐条标注，集成前需按其 LICENSE 文件确认。
- `ppt-master`、`news-api` 等超高星项目含 AGPL-3.0 / 闭源倾向组件，本清单优先收录 MIT/Apache 许可项，AGPL 项未纳入正式推荐。

详细安装命令、最小可运行示例与项目内挂载代码见 [`snippets.md`](./snippets.md)。