# -*- coding: utf-8 -*-
"""Re-encode briefing/catalog overlay text as UTF-8. Leave GDD as GBK."""
from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_ui import GAME, write_utf8, write_gbk, decode_src, read_bytes


def convert(rel):
    path = os.path.join(GAME, rel)
    if not os.path.isfile(path):
        print("missing", rel)
        return
    text = decode_src(read_bytes(path))
    write_utf8(path, text)
    print("utf-8", rel)


def main():
    for fn in ("simultor.txt", "td_miss.txt", "td_tours.txt", "misssel.txt", "multipla.txt", "arcade.txt", "wptasks.txt"):
        convert(os.path.join("f22data", fn))
    convert(os.path.join("briefing", "credits1.txt"))
    # existing briefing files already in BODIES will be rewritten by apply_briefing_bodies
    gdd = os.path.join(GAME, "f22data", "simultor.gdd")
    t = decode_src(read_bytes(gdd))
    repl = [
        ('TEXT "飞行"', 'TEXT "飞行训练"'),
        ('TEXT "武器"', 'TEXT "武器训练"'),
        ('TOOLTIP "MISS_TYPE_0" TEXT "基础飞行训练"', 'TOOLTIP "MISS_TYPE_0" TEXT "自由飞行"'),
        ('TOOLTIP "MISS_TYPE_1" TEXT "红海战区航线游览"', 'TOOLTIP "MISS_TYPE_1" TEXT "起飞、着陆与空中加油训练"'),
        ('TOOLTIP "MISS_TYPE_2" TEXT "武器训练"', 'TOOLTIP "MISS_TYPE_2" TEXT "武器训练"'),
        ('TOOLTIP "MISS_TYPE_3" TEXT "预警机任务训练"', 'TOOLTIP "MISS_TYPE_3" TEXT "战斗机动训练"'),
        ('TOOLTIP "MISS_TYPE_4" TEXT "僚机协同训练"', 'TOOLTIP "MISS_TYPE_4" TEXT "预警机任务训练"'),
        ('TOOLTIP "MISS_TYPE_5" TEXT "空战训练"', 'TOOLTIP "MISS_TYPE_5" TEXT "空战战术训练"'),
    ]
    new = t
    for a, b in repl:
        new = new.replace(a, b)
    if new != t:
        write_gbk(gdd, new)
        print("updated simultor.gdd labels")
    else:
        print("simultor.gdd labels unchanged")


if __name__ == "__main__":
    main()
