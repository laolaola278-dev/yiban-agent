"""工具集：校历查询 / 材料清单（提交前按学校真实规定核对补充）"""
import json
from datetime import date, datetime
from config import CALENDAR_PATH

# TODO：按学校真实通知核对、补充每一项材料
MATERIALS = {
    "国家奖学金": [
        "《国家奖学金申请审批表》",
        "上一学年成绩单（教务处盖章）",
        "综合素质测评排名证明",
        "个人事迹材料（1000 字以内）",
    ],
    "国家励志奖学金": [
        "《国家励志奖学金申请表》",
        "家庭经济困难认定申请表",
        "上一学年成绩单",
        "家庭经济情况说明",
    ],
    "校级助学金": [
        "助学金申请表",
        "家庭经济困难认定结果复印件",
        "班级评议记录",
    ],
    "宿舍报修": [
        "报修人姓名 + 宿舍号 + 联系电话",
        "故障描述与照片",
        "可预约维修的时间段",
    ],
    "差旅/公务报销": [
        "报销单（负责人签字）",
        "正规发票（抬头、税号正确）",
        "行程审批单",
        "银行卡复印件",
    ],
}

def load_calendar():
    with open(CALENDAR_PATH, encoding="utf-8") as f:
        return json.load(f)

def week_info(query_date=None):
    cal = load_calendar()
    start = datetime.strptime(cal["semester_start"], "%Y-%m-%d").date()
    d = query_date or date.today()
    if d < start:
        return "新学期 {} 开学，目前尚未开学，共 {} 个教学周。".format(
            cal["semester_start"], cal["total_weeks"])
    week = (d - start).days // 7 + 1
    lines = ["今天是 {}，本学期第 {} 教学周（本学期 {} 开学，共 {} 周）。".format(
        d.isoformat(), week, cal["semester_start"], cal["total_weeks"])]
    for ev in cal.get("events", []):
        lines.append("第{}-{}周：{}".format(ev["week_start"], ev["week_end"], ev["label"]))
    return "\n".join(lines)

def checklist(item):
    key = next((k for k in MATERIALS if k in item or item in k), None)
    if key is None:
        return None
    mats = "\n".join("- " + m for m in MATERIALS[key])
    return "办理【{}】一般需要准备以下材料（以学校最新通知为准）：\n{}".format(key, mats)
