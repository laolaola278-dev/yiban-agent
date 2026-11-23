# 资源采集汇总（PPT 模板 + GitHub 插件）

> 采集时间：2026-11-18；方式：2 个子代理并发，全程 GitHub API / web_fetch，未触碰用户浏览器。
> 用途：本项目（易班百事通 · 数智新技艺参赛）答辩材料制作与工具选型。

## 一、PPT 模板（14 条，详见 ppt-templates/README.md）

### 最推荐 3 个

| # | 名称 | 直链 | 理由 |
|---|---|---|---|
| 1 | 站长素材·简约科技毕业论文答辩 | https://downsc.chinaz.net/Files/download/moban/202404/dc1864.pptx | 中文、科技学术风、免费直链、2.05MB，最贴答辩场景 |
| 2 | GordenPPTSkill·top-thesis | https://raw.githubusercontent.com/GordenSun/GordenPPTSkill/main/templates/top-thesis/template.pptx | 中文答辩骨架、MIT 许可、完全可编辑 |
| 3 | Microsoft·Scientific discovery | https://createcatalog.public.onecdn.static.microsoft.com/catalog-assets/en-us/51de1e5f-e0e8-4dd0-99f3-5b7584f7abdc/TF51de1e5f-e0e8-4dd0-99f3-5b7584f7abdce62b1bc2_wac-512944e5432e.pptx | 微软官方免费模板、科技蓝，直链已验证 |

- 本地已存 12 张预览图（ppt-templates/previews/），挑模板不用翻网页，直接看图。
- 限制：稻壳儿/Slidesgo 页面 404 或会员墙；2 个高校仓库未标 LICENSE（已在 README 逐条标注）。

## 二、GitHub 插件（22 个，详见 github-plugins/README.md + snippets.md）

### 最推荐 3 个

| # | 插件 | Star | 能给项目带来什么 |
|---|---|---|---|
| 1 | ragas (vibrantlabsai/ragas) | 16,361 | 把防幻觉兜底变成 faithfulness / answer_relevancy / context_precision / context_recall 四个可量化分数，PPT 实测数据页直接升级 |
| 2 | FlagEmbedding/bge-reranker | 12,344 | 与现有 bge-m3 同源，FAISS top-20 → rerank top-5 二阶段精排，提升引用命中率、降幻觉（PPT 技术亮点） |
| 3 | python-pptx (scanny/python-pptx) | 3,590 | 把问答+引用溯源自动导出答辩幻灯片；配 ppt-master 生成初稿提效 |

- snippets.md 含 7 个插件的 pip 命令 + 最小示例 + 本项目的具体挂载点（如 backend_api.py 的 format_reply、scripts/ingest.py）。
- raw_github_data.json 保留 135 个仓库的原始 API 数据作为证据链。
- 限制：GitHub 未认证 API 限速（搜索 10/min、核心 60/hr），RAG evaluation 查询中途 403，已由其他查询补齐；部分仓库直链重定向/无 LICENSE，已逐条标注。

## 三、选题建议（结合当前项目）

1. 做 PPT：先用站长素材 dc1864.pptx（科技学术风、中文）做底版，把 PPT脚本.md 的 13 页文案逐页套进去；预览图在 previews/ 里先挑配色。
2. 加技术分：改 scripts/ingest.py 接 bge-reranker（二阶段精排），再跑 ragas 出 4 维指标填 P7 实测数据页——纯加分项，改动小、叙事强。
3. 提效：python-pptx + snippets.md 的 export_answer_ppt.py 挂载点，把系统现场问答+引用直接导出成答辩附录页，评委问证据时直接翻。
---

## 四、已部署到项目内的落地清单（2026-11-18 实际完成）

**PPT 模板（4 个 .pptx 本体已下载到 ppt-templates/templates/，包内自带）**

| 文件 | 用途 |
|---|---|
| 01-站长素材-科技答辩.pptx | 主版式（中文科技学术风，首选） |
| 02-Gorden-top-thesis.pptx | 中文答辩骨架（MIT） |
| 05-Gorden-数据图表页.pptx | 实测数据/评测页 |
| 06-站长素材-蓝色精简答辩.pptx | 轻量备选 |

**插件（代码已接入，直接可用或一键开启）**

| 插件 | 落地位置 | 状态 |
|---|---|---|
| bge-reranker（FlagEmbedding） | agent/reranker.py + agent/pipeline.py + config.py（USE_RERANK 开关） | 代码已接入；.env 设 USE_RERANK=1 并装 requirements-optional.txt 即生效；未装自动降级 |
| ragas | scripts/eval_ragas.py | 评测脚本已写；装 requirements-optional.txt 后运行，出 4 维指标 |
| python-pptx | scripts/export_answer_ppt.py | 已入主依赖；运行即把现场问答+引用导出成答辩附录 PPTX（自动套 templates/ 下模板） |

注意：FlagEmbedding/ragas 依赖较大（torch 约 2GB），已隔离到 requirements-optional.txt，答辩前网络好时再装；不装主程序完全正常。