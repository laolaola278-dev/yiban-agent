"""把自研 RAG 管线包装成 OpenAI 兼容 API（供 open-webui / kotaemon / lobe-chat 等前端接入）

启动：python -m uvicorn backend_api:app --host 0.0.0.0 --port 8010
前端指向：http://127.0.0.1:8010/v1  （API Key 随便填，如 sk-local）
"""
import sys
import time
import uuid
import asyncio
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.pipeline import YibanAgent

app = FastAPI(title="Yiban Agent API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = YibanAgent()
    return _agent

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "yiban-agent"
    messages: list[Message]
    stream: bool = False

def format_reply(result):
    """回答 + 引用来源（Markdown，前端直接渲染）"""
    reply = result["reply"]
    if result.get("citations"):
        lines = ["", "---", "**📎 引用来源**"]
        for c in result["citations"]:
            lines.append("**[{}]** {} · {}（相似度 {}）".format(c["n"], c["source"], c["section"], c["score"]))
            lines.append("> " + c["snippet"] + "…")
        lines.append("")
        lines.append("意图：{} · 耗时 {}s".format(result["intent"], result["latency"]))
        reply = reply + "\n" + "\n".join(lines)
    return reply

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/v1/models")
def models():
    return {"object": "list", "data": [{"id": "yiban-agent", "object": "model", "owned_by": "yiban"}]}

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    msgs = [m for m in req.messages if m.content]
    if not msgs:
        return {"error": {"message": "empty messages"}}
    user_input = msgs[-1].content
    history = [{"role": m.role, "content": m.content} for m in msgs[:-1]]
    result = get_agent().answer(history, user_input)
    reply = format_reply(result)
    created = int(time.time())
    cid = "chatcmpl-" + uuid.uuid4().hex[:12]

    if not req.stream:
        return {
            "id": cid, "object": "chat.completion", "created": created, "model": req.model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    async def gen():
        for i in range(0, len(reply), 24):
            chunk = {
                "id": cid, "object": "chat.completion.chunk", "created": created, "model": req.model,
                "choices": [{"index": 0, "delta": {"content": reply[i:i+24]}, "finish_reason": None}],
            }
            yield "data: " + __import__("json").dumps(chunk, ensure_ascii=False) + "\n\n"
            await asyncio.sleep(0.02)
        done = {"id": cid, "object": "chat.completion.chunk", "created": created, "model": req.model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
        yield "data: " + __import__("json").dumps(done, ensure_ascii=False) + "\n\n"
        yield "data: [DONE]\n\n"

    from fastapi.responses import StreamingResponse
    return StreamingResponse(gen(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
