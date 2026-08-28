# -*- coding: utf-8 -*-
"""Restore English originals from locale_zh/en_backup."""
from __future__ import print_function
import os, shutil

import apply_ui


def main():
    game = apply_ui.GAME
    backup = apply_ui.BACKUP
    if not os.path.isdir(backup):
        print("backup missing:", backup)
        return
    n = 0
    for dirpath, _, files in os.walk(backup):
        for fn in files:
            src = os.path.join(dirpath, fn)
            rel = os.path.relpath(src, backup)
            dst = os.path.join(game, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            n += 1
    print("restored", n, "files from en_backup")
    print("Note: WINFONTS\\zh_ui.ttf is extra and is not removed.")


if __name__ == "__main__":
    main()
