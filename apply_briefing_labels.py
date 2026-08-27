# -*- coding: utf-8 -*-
"""Safe briefing label pass: only tagged field names and a few exact value lines."""
from __future__ import print_function
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_ui import GAME, write_gbk, decode_src, read_bytes, backup_file

LABELS = [
    ("MISSION OBJECTIVES:", "任务目标："),
    ("START LOCATION:", "起飞位置："),
    ("MISSION TYPE:", "任务类型："),
    ("TAKEOFF BASE:", "起飞基地："),
    ("ESCORT CALLSIGN:", "护航呼号："),
    ("WILD WEASEL CALLSIGN:", "野鼬呼号："),
    ("STRIKE CALLSIGNS:", "打击呼号："),
    ("SEAD CALLSIGNS:", "压制防空呼号："),
    ("STRIKE CALLSIGN:", "打击呼号："),
    ("START TIME:", "起飞时刻："),
    ("GAME LENGTH:", "对局时长："),
    ("RECOVER AT:", "返航降落："),
    ("BINGO BASE:", "最低燃油备降基地："),
    ("CALLSIGN:", "呼号："),
    ("ARMAMENT:", "挂载："),
    ("WEAPONS:", "武器："),
    ("BRIEFING", "任务简报"),
    ("AWACS:", "预警机："),
    ("JSTARS:", "联合星："),
    ("TEAMS:", "阵营："),
]

TYPES = [
    ("Suppression of Enemy Air Defences (SEAD)", "压制敌防空（SEAD）"),
    ("Battlefield Air Interdiction (BAI)", "战场遮断（BAI）"),
    ("High Value Asset Attack (HVAA)", "高价值目标攻击（HVAA）"),
    ("Close Air Support (CAS)", "近距空中支援（CAS）"),
    ("Combat Air Partrol (CAP)", "战斗空中巡逻（CAP）"),
    ("Combat Air Patrol (CAP)", "战斗空中巡逻（CAP）"),
    ("Combined fighter patrol and SEAD sweep", "歼击机巡逻与压制防空扫荡"),
    ("Practice emergency take-off", "应急起飞训练"),
    ("Practice emergency landing", "应急着陆训练"),
    ("Practice air refueling", "空中加油训练"),
    ("Practice take-off", "起飞训练"),
    ("Practice landing", "着陆训练"),
    ("Egyptian armed reconaissance", "埃及武装侦察"),
    ("Armed reconaissance", "武装侦察"),
    ("Interdiction strike", "遮断打击"),
    ("Airfield denial", "机场封锁"),
    ("Airfield strike", "机场打击"),
    ("Multiple EWR Strike", "多点预警雷达打击"),
    ("Short range air interception", "近距空中拦截"),
    ("Scramble air cover", "紧急起飞空中掩护"),
    ("Egyptian Strike", "埃及打击任务"),
    ("Mobile strike", "机动目标打击"),
    ("SEAD & Counter Air", "压制防空与制空"),
    ("Battlefield Air Interdiction", "战场遮断"),
    ("Fighter Sweep", "歼击机清场"),
    ("Fighter sweep", "歼击机清场"),
    ("Air Intercept", "空中拦截"),
    ("Ship kill", "反舰"),
    ("Decapitation", "斩首"),
    ("SEAD strike", "压制防空打击"),
]


def transform(text):
    for en, zh in LABELS:
        text = text.replace("<c=g>" + en + "</c>", "<c=g>" + zh + "</c>")
    # Values immediately after AWACS/JSTARS tags
    text = re.sub(r"(<c=g>预警机：</c> )Yes\b", r"\1有", text)
    text = re.sub(r"(<c=g>预警机：</c> )YES\b", r"\1有", text)
    text = re.sub(r"(<c=g>预警机：</c> )No\b", r"\1无", text)
    text = re.sub(r"(<c=g>预警机：</c> )Non\b", r"\1无", text)
    text = re.sub(r"(<c=g>联合星：</c> )Yes\b", r"\1有", text)
    text = re.sub(r"(<c=g>联合星：</c> )No\b", r"\1无", text)
    # Mission type line
    for en, zh in TYPES:
        text = text.replace("<c=g>任务类型：</c> " + en, "<c=g>任务类型：</c> " + zh)
    return text


def main():
    briefing = os.path.join(GAME, "briefing")
    n = 0
    for fn in os.listdir(briefing):
        if not fn.lower().endswith(".txt") or fn.lower() == "credits1.txt":
            continue
        rel = os.path.join("briefing", fn)
        backup_file(rel)
        path = os.path.join(GAME, rel)
        text = decode_src(read_bytes(path))
        new = transform(text)
        if new != text:
            write_gbk(path, new)
            n += 1
    print("updated", n, "briefings")

if __name__ == "__main__":
    main()
