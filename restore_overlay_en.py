# -*- coding: utf-8 -*-
"""Restore English briefing/catalog overlay text. GDD UI stays Chinese."""
from __future__ import print_function
import os, shutil

GAME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "en_backup")


def copy_tree(rel):
    src = os.path.join(BACKUP, rel)
    dst = os.path.join(GAME, rel)
    if os.path.isfile(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print("restored", rel)
        return 1
    if not os.path.isdir(src):
        print("missing backup", rel)
        return 0
    n = 0
    for dirpath, _, files in os.walk(src):
        for fn in files:
            s = os.path.join(dirpath, fn)
            r = os.path.relpath(s, BACKUP)
            d = os.path.join(GAME, r)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            n += 1
    print("restored", n, "from", rel)
    return n


def main():
    copy_tree("briefing")
    for fn in ("simultor.txt", "td_miss.txt", "td_tours.txt", "misssel.txt", "multipla.txt", "arcade.txt", "wptasks.txt"):
        copy_tree(os.path.join("f22data", fn))
    print("overlay English restored; GDD/hints/font unchanged")


if __name__ == "__main__":
    main()
