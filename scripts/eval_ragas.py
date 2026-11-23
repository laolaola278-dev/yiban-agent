r"""ragas 四维评测（可选插件，装 ragas 后运行）

把"防幻觉兜底"变成 4 个可量化分数，直接填 PPT 第 7 页实测数据：
  faithfulness（忠实度）       回答是否都能从引用原文推导
  answer_relevancy（相关性）   回答是否切题
  context_precision（精确率）  检索到的条款是否都是有用的
  context_recall（召回率）     正确条款是否被检索到

用法：
  pip install -r requirements-optional.txt
  python scripts\eval_ragas.py

依赖：eval/testset.jsonl（需含 "ground_truth" 字段；没有则脚本自动生成占位答案，仅供演示跑通）
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from config import TESTSET_PATH
from agent.pipeline import YibanAgent


def build_dataset(agent):
    from datasets import Dataset
    rows = []
    items = [json.loads(l) for l in TESTSET_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    for it in items[:50]:  # 评测 50 题足够，控制 API 成本
        r = agent.answer([], it["q"])
        contexts = [c["snippet"] for c in r["citations"]] or ["(未检索到相关内容)"]
        rows.append({
            "question": it["q"],
            "answer": r["reply"],
            "contexts": contexts,
            "ground_truth": it.get("ground_truth") or it.get("must_include", [""])[0] or "见校规原文",
        })
    return Dataset.from_list(rows)


def main():
    try:
        import ragas
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    except ImportError:
        print("请先安装：pip install -r requirements-optional.txt")
        sys.exit(1)

    agent = YibanAgent()
    print("构造评测集（调用检索+大模型，约几分钟）...")
    ds = build_dataset(agent)
    print("跑 ragas 四维评测...")
    result = evaluate(ds, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    print("\n===== ragas 评测结果（填 PPT 第 7 页）=====")
    print(result)
    out = BASE / "eval" / "ragas_result.json"
    result.save(str(out))
    print("结果已保存:", out)


if __name__ == "__main__":
    main()
