# -*- coding: utf-8 -*-
"""Final polish: leftover catalog name, window titles, control-mapping label, GBK credits."""
from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_ui import GAME, write_gbk, backup_file, decode_src, read_bytes


def patch(rel, transform):
    path = os.path.join(GAME, rel)
    backup_file(rel)
    text = decode_src(read_bytes(path))
    new = transform(text)
    if new != text:
        write_gbk(path, new)
        print("updated", rel)
    else:
        print("unchanged", rel)


def main():
    def td_miss(t):
        return t.replace(
            '"Red Sea Ops Egyptian Tour"',
            '"红海作战埃及巡航"',
        )

    patch(os.path.join("f22data", "td_miss.txt"), td_miss)

    # Keep WINDOW TITLE in English. Some remaster paths look up screens by TITLE
    # ("Brief", "Simulator") when Confirm starts the mission.
    titles_en = [
        ('TITLE "制作人员"', 'TITLE "Credits"'),
        ('TITLE "模拟训练"', 'TITLE "Simulator"'),
        ('TITLE "战区巡航"', 'TITLE "Tour of Duty"'),
        ('TITLE "快速作战"', 'TITLE "Quick Combat"'),
        ('TITLE "多人游戏"', 'TITLE "Multiplay"'),
        ('TITLE "简报"', 'TITLE "Brief"'),
    ]

    def titles_only(t):
        for a, b in titles_en:
            t = t.replace(a, b)
        return t

    gdd = os.path.join(GAME, "f22data")
    for fn in os.listdir(gdd):
        if fn.lower().endswith(".gdd"):
            patch(os.path.join("f22data", fn), titles_only)

    def option(t):
        return t.replace("校准控制器...", "控制器校准...")

    patch(os.path.join("f22data", "option.gdd"), option)

    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credits1_zh.txt")
    dst_rel = os.path.join("briefing", "credits1.txt")
    # credits written next to this script as UTF-8 source if present; else game file
    game_credits = os.path.join(GAME, dst_rel)
    backup_file(dst_rel)
    raw = open(game_credits, "rb").read()
    try:
        text = raw.decode("utf-8")
        if "执行制作人" in text:
            write_gbk(game_credits, text.replace("\n", "\r\n") if "\r\n" not in text else text)
            print("re-encoded credits1.txt as GBK")
        else:
            print("credits1.txt already GBK or unexpected encoding")
    except UnicodeDecodeError:
        print("credits1.txt not utf-8, skip re-encode")


if __name__ == "__main__":
    main()
