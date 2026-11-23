"""批量评测：python scripts/eval.py  （输出逐条 PASS/FAIL、通过率、平均耗时）"""
import json
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from config import TESTSET_PATH
from agent.pipeline import YibanAgent

def judge(item, result):
    must = item.get("must_include") or []
    if must:
        return all(k in result["reply"] for k in must)
    expect = item.get("expect_intent")
    if expect:
        return result["intent"] == expect
    return True

def main():
    agent = YibanAgent()
    items = [json.loads(l) for l in TESTSET_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    passed, lat = 0, []
    for it in items:
        t0 = time.time()
        r = agent.answer([], it["q"])
        dt = time.time() - t0
        lat.append(dt)
        ok = judge(it, r)
        passed += ok
        print("[{}] {}（{:.1f}s, intent={}）".format("PASS" if ok else "FAIL", it["q"], dt, r["intent"]))
        if not ok:
            print("      期望：{} / 实际：{}".format(
                it.get("must_include") or it.get("expect_intent"),
                r["reply"][:60].replace("\n", " ")))
    n = max(len(items), 1)
    print("\n通过率：{}/{} = {:.0%}；平均耗时：{:.1f}s".format(
        passed, len(items), passed / n, sum(lat) / max(len(lat), 1)))

if __name__ == "__main__":
    main()
