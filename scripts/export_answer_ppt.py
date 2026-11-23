r"""把系统问答+引用溯源自动导出成答辩幻灯片（python-pptx）

把现场演示的真实问答固化成 PPT 附录页，评委问"证据在哪"时直接翻页。
用法：python scripts\export_answer_ppt.py
输出：eval/答辩附录-问答实录.pptx
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from agent.pipeline import YibanAgent

# 可选：套用项目内的免费模板（有模板则用，没有则用空白版式）
TEMPLATES = BASE / "docs" / "resources" / "ppt-templates" / "templates"
DEMO_QUESTIONS = [
    "国家励志奖学金的申请条件是什么？",
    "宿舍水管漏水怎么报修？",
    "办理差旅报销需要哪些材料？",
    "我这个情况能拿钱吗？",
]


def pick_template():
    if TEMPLATES.exists():
        files = sorted(TEMPLATES.glob("*.pptx"))
        if files:
            print("使用模板:", files[0].name)
            return Presentation(str(files[0]))
    return Presentation()


def main():
    agent = YibanAgent()
    prs = pick_template()
    blank = prs.slide_layouts[6]

    for q in DEMO_QUESTIONS:
        r = agent.answer([], q)
        slide = prs.slides.add_slide(blank)
        # 标题
        title = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(9), Inches(0.7))
        tf = title.text_frame
        tf.text = "问：" + q
        tf.paragraphs[0].runs[0].font.size = Pt(22)
        tf.paragraphs[0].runs[0].font.bold = True
        tf.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x0B, 0x53, 0x94)
        # 回答
        body = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(3.2))
        tf = body.text_frame
        tf.word_wrap = True
        tf.text = "答：" + r["reply"][:1200]
        for p in tf.paragraphs:
            for run in p.runs:
                run.font.size = Pt(13)
        # 引用溯源
        if r["citations"]:
            cites = "\n".join(
                "[{}] {} · {}（相似度 {}）".format(c["n"], c["source"], c["section"], c["score"])
                for c in r["citations"]
            )
            box = slide.shapes.add_textbox(Inches(0.5), Inches(4.7), Inches(9), Inches(1.6))
            tf = box.text_frame
            tf.word_wrap = True
            tf.text = "引用来源：\n" + cites
            for p in tf.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(11)
                    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        # 意图与耗时
        meta = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(9), Inches(0.4))
        meta.text_frame.text = "意图：{} · 耗时 {}s".format(r["intent"], r["latency"])

    out = BASE / "eval" / "答辩附录-问答实录.pptx"
    prs.save(str(out))
    print("已导出:", out, "共", len(DEMO_QUESTIONS), "页")


if __name__ == "__main__":
    main()
