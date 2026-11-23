"""主流程：路由 -> 工具/检索 -> 带引用回答 -> 兜底防幻觉"""
import time
from .llm import chat
from .router import route
from .retriever import Retriever
from .reranker import rerank
import config
from . import tools
from config import TOP_K, SCORE_THRESHOLD

ANSWER_SYSTEM = """你是"易班百事通"，XX学院易班分站的校园事务智能助手。
回答规则：
1. 仅依据【参考资料】回答，禁止编造文件里没有的内容；关键结论后标注引用编号，如 [1] 或 [1][2]。
2. 用友好、简洁的中文面向学生回答；金额、名额、时间必须与原文一致。
3. 若参考资料不足以回答问题，只输出一行：NOT_FOUND"""

FALLBACK = ("这个问题暂时超出了我的知识库范围。建议：\n"
            "1. 到学校官网通知栏或易班平台检索最新通知；\n"
            "2. 咨询对应职能部门（学生资助中心 / 后勤处 / 财务处 / 教务处）；\n"
            "3. 欢迎在易班分站留言，知识库会持续更新。")

class YibanAgent:
    def __init__(self):
        self.retriever = Retriever()

    def _result(self, reply, citations, intent, t0):
        return {
            "reply": reply,
            "citations": citations,
            "intent": intent,
            "latency": round(time.time() - t0, 2),
        }

    def answer(self, history, user_input):
        t0 = time.time()
        step = route(history, user_input)
        intent = step["intent"]

        # 1) 含糊问题 -> 澄清追问
        if intent == "unclear":
            reply = step.get("clarify") or "能具体说说是哪一项事务吗？例如：国家励志奖学金、宿舍报修、差旅报销？"
            return self._result(reply, [], intent, t0)

        # 2) 校历类 -> 工具直答
        if intent == "calendar":
            return self._result(tools.week_info(), [], intent, t0)

        query = step.get("rewritten") or user_input

        # 3) 材料清单 -> 结构化工具；未收录则退回知识库
        if intent == "checklist":
            cl = tools.checklist(query)
            if cl:
                return self._result(cl, [], intent, t0)

        # 4) 常规问答 -> RAG 检索 + 引用溯源
        raw_hits = self.retriever.search(query, k=config.RETRIEVE_TOP_K if config.USE_RERANK else TOP_K)
        if config.USE_RERANK:
            raw_hits = rerank(query, raw_hits)
        hits = [h for h in raw_hits if h["score"] >= SCORE_THRESHOLD]
        if not hits:
            return self._result(FALLBACK, [], intent, t0)

        context = "\n\n".join(
            "[{}] 来源：{}（{}）\n{}".format(i + 1, h["source"], h["section"] or "正文", h["text"])
            for i, h in enumerate(hits)
        )
        msgs = [{"role": "system", "content": ANSWER_SYSTEM}]
        msgs += history[-6:]
        msgs.append({"role": "user", "content": "【问题】" + query + "\n\n【参考资料】\n" + context})
        reply = chat(msgs, temperature=0.3)

        if "NOT_FOUND" in reply:
            return self._result(FALLBACK, [], intent, t0)

        citations = [
            {"n": i + 1, "source": h["source"], "section": h["section"] or "正文",
             "score": round(h["score"], 3), "snippet": h["text"][:150]}
            for i, h in enumerate(hits)
        ]
        return self._result(reply, citations, intent, t0)
