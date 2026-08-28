# -*- coding: utf-8 -*-
"""Apply the full Chinese patch: UI, briefings, catalogs, menu PCX, overlay DLL, manuals."""
from __future__ import print_function
import os
import shutil
import sys

def _here():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


HERE = _here()
sys.path.insert(0, HERE)

import apply_ui


def game():
    return apply_ui.GAME


def copy_font():
    src = r"C:\Windows\Fonts\simhei.ttf"
    if not os.path.isfile(src):
        src = r"C:\Windows\Fonts\msyh.ttc"
    dst = os.path.join(game(), "WINFONTS", "zh_ui.ttf")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isfile(src):
        shutil.copy2(src, dst)
        print("font", src, "->", dst)
    elif os.path.isfile(dst):
        print("font already present")
    else:
        print("WARNING: no SimHei/YaHei, UI Chinese may fail")


def copy_dll():
    src = os.path.join(HERE, "gdi_zh", "DINPUT8.dll")
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", HERE)
        cand = [
            os.path.join(meipass, "gdi_zh", "DINPUT8.dll"),
            os.path.join(meipass, "DINPUT8.dll"),
            src,
        ]
        src = next((p for p in cand if os.path.isfile(p)), src)
    dst = os.path.join(game(), "DINPUT8.dll")
    if not os.path.isfile(src):
        print("WARNING: missing", src)
        return
    shutil.copy2(src, dst)
    print("dll ->", dst)


def copy_manuals():
    names = ("F-22 ADF 飞行手册 中文.pdf", "F-22 ADF 按键对照 中文.pdf")
    src_dir = os.path.join(HERE, "manuals")
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", HERE)
        if os.path.isdir(os.path.join(meipass, "manuals")):
            src_dir = os.path.join(meipass, "manuals")
    for name in names:
        src = os.path.join(src_dir, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(game(), name))
            print("manual", name)


def main():
    if not os.path.isfile(os.path.join(game(), "adf.exe")):
        print("adf.exe not found in", game())
        return 1
    print("game", game())
    copy_font()
    import apply_ui
    apply_ui.main()
    import apply_finish
    apply_finish.main()
    import restore_overlay_en
    restore_overlay_en.main()
    import paint_pcx
    paint_pcx.main()
    import install_acd
    install_acd.main()
    import install_tools
    install_tools.main()
    import import_acd
    import_acd.main()
    copy_dll()
    copy_manuals()
    print("apply_all done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
