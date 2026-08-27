# -*- coding: utf-8 -*-
"""Restore English originals from locale_zh/en_backup."""
from __future__ import print_function
import os, shutil

GAME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "en_backup")


def main():
    if not os.path.isdir(BACKUP):
        print("backup missing:", BACKUP)
        return
    n = 0
    for dirpath, _, files in os.walk(BACKUP):
        for fn in files:
            src = os.path.join(dirpath, fn)
            rel = os.path.relpath(src, BACKUP)
            dst = os.path.join(GAME, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            n += 1
    print("restored", n, "files from en_backup")
    print("Note: WINFONTS\\zh_ui.ttf is extra and is not removed.")


if __name__ == "__main__":
    main()
