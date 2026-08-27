# -*- coding: utf-8 -*-
"""Write translated briefing bodies into the game as GBK."""
from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_ui import GAME, write_gbk, backup_file
from bodies_sim import BODIES as SIM
from bodies_tod import BODIES as TOD
from bodies_rs import BODIES as RS

def main():
    bodies = {}
    bodies.update(SIM)
    bodies.update(TOD)
    bodies.update(RS)
    n = 0
    bad = []
    for fn, text in sorted(bodies.items()):
        rel = os.path.join("briefing", fn)
        path = os.path.join(GAME, rel)
        if not os.path.isfile(path):
            bad.append(fn)
            continue
        backup_file(rel)
        write_gbk(path, text)
        n += 1
    print("wrote", n, "briefings", "missing", bad)

if __name__ == "__main__":
    main()
