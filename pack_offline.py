# -*- coding: utf-8 -*-
"""Build a portable research zip: Chinese patch + ACD. Does not crack Steam."""
from __future__ import print_function
import os
import zipfile
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist", "F22ADF_research_zh.zip")

INCLUDE_EXT = {".py", ".md", ".txt", ".dll", ".def", ".bat", ".pdf", ".c"}
INCLUDE_NAMES = {"ADF_ACD.exe"}
SKIP_DIR = {
    "en_backup",
    "briefing_cards",
    "_pcx_preview",
    "__pycache__",
    "tcc",
    "tcc_dl",
    "build",
    "dist",
    "manual_src",
}


def want(rel, fn):
    if fn in INCLUDE_NAMES:
        return True
    ext = os.path.splitext(fn)[1].lower()
    if ext not in INCLUDE_EXT:
        return False
    if fn.startswith("_") and ext in (".py", ".txt"):
        return False
    return True


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "README_OFFLINE.txt",
            (
                "F-22 ADF 研究用离线包（汉化 + ACD 1.0）\n"
                "不含游戏本体，也不绕过 Steam 启动校验。\n"
                "\n"
                "安装（不需要 Steam 登录）\n"
                "1. 解压后把整个 locale_zh 放到已有游戏目录（与 adf.exe 同级）。\n"
                "2. 运行 python locale_zh\\setup_zh.py，或 python locale_zh\\apply_all.py。\n"
                "3. 空战设计器：空战设计器.bat → Generate/Save → 导入ACD任务.bat。\n"
                "\n"
                "运行游戏\n"
                "2026 重制版 adf.exe 会调用 steam_api.dll，须从 Steam 启动，或 Steam 离线模式。\n"
                "本包不提供去 Steam 的破解。\n"
            ).encode("utf-8"),
        )
        for dirpath, dirs, files in os.walk(HERE):
            dirs[:] = [d for d in dirs if d not in SKIP_DIR and d != ".git"]
            for fn in files:
                if not want(os.path.relpath(os.path.join(dirpath, fn), HERE), fn):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.join("locale_zh", os.path.relpath(full, HERE))
                z.write(full, rel)
                n += 1
    print("wrote", OUT, "files", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
