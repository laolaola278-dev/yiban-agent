"""意图路由：LLM 输出 JSON，判定 faq/calendar/checklist/unclear 并改写查询"""
import json
from .llm import chat

ROUTER_SYSTEM = """你是"易班百事通"校园事务智能体的意图路由器。根据用户最新问题和对话历史，输出一个 JSON 对象（不要输出任何其他文字）：
{"intent": "faq 或 calendar 或 checklist 或 unclear", "clarify": "intent 为 unclear 时输出一句澄清追问，否则为 null", "rewritten": "结合上下文把问题改写成可独立检索的完整问题，无法改写时沿用原问题"}

判定规则：
- calendar：问今天是第几周、校历、开学时间、考试周、放假时间；
- checklist：问办理某事项要准备什么材料、带什么证件；
- faq：问政策、条件、金额、时间、流程（奖助学金、综测、报修、报销等）；
- unclear：问题信息缺失无法作答（如只说"奖学金"没说哪一种），或与校园事务完全无关。
注意：能合理推断时优先选具体意图，不要滥用 unclear。"""

def route(history, user_input):
    msgs = [{"role": "system", "content": ROUTER_SYSTEM}]
    msgs += history[-6:]
    msgs.append({"role": "user", "content": user_input})
    raw = chat(msgs, temperature=0.1, response_json=True)
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        start, end = raw.find("{"), raw.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(raw[start:end + 1])
            except Exception:
                data = None
    if not isinstance(data, dict):
        data = {}
    return {
        "intent": data.get("intent", "faq"),
        "clarify": data.get("clarify"),
        "rewritten": data.get("rewritten") or user_input,
    }
