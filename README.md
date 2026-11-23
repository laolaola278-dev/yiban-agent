# 易班百事通 —— 校园事务智能问答助手

## 项目地址与在线体验

- **GitHub 项目地址**：[https://github.com/{{GITHUB_REPO}}](https://github.com/{{GITHUB_REPO}})（提交前把 `{{GITHUB_REPO}}` 替换为你的实际仓库路径，如 `yourname/yiban-agent`）
- **在线体验网址**：[{{DEMO_URL}}]({{DEMO_URL}})（部署后填入实际地址，如 `https://yiban-agent.example.com`；本地演示访问 `http://localhost:7860`）
- **本地体验**：双击 `启动.bat` 或 `启动-docker.bat` → 浏览器打开 `http://localhost:7860`，账号 admin / admin

> 有问必答，答必有据。基于自研 RAG 管线的校园事务智能体，参加 2026 广东省"数智新技艺"作品遴选。

学生一句话提问，系统从**学校官网公开发布的真实校规**（64 篇、约 14 万字）中检索原文作答，
每条回答附**来源文件 + 章节 + 原文片段**；查不到就明说并给出官方求助渠道，绝不编造。

---

## 一、系统架构（双引擎）

    学生提问
       |
    [前端层] kotaemon WebUI :7860（行内引用角标 + PDF 原文高亮）
       |  OpenAI 兼容协议
    [网关层] backend_api.py :8010（自研管线包装为标准接口）
       |
    [智能体层] agent/
      意图路由（LLM JSON 分类 + 查询改写）
      ├─ unclear   → 多轮澄清追问
      ├─ calendar  → 校历工具（第几教学周/考试周）
      ├─ checklist → 材料清单工具（结构化输出）
      └─ faq       → RAG 检索链路
       |
    [检索层] 条款级切片(保留章节元数据) → bge-m3 向量化 → FAISS 余弦 TOP-K → 阈值过滤
       |
    [知识层] data/raw/ 64 篇官网真实校规（每篇来源URL登记 manifest.jsonl）

**防幻觉三防线**：检索阈值过滤 → 生成端 NOT_FOUND 检测 → 兜底引导（官方渠道 + 更新机制）。

---

## 二、知识库内容（全部来自广东职业技术学院官网）

| 条线 | 篇数 | 代表文件 |
|---|---|---|
| 资助 | 13 | 国家奖学金/励志/助学金评审办法、困难认定、勤工助学、助学贷款 |
| 学生管理 | 14 | 学生奖励办法(2026修订)、处分管理规定、优良学风班、晨午晚检 |
| 宿舍 | 18 | 学生公寓管理规定(全文)、报修8步流程、热水热线、水电费 |
| 报销 | 19 | 差旅费报销、发票管理、电子票据、学费收缴、奖助金发放 |

> 综测说明：官网无独立综测办法，综测体系内嵌于《学生奖励办法(2026修订)》——已按此出题。

---

## 三、快速开始（一键）

1. **配置**：首次运行自动生成 .env 并打开记事本，填两个 Key：
   - CHAT_API_KEY：DeepSeek https://platform.deepseek.com
   - EMBED_API_KEY：SiliconFlow https://cloud.siliconflow.cn（bge-m3 免费）
   - 单 Key 备选：全用智谱 glm-4-flash + embedding-3（EMBED_DIM=2048）
2. **双击 启动.bat**：建环境→装依赖→建知识库→起后端(8010)→起前端(7860)→开浏览器
3. **登录**：admin / admin（kotaemon 本地用户管理）
4. **接入**：kotaemon 页面 Settings → OpenAI-compatible →
   - API Base：http://127.0.0.1:8010/v1
   - API Key：任意（如 sk-local）
   - Model：yiban-agent

## 四、工具箱（全 bat，双击即用）

| 脚本 | 作用 |
|---|---|
| 启动.bat | 一键全栈：环境+建库+后端+kotaemon+浏览器（kotaemon 必达，不降级） |
| 停止.bat | 停止全部服务 |
| 启动前端.bat | 单独启动 kotaemon |
| 启动后端.bat | 单独启动 8010 网关 |
| 重建知识库.bat | 更新 data/raw 后重新切片向量化 |
| 跑评测.bat | 跑测试集出通过率/耗时（PPT 数据） |

守护机制：计划任务 KotaemonWatchdog 每 5 分钟探测 7860，掉线自动重启（watchdog.log）。

## 五、前端双通道说明（答辩要点）

- **通道 A（kotaemon 自带 RAG）**：校规拖进 File Collection，行内引用角标 + PDF 原文高亮——"答必有据"视觉冲击
- **通道 B（自研管线）**：走 8010 网关，条款级切片 + 意图路由 + 澄清 + 工具调用 + 阈值兜底——技术叙事核心
- 双通道可并存演示：同一问题对比回答，突出自研管线的引用溯源与防幻觉兜底

## 六、工程踩坑实录（真实调试记录，PPT 可讲）

| 坑 | 现象 | 解法 |
|---|---|---|
| llama-cpp-python 编译 | 需 MSVC 构建失败 | 纯 API 模式剔除 |
| deepsearch-glm 无 win wheel | docling 拉入 Linux-only 包 | 砍掉 docling extra |
| uv.lock 死锁 | 强杀进程留 0 字节锁 | 清锁重解析 |
| 大 wheel 下载挂死 | lancedb/pylance/llama-hub 反复卡死 | curl 断点续传 + find-links 离线装 |
| langchain 0.3 不兼容 | metaclass conflict | 降级 langchain 0.2.x |
| SVG 碎图标 | gradio XSS 白名单拒 svg MIME | patch 白名单 + CDN 本地化 |
| 路径括号 | hds(js) 让 cmd 引号崩坏 | 引号包裹+真实路径 |
| 官网反爬 | 栏目页 AJAX/登录墙 | POST 内部接口+浏览器渲染抓取 |

## 七、目录结构

    yiban-agent/
    ├─ 启动.bat / 停止.bat / 启动前端.bat / 启动后端.bat / 跑评测.bat / 重建知识库.bat
    ├─ backend_api.py          OpenAI 兼容网关（8010）
    ├─ backend_api.py 已含直启入口（python backend_api.py）
    ├─ agent/                  pipeline / router / retriever / tools / llm
    ├─ scripts/                ingest.py（建库）/ eval.py（评测）
    ├─ data/raw/               64 篇真实校规 + manifest.jsonl × 4
    ├─ eval/testset.jsonl      测试问答集
    └─ README.md

## 八、合规与原创声明

- 全部代码、提示词、评测集自研；模型为官方 API 调用，符合平台协议
- 知识库仅收录学校官网公开发布的制度文件，每篇附来源 URL 可核对
- 不采集学生个人信息，不存储对话数据；查不到即兜底引导官方渠道
- 已排除占位假文档，raw 目录全部为真实抓取文件
## 九、可选增强（答辩加分，按需开启）

- 二阶段精排：.env 加 USE_RERANK=1 + pip install -r requirements-optional.txt（FlagEmbedding，含 torch 约 2GB），FAISS 召回 20 条 → bge-reranker 精排 5 条，提升引用命中率；未装自动降级为零开销。
- ragas 四维评测：装可选依赖后 python scripts\eval_ragas.py，出忠实度/相关性/精确率/召回率，结果存 eval\ragas_result.json，填 PPT P7 实测数据页。
- 答辩附录自动生成：python scripts\export_answer_ppt.py，把现场问答+引用溯源导出为 eval\答辩附录-问答实录.pptx，自动套用 docs\resources\ppt-templates\templates\ 下的免费模板。
- PPT 模板：4 个 .pptx 本体已随项目打包（templates/ 目录），12 张预览图可直接挑配色。
## 十一、Docker 部署（可选，一行命令起全栈）

项目已提供 `Dockerfile` + `docker-compose.yml`，一条命令同时起后端（自研 RAG，:8010）与前端（kotaemon，:7860）：

```bash
# 1) 先配好 .env（API Key）
cp .env.example .env    # Windows: copy .env.example .env
# 2) 启动
docker compose up -d --build
# 3) 打开 http://localhost:7860（admin/admin）
# 停止：docker compose down
```

Windows 用户可直接双击 `启动-docker.bat`。Linux 服务器部署时把 `docker-compose.yml` 里 kotaemon 的
`OPENAI_API_BASE` 保持 `http://backend:8010/v1`（容器内网互通），无需改 hosts。
注意：镜像首次拉取约 2-4GB；`.env` 与 `data/` 通过 volume 挂载，容器重建不丢配置与知识库。

## 十二、Docker 文件说明

| 文件 | 作用 |
|---|---|
| Dockerfile | 基于 python:3.10-slim 构建后端镜像，含 healthcheck |
| docker-compose.yml | 编排 backend + kotaemon 双容器，前置健康检查 |
| .dockerignore | 排除 .venv/缓存/.env/大素材，镜像精简 |
| 启动-docker.bat | Windows 一键：检查 Docker → 构建 → 启动 → 开浏览器 |