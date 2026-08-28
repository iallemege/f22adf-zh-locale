# -*- coding: utf-8 -*-
"""F-22 ADF Simplified Chinese patch installer (tkinter)."""
from __future__ import print_function

import os
import shutil
import sys
import traceback

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
except ImportError:
    tk = None


def find_game():
    env = os.environ.get("F22ADF_GAME")
    if env and os.path.isfile(os.path.join(env, "adf.exe")):
        return env
    here = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    for cand in (here, os.path.dirname(here), os.path.join(here, "..")):
        cand = os.path.abspath(cand)
        if os.path.isfile(os.path.join(cand, "adf.exe")):
            return cand
    steam = r"D:\Steam\steamapps\common\F22ADF"
    if os.path.isfile(os.path.join(steam, "adf.exe")):
        return steam
    return None


def set_game(path):
    os.environ["F22ADF_GAME"] = path
    import apply_ui
    apply_ui.GAME = path


def install(game, log):
    set_game(game)
    import apply_all
    apply_all.GAME = game
    # apply_all uses apply_ui.GAME
    rc = apply_all.main()
    log("完成，退出码 %s。请从 Steam 启动游戏。" % rc)
    return rc == 0


def uninstall(game, log):
    set_game(game)
    import restore_english
    restore_english.GAME = game
    restore_english.BACKUP = os.path.join(os.path.dirname(restore_english.__file__), "en_backup")
    if getattr(sys, "frozen", False):
        restore_english.BACKUP = os.path.join(game, "locale_zh", "en_backup")
    restore_english.main()
    dll = os.path.join(game, "DINPUT8.dll")
    if os.path.isfile(dll):
        os.remove(dll)
        log("已删除 DINPUT8.dll")
    log("已还原英文数据。")
    return True


class App(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("F-22 ADF 简体中文补丁")
        self.root.geometry("560x420")
        self.game = tk.StringVar(value=find_game() or "")
        tk.Label(self.root, text="游戏目录（须含 adf.exe）", anchor="w").pack(fill="x", padx=12, pady=(12, 0))
        row = tk.Frame(self.root)
        row.pack(fill="x", padx=12, pady=4)
        tk.Entry(row, textvariable=self.game).pack(side="left", fill="x", expand=True)
        tk.Button(row, text="浏览…", command=self.browse).pack(side="left", padx=(8, 0))
        btns = tk.Frame(self.root)
        btns.pack(fill="x", padx=12, pady=8)
        tk.Button(btns, text="安装汉化", width=14, command=self.do_install).pack(side="left")
        tk.Button(btns, text="卸载汉化", width=14, command=self.do_uninstall).pack(side="left", padx=8)
        self.out = scrolledtext.ScrolledText(self.root, height=16, font=("Consolas", 9))
        self.out.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log("点「安装汉化」会写入 GBK 译文、黑体字库，并安装防闪退的 DINPUT8.dll。")
        self.log("WINDOW 标题保持英文，避免点开始任务时按 TITLE 找不到界面。")

    def log(self, s):
        self.out.insert("end", s + "\n")
        self.out.see("end")
        self.root.update_idletasks()

    def browse(self):
        path = filedialog.askopenfilename(title="选择 adf.exe", filetypes=[("adf.exe", "adf.exe"), ("All", "*.*")])
        if path:
            self.game.set(os.path.dirname(path))

    def game_dir(self):
        g = self.game.get().strip()
        if not g or not os.path.isfile(os.path.join(g, "adf.exe")):
            messagebox.showerror("错误", "找不到 adf.exe，请先浏览到游戏目录。")
            return None
        return g

    def do_install(self):
        g = self.game_dir()
        if not g:
            return
        try:
            self.log("安装到 " + g)
            if install(g, self.log):
                messagebox.showinfo("完成", "汉化已安装。从 Steam 启动游戏。")
        except Exception:
            self.log(traceback.format_exc())
            messagebox.showerror("失败", "安装出错，见窗口日志。")

    def do_uninstall(self):
        g = self.game_dir()
        if not g:
            return
        try:
            uninstall(g, self.log)
            messagebox.showinfo("完成", "已卸载汉化。")
        except Exception:
            self.log(traceback.format_exc())
            messagebox.showerror("失败", "卸载出错。需要 locale_zh\\en_backup。")

    def run(self):
        self.root.mainloop()


def main():
    if tk is None:
        print("需要 tkinter")
        return 1
    App().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
