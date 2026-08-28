# -*- coding: utf-8 -*-
"""F-22 ADF one-click installer (tkinter). No Python needed once frozen."""
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

VERSION = "1.3.0"


def icon_path():
    if getattr(sys, "frozen", False):
        p = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)), "adf.ico")
        if os.path.isfile(p):
            return p
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, "adf.ico")
    return p if os.path.isfile(p) else None


def apply_icon(root):
    ico = icon_path()
    if not ico:
        return
    try:
        root.iconbitmap(ico)
    except Exception:
        pass


class _LogStream(object):
    def __init__(self, write):
        self._write = write
        self._buf = ""

    def write(self, s):
        if not s:
            return
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            line = line.rstrip("\r")
            if line:
                self._write(line)

    def flush(self):
        if self._buf.strip():
            self._write(self._buf.rstrip())
        self._buf = ""


def find_game():
    env = os.environ.get("F22ADF_GAME")
    if env and os.path.isfile(os.path.join(env, "adf.exe")):
        return env
    here = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    guesses = [
        here,
        os.path.dirname(here),
        os.getcwd(),
        r"D:\Steam\steamapps\common\F22ADF",
        r"C:\Program Files (x86)\Steam\steamapps\common\F22ADF",
        r"C:\Program Files\Steam\steamapps\common\F22ADF",
    ]
    seen = set()
    for cand in guesses:
        cand = os.path.abspath(cand)
        key = os.path.normcase(cand)
        if key in seen:
            continue
        seen.add(key)
        if os.path.isfile(os.path.join(cand, "adf.exe")):
            return cand
    return None


def set_game(path):
    import apply_ui
    apply_ui.bind_game(path)


def _run_logged(fn, log):
    old = sys.stdout
    sys.stdout = _LogStream(log)
    try:
        return fn()
    finally:
        try:
            sys.stdout.flush()
        except Exception:
            pass
        sys.stdout = old


def copy_setup_exe(game, log):
    if not getattr(sys, "frozen", False):
        return
    dst = os.path.join(game, "F22ADF_zh_setup.exe")
    src = sys.executable
    try:
        if os.path.normcase(os.path.abspath(src)) != os.path.normcase(os.path.abspath(dst)):
            shutil.copy2(src, dst)
            log("安装器已复制到游戏目录")
    except OSError as e:
        log("未能复制安装器: %s" % e)


def install(game, log):
    set_game(game)
    import apply_all
    rc = _run_logged(apply_all.main, log)
    copy_setup_exe(game, log)
    log("完成，退出码 %s。请从 Steam 启动游戏。" % rc)
    return rc == 0


def uninstall(game, log):
    set_game(game)
    import restore_english
    _run_logged(restore_english.main, log)
    dll = os.path.join(game, "DINPUT8.dll")
    if os.path.isfile(dll):
        os.remove(dll)
        log("已删除 DINPUT8.dll")
    log("已还原英文数据。")
    return True


def import_acd(game, log):
    set_game(game)
    import install_acd
    import import_acd as imp
    _run_logged(install_acd.main, log)
    rc = _run_logged(imp.main, log)
    copy_setup_exe(game, log)
    return rc


class App(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("F-22 ADF 简体中文安装器  v%s" % VERSION)
        self.root.geometry("640x480")
        apply_icon(self.root)
        self.game = tk.StringVar(value=find_game() or "")
        tk.Label(self.root, text="游戏目录（须含 adf.exe）", anchor="w").pack(fill="x", padx=12, pady=(12, 0))
        row = tk.Frame(self.root)
        row.pack(fill="x", padx=12, pady=4)
        tk.Entry(row, textvariable=self.game).pack(side="left", fill="x", expand=True)
        tk.Button(row, text="浏览…", command=self.browse).pack(side="left", padx=(8, 0))
        btns = tk.Frame(self.root)
        btns.pack(fill="x", padx=12, pady=8)
        tk.Button(btns, text="安装全部", width=12, command=self.do_install).pack(side="left")
        tk.Button(btns, text="卸载汉化", width=12, command=self.do_uninstall).pack(side="left", padx=8)
        tk.Button(btns, text="导入ACD", width=12, command=self.do_import_acd).pack(side="left")
        tk.Button(btns, text="作弊说明", width=12, command=self.do_cheats).pack(side="left", padx=8)
        self.out = scrolledtext.ScrolledText(self.root, height=18, font=("Consolas", 9))
        self.out.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log("双击本程序即可，不需要安装 Python。")
        self.log("「安装全部」写入：界面中文、菜单 PCX、DINPUT8、手册、ACD / AGE / BAM、TrackIR 包。")
        self.log("窗口 TITLE/TEXT 查找键保持英文，避免点开始任务闪退。")
        self.log("游戏仍从 Steam 启动。ACD / AGE / BAM 本身不需要 Steam。")
        self.log("作弊：座舱里按住 Alt 再依次敲 D I D I T，然后可用 Alt+D / Shift+I 等。点「作弊说明」。")

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
                messagebox.showinfo("完成", "已安装。从 Steam 启动游戏。")
        except Exception:
            self.log(traceback.format_exc())
            messagebox.showerror("失败", "安装出错，见窗口日志。")

    def do_import_acd(self):
        g = self.game_dir()
        if not g:
            return
        try:
            rc = import_acd(g, self.log)
            if rc == 0:
                self.log("ACD 任务已导入。Steam → 模拟训练 → 自由飞行。")
                messagebox.showinfo("完成", "已导入空战设计任务。")
            else:
                self.log("还没有生成任务。先运行游戏目录「空战设计器.bat」，Save 后再点导入。")
        except Exception:
            self.log(traceback.format_exc())
            messagebox.showerror("失败", "导入出错，见窗口日志。")

    def do_cheats(self):
        g = self.game.get().strip()
        path = os.path.join(g, "作弊说明.txt") if g else ""
        if not os.path.isfile(path):
            try:
                import install_tools
                if g and os.path.isfile(os.path.join(g, "adf.exe")):
                    set_game(g)
                    install_tools.write_cheats(g)
            except Exception:
                path = ""
        if path and os.path.isfile(path):
            try:
                os.startfile(path)
                return
            except OSError:
                pass
        win = tk.Toplevel(self.root)
        win.title("作弊说明")
        apply_icon(win)
        box = scrolledtext.ScrolledText(win, width=72, height=24, font=("Consolas", 9))
        box.pack(fill="both", expand=True, padx=8, pady=8)
        try:
            import install_tools
            box.insert("end", install_tools.CHEATS_ZH)
        except Exception:
            box.insert("end", "座舱中按住 Alt，依次敲 D I D I T，松开后即开启作弊。")
        box.see("1.0")

    def do_uninstall(self):
        g = self.game_dir()
        if not g:
            return
        try:
            uninstall(g, self.log)
            messagebox.showinfo("完成", "已卸载汉化。")
        except Exception:
            self.log(traceback.format_exc())
            messagebox.showerror("失败", "卸载出错。需要游戏目录 locale_zh\\en_backup。")

    def run(self):
        self.root.mainloop()


def _alert(title, text):
    if tk is not None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, text)
        root.destroy()
    else:
        print(text)


def _cli_game():
    g = find_game()
    if not g:
        _alert("错误", "找不到 adf.exe。把本程序放到游戏目录，或先浏览安装。")
        return None
    return g


def _cli_window(title, work):
    """work(log) -> truthy on success."""
    if tk is None:
        return 0 if work(print) else 1
    root = tk.Tk()
    root.title(title)
    apply_icon(root)
    root.geometry("640x420")
    out = scrolledtext.ScrolledText(root, height=18, font=("Consolas", 9))
    out.pack(fill="both", expand=True, padx=12, pady=12)

    def log(s):
        out.insert("end", str(s) + "\n")
        out.see("end")
        root.update()

    ok = [False]

    def go():
        try:
            ok[0] = bool(work(log))
        except Exception:
            log(traceback.format_exc())
            ok[0] = False
        tk.Button(root, text="关闭", command=root.destroy).pack(pady=(0, 12))

    root.after(50, go)
    root.mainloop()
    return 0 if ok[0] else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--import-acd" in argv:
        g = _cli_game()
        if not g:
            return 1
        return _cli_window("导入 ACD", lambda log: import_acd(g, log) == 0)
    if "--uninstall" in argv:
        g = _cli_game()
        if not g:
            return 1
        return _cli_window("卸载汉化", lambda log: uninstall(g, log))
    if "--install" in argv:
        g = _cli_game()
        if not g:
            return 1
        return _cli_window("安装汉化", lambda log: install(g, log))
    if tk is None:
        print("需要图形界面，或使用 --install / --uninstall / --import-acd")
        return 1
    App().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
