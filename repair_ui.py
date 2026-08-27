# -*- coding: utf-8 -*-
"""Restore GDD/WIN from backup, then re-apply TEXT/TOOLTIP-only replacements."""
from __future__ import print_function
import os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_ui import GAME, BACKUP, UI, write_gbk, write_utf8, decode_src, read_bytes, quoted_replace, CATALOG, HINT, WPTASK, CREDIT_ROLES, backup_file, apply_file

def restore_tree(rel_dir, exts):
    src_root = os.path.join(BACKUP, rel_dir)
    dst_root = os.path.join(GAME, rel_dir)
    if not os.path.isdir(src_root):
        print("no backup", src_root)
        return
    n = 0
    for dirpath, _, files in os.walk(src_root):
        for fn in files:
            if exts and not any(fn.lower().endswith(e) for e in exts):
                continue
            src = os.path.join(dirpath, fn)
            rel = os.path.relpath(src, src_root)
            dst = os.path.join(dst_root, rel)
            shutil.copy2(src, dst)
            n += 1
    print("restored", n, "from", rel_dir)


def text_only_replace(text, pairs):
    table = dict(pairs)
    def repl(m):
        inner = m.group(2)
        zh = table.get(inner)
        if zh is None:
            return m.group(0)
        return m.group(1) + '"' + zh + '"'
    return re.sub(r'(TEXT\s+)"([^"]*)"', repl, text, flags=re.IGNORECASE)


def main():
    restore_tree("f22data", (".gdd", ".win", ".cfg"))

    def windesc(t):
        # Engine: CreateWinFont max 3 files. Do not add a fourth CREATE_SYS_FONT.
        t = t.replace('CREATE_SYS_FONT "winfonts\\f22_1.ext"', 'CREATE_SYS_FONT "winfonts\\zh_ui.ttf"')
        t = t.replace('CREATE_SYS_FONT "winfonts\\f22_2.ext"', 'CREATE_SYS_FONT "winfonts\\zh_ui.ttf"')
        t = t.replace('STYLE "Univers"', 'STYLE "SimHei"')
        t = t.replace('STYLE "MS Sans Serif"', 'STYLE "SimHei"')
        t = t.replace('STYLE "OPUnivers-FiftySeven"', 'STYLE "SimHei"')
        t = t.replace('STYLE "Arial Black"', 'STYLE "SimHei"')
        return t

    apply_file(os.path.join("f22data", "windesc.win"), windesc)

    titles = [
        ('TITLE "Credits"', 'TITLE "制作人员"'),
        ('TITLE "Simulator"', 'TITLE "模拟训练"'),
        ('TITLE "Tour of Duty"', 'TITLE "战区巡航"'),
        ('TITLE "Quick Combat"', 'TITLE "快速作战"'),
        ('TITLE "Multiplay"', 'TITLE "多人游戏"'),
        ('TITLE "Brief"', 'TITLE "简报"'),
    ]

    def gdd_text(t):
        t = text_only_replace(t, UI)
        for a, b in titles:
            t = t.replace(a, b)
        return t

    for fn in os.listdir(os.path.join(GAME, "f22data")):
        if fn.lower().endswith(".gdd"):
            apply_file(os.path.join("f22data", fn), gdd_text)

    # cockpit hints: rebuild from English backup
    hin = os.path.join(BACKUP, "huddle", "f22.ins")
    if os.path.isfile(hin):
        shutil.copy2(hin, os.path.join(GAME, "huddle", "f22.ins"))
    apply_file(os.path.join("huddle", "f22.ins"), lambda t: quoted_replace(t, HINT))

    # options.cfg FEATURE names are engine lookup keys. Do not translate.

    # catalogs: restore then re-apply (quoted mission names are display-only)
    for fn in ("simultor.txt", "td_miss.txt", "td_tours.txt", "misssel.txt", "multipla.txt", "arcade.txt"):
        b = os.path.join(BACKUP, "f22data", fn)
        d = os.path.join(GAME, "f22data", fn)
        if os.path.isfile(b):
            shutil.copy2(b, d)
        apply_file(os.path.join("f22data", fn), lambda t: quoted_replace(t, sorted(CATALOG.items(), key=lambda kv: -len(kv[0]))), writer=write_utf8)

    apply_file(os.path.join("f22data", "arcade.txt"), lambda t: t.replace('MISSION_TYPE 0 "Arcade"', 'MISSION_TYPE 0 "快速作战"'), writer=write_utf8)
    print("repair done")

if __name__ == "__main__":
    main()
