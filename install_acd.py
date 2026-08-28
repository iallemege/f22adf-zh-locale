# -*- coding: utf-8 -*-
"""Install 1998 Air Combat Designer into the game ADD_ONS folder."""
from __future__ import print_function
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_ui


def bundle_root():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


HERE = bundle_root()


def acd_dir():
    roots = [HERE]
    if getattr(sys, "frozen", False):
        roots.append(os.path.dirname(sys.executable))
    for root in roots:
        for name in ("acd", "_acd_src"):
            p = os.path.join(root, name)
            if os.path.isfile(os.path.join(p, "ADF_ACD.exe")):
                return p
    return None


def dest_dir():
    return os.path.join(apply_ui.GAME, "ADD_ONS")


def write_bat(path, cwd, exe):
    body = (
        "@echo off\r\n"
        "cd /d \"%s\"\r\n"
        "start \"\" \"%s\"\r\n"
    ) % (cwd, exe)
    with open(path, "wb") as f:
        f.write(body.encode("ascii", "replace"))


def write_howto(path):
    text = """F-22 ADF 空战设计器（ACD 1.0，1998 Game Tool Technologies）

这是独立的 Win32 工具，不经过 Steam。生成任务后要导入，游戏本体仍从 Steam 启动。

用法
1. 运行游戏目录下的「空战设计器.bat」，或 ADD_ONS\\ADF_ACD.exe。
2. 设好架次数、敌我比例、挂载、接近系数，点 Generate Scenario，再点 Save Scenario。
3. 关掉 ACD，运行「导入ACD任务.bat」（或再开安装器点「导入ACD」）。
4. 从 Steam 启动游戏 → 模拟训练 → 自由飞行 →「空战设计（ACD）」。

说明
- Save 会在 ADD_ONS 写出 adf_dmd.pdl/mdl/udl，以及一份会盖掉中文目录的 SIMULTOR.TXT。
  导入脚本会改 PDL 路径、拷进 pdl/mdl/udl，并删掉那份 SIMULTOR.TXT。
- 不要按 1998 年 readme 把 ADD_ONS\\SIMULTOR.TXT 留着，否则模拟训练列表会变回英文旧表。
- 弹窗可以关掉，不影响存盘。
- 非 F-22 外形只换模型，飞控仍是 F-22，也没有该机座舱。

原版说明见 ADD_ONS\\readme.txt。
"""
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))


def main():
    src = acd_dir()
    if not src:
        print("ACD missing: put ADF_ACD.exe in locale_zh\\acd\\ or locale_zh\\_acd_src\\")
        return 1
    dest = dest_dir()
    os.makedirs(dest, exist_ok=True)
    for fn in ("ADF_ACD.exe", "readme.txt", "adfacd.txt"):
        s = os.path.join(src, fn)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(dest, fn))
            print("acd", fn)
    write_howto(os.path.join(dest, "说明.txt"))
    write_howto(os.path.join(apply_ui.GAME, "空战设计器说明.txt"))
    exe = os.path.join(dest, "ADF_ACD.exe")
    write_bat(os.path.join(apply_ui.GAME, "空战设计器.bat"), dest, exe)
    write_bat(os.path.join(dest, "启动空战设计器.bat"), dest, exe)
    setup = sys.executable if getattr(sys, "frozen", False) else os.path.join(HERE, "setup_zh.py")
    if getattr(sys, "frozen", False):
        dest_setup = os.path.join(apply_ui.GAME, "F22ADF_zh_setup.exe")
        try:
            if os.path.normcase(os.path.abspath(setup)) != os.path.normcase(os.path.abspath(dest_setup)):
                shutil.copy2(setup, dest_setup)
            setup = dest_setup
        except OSError:
            pass
        bat = (
            "@echo off\r\n"
            "cd /d \"%~dp0\"\r\n"
            "\"%s\" --import-acd\r\n"
            "pause\r\n"
        ) % setup
    else:
        bat = (
            "@echo off\r\n"
            "cd /d \"%~dp0\"\r\n"
            "python \"%s\" --import-acd\r\n"
            "pause\r\n"
        ) % os.path.join(HERE, "setup_zh.py")
    for name in ("导入ACD任务.bat", "import_acd.bat"):
        with open(os.path.join(apply_ui.GAME, name), "wb") as f:
            f.write(bat.encode("ascii", "replace"))
    print("ACD ->", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
