# -*- coding: utf-8 -*-
"""Install AGE, BAM, TrackIR pack, and write cheat-mode notes."""
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

CHEATS_ZH = """F-22 ADF 作弊与调试（内置，无须改文件）

先开作弊模式（后面每一条都要先开这个）
1. 从 Steam 启动游戏。
2. 进任意任务，进入 F-22 座舱。
3. 按住 Alt 不放，依次敲：D I D I T。
4. 松开 Alt。此时作弊模式已打开。

重新挂弹与加油
Alt+D
多人游戏不可用。

无敌
Shift+I
不再吃伤害，可穿过建筑物。高速接地时只有机腹触地才完全免伤（原版就有这个毛病）。

悬停
Shift+U
飞机停在原地，仍可转动机头。

改时刻（不是跳过任务时间）
Alt+K  向前两小时，任务继续进行。
Shift+K  向前一分钟。

隐藏界面文字 / 截图
Alt+L  关掉左下角时钟等文字（方便截宣传图）。
Shift+F11  截图，存成游戏目录 SCRN0.LBM。重制版上这张图有时是坏的。

调试菜单
Alt+F10、Alt+F11  循环打开调试页：AI 航线（SmartView 里最好看）、地图标出所有机场、飞控统计等。

附加工具（安装器已拷到游戏目录，本身不经过 Steam）
- 空战设计器.bat → ADD_ONS\\ADF_ACD.exe
- 界面编辑器.bat → ADD_ONS\\AGE\\AGE.exe（1998 AGE）
- BAM任务管理.bat → 游戏目录 BAM.exe（1998 Basic ADF Manager）
- TrackIR 2009 补丁只放在 ADD_ONS\\TrackIR\\，是给原版 Total Air War 的，不要覆盖 2026 重制版文件。

AGE / BAM 若写出 ADD_ONS\\SIMULTOR.TXT，会盖掉模拟训练列表。用完后删掉该文件，或再开安装器点「导入ACD」。
"""


def tool_dir(*parts):
    roots = [HERE]
    if getattr(sys, "frozen", False):
        roots.append(os.path.dirname(sys.executable))
    for root in roots:
        p = os.path.join(root, "tools", *parts)
        if os.path.isdir(p) or os.path.isfile(p):
            return p
        p = os.path.join(root, "_tool_src", *parts)
        if os.path.isdir(p) or os.path.isfile(p):
            return p
    return None


def write_utf8(path, text):
    with open(path, "wb") as f:
        f.write(text.encode("utf-8-sig"))


def write_bat(path, cwd, exe):
    body = (
        "@echo off\r\n"
        "cd /d \"%s\"\r\n"
        "start \"\" \"%s\"\r\n"
    ) % (cwd, exe)
    with open(path, "wb") as f:
        f.write(body.encode("ascii", "replace"))


def copy_tree(src, dest):
    if not src or not os.path.isdir(src):
        return 0
    os.makedirs(dest, exist_ok=True)
    n = 0
    for dirpath, _, files in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        out = dest if rel == "." else os.path.join(dest, rel)
        os.makedirs(out, exist_ok=True)
        for fn in files:
            shutil.copy2(os.path.join(dirpath, fn), os.path.join(out, fn))
            n += 1
    return n


def ensure_game_folders(game):
    for name in ("ADD_ONS", "PDL", "KDL", "UDL", "MDL", "BRIEFING", "SCRIPTS", "NOT_USED"):
        os.makedirs(os.path.join(game, name), exist_ok=True)


def install_age(game):
    src = tool_dir("age")
    if not src or not os.path.isfile(os.path.join(src, "AGE.exe")):
        print("AGE missing")
        return 1
    dest = os.path.join(game, "ADD_ONS", "AGE")
    n = copy_tree(src, dest)
    write_utf8(
        os.path.join(dest, "说明.txt"),
        "ADF 界面编辑器 AGE（1998）\r\n\r\n"
        "独立工具，不经过 Steam。首次运行：Options → Settings，把 Game folder 指到本游戏目录（含 adf.exe）。\r\n"
        "Default Script folder 指到 ADD_ONS\\AGE。\r\n"
        "导出任务后若出现 ADD_ONS\\SIMULTOR.TXT，请删掉，否则模拟训练列表会被旧英文表盖掉。\r\n"
        "原版说明见 Age.txt、setup.txt。\r\n",
    )
    write_bat(os.path.join(game, "界面编辑器.bat"), dest, os.path.join(dest, "AGE.exe"))
    write_bat(os.path.join(dest, "启动AGE.bat"), dest, os.path.join(dest, "AGE.exe"))
    print("AGE", n, "files ->", dest)
    return 0


def install_bam(game):
    src = tool_dir("bam")
    if not src or not os.path.isfile(os.path.join(src, "BAM.exe")):
        print("BAM missing")
        return 1
    for fn in ("BAM.exe", "bam.wav", "readme.txt"):
        s = os.path.join(src, fn)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(game, fn))
            print("bam", fn)
    write_utf8(
        os.path.join(game, "BAM说明.txt"),
        "Basic ADF Manager 1.00（1998 Bimo）\r\n\r\n"
        "把附加任务解压到 SCRIPTS\\某文件夹，运行 BAM任务管理.bat。\r\n"
        "LOAD 载入，VERIFY 检查，ON 表示任务可供 ADF 使用。关 BAM 前保持 ON，再关 BAM，然后从 Steam 启动游戏。\r\n"
        "若写出 ADD_ONS\\SIMULTOR.TXT，用完请删，避免盖掉模拟训练列表。\r\n"
        "不想听启动音就把 BAM.WAV 改名或删掉。\r\n",
    )
    write_bat(os.path.join(game, "BAM任务管理.bat"), game, os.path.join(game, "BAM.exe"))
    return 0


def install_trackir(game):
    src = tool_dir("trackir")
    if not src or not os.path.isfile(os.path.join(src, "F22.dll")):
        print("TrackIR pack missing")
        return 1
    dest = os.path.join(game, "ADD_ONS", "TrackIR")
    n = copy_tree(src, dest)
    write_utf8(
        os.path.join(dest, "说明.txt"),
        "F22 TrackIR Patch v1.1（2009-06-18，Formski）\r\n\r\n"
        "这是给 1998/2009 年 F-22 Total Air War 的补丁：把 F22.dll 和 D3D 或 Glide 的 f22.dat 拷进 TAW 目录。\r\n"
        "2026 Steam 重制版 F-22 ADF 没有 f22.dat，也不是那套 exe。\r\n"
        "不要把这些文件覆盖进重制版游戏根目录，否则可能无法启动。\r\n"
        "若你同时装着原版 TAW：先在 NaturalPoint 软件里 Game Update，确认列表有 F22 Total Air War，再按 readme.txt 拷贝。\r\n"
        "F9（NaturalPoint 默认）关掉 TrackIR 后可用键盘环视和 F1 全屏平视显示器。\r\n",
    )
    write_utf8(
        os.path.join(game, "TrackIR补丁说明.txt"),
        "TrackIR 2009 补丁已放到 ADD_ONS\\TrackIR\\，只适用于原版 Total Air War，不要覆盖 2026 重制版。\r\n",
    )
    print("TrackIR", n, "files ->", dest)
    return 0


def write_cheats(game):
    write_utf8(os.path.join(game, "作弊说明.txt"), CHEATS_ZH)
    write_utf8(os.path.join(game, "ADD_ONS", "作弊说明.txt"), CHEATS_ZH)
    print("cheats -> 作弊说明.txt")


def main():
    game = apply_ui.GAME
    if not os.path.isfile(os.path.join(game, "adf.exe")):
        print("adf.exe not found in", game)
        return 1
    ensure_game_folders(game)
    install_age(game)
    install_bam(game)
    install_trackir(game)
    write_cheats(game)
    print("install_tools done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
