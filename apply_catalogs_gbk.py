# -*- coding: utf-8 -*-
from __future__ import print_function
import os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_ui import GAME, BACKUP, CATALOG, quoted_replace, write_gbk

def main():
    for fn in ("simultor.txt", "td_miss.txt", "td_tours.txt", "misssel.txt", "multipla.txt", "arcade.txt", "wptasks.txt"):
        b = os.path.join(BACKUP, "f22data", fn)
        d = os.path.join(GAME, "f22data", fn)
        if os.path.isfile(b):
            text = open(b, "rb").read().decode("latin-1")
            if fn == "wptasks.txt":
                from apply_ui import WPTASK
                for en, zh in WPTASK:
                    text = text.replace('"' + en + '"', '"' + zh + '"')
            else:
                text = quoted_replace(text, sorted(CATALOG.items(), key=lambda kv: -len(kv[0])))
                if fn == "arcade.txt":
                    text = text.replace('MISSION_TYPE 0 "Arcade"', 'MISSION_TYPE 0 "快速作战"')
            write_gbk(d, text)
            print("gbk", fn)

if __name__ == "__main__":
    main()
