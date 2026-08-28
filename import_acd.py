# -*- coding: utf-8 -*-
"""Copy ACD output into pdl/mdl/udl and register it under Simulator / Free Flight."""
from __future__ import print_function
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_ui
from apply_ui import backup_file, write_gbk, decode_src, read_bytes

PDL_NAME = "adf_dmd.pdl"
MDL_NAME = "adf_dmd.mdl"
UDL_NAME = "adf_dmd.udl"
BRIEF_STEM = "acd1"
LABEL = "空战设计（ACD）"
BRIEF_ID = 200
BITMAP_ID = 0


def find_generated():
    addons = os.path.join(apply_ui.GAME, "ADD_ONS")
    names = {}
    if not os.path.isdir(addons):
        return names
    for fn in os.listdir(addons):
        low = fn.lower()
        if low == PDL_NAME:
            names["pdl"] = os.path.join(addons, fn)
        elif low == MDL_NAME:
            names["mdl"] = os.path.join(addons, fn)
        elif low == UDL_NAME:
            names["udl"] = os.path.join(addons, fn)
    return names


def fix_pdl(path):
    text = decode_src(open(path, "rb").read())
    text = re.sub(r"MDL_FILE\s+\S+", "MDL_FILE " + MDL_NAME, text, count=1, flags=re.I)
    text = re.sub(r"UDL_FILE\s+\S+", "UDL_FILE " + UDL_NAME, text, count=1, flags=re.I)
    if "\r\n" not in text:
        text = text.replace("\n", "\r\n")
    open(path, "wb").write(text.encode("latin-1", "replace"))


def write_briefing():
    rel = os.path.join("briefing", BRIEF_STEM + ".txt")
    backup_file(rel)
    body = (
        "<c=r>空战设计（ACD）</c>\r\n"
        "\r\n"
        "由 1998 年 Air Combat Designer 生成的随机空战。\r\n"
        "架次、国籍与挂载以设计器存盘时为准。\r\n"
        "非 F-22 外形只换模型，飞控仍是 F-22。\r\n"
    )
    write_gbk(os.path.join(apply_ui.GAME, rel), body)
    print("briefing", rel)


def register_simultor():
    rel = os.path.join("f22data", "simultor.txt")
    backup_file(rel)
    path = os.path.join(apply_ui.GAME, rel)
    text = decode_src(read_bytes(path))
    line = 'MISSION 6 "%s" "%s"  "%s"  %d\tUSE_BITMAP %d' % (
        LABEL,
        PDL_NAME,
        BRIEF_STEM,
        BRIEF_ID,
        BITMAP_ID,
    )
    if "adf_dmd.pdl" in text.lower():
        text = re.sub(
            r'MISSION\s+6\s+"[^"]+"\s+"adf_dmd\.pdl"[^\n]*',
            line,
            text,
            count=1,
            flags=re.I,
        )
    else:
        text = re.sub(
            r'(MISSION_TYPE\s+1\s+"[^"]+"\s+)(\d+)',
            lambda m: m.group(1) + str(int(m.group(2)) + 1),
            text,
            count=1,
        )
        # append after the last Free Flight mission (type 1 block, before Flight Training)
        text = re.sub(
            r'(MISSION 5\s+"[^"]+"\s+"sim5\.pdl"[^\n]*)',
            r"\1\r\n" + line,
            text,
            count=1,
            flags=re.I,
        )
        if "adf_dmd.pdl" not in text.lower():
            text = text.rstrip() + "\r\n" + line + "\r\n"
    write_gbk(path, text)
    print("registered", LABEL)


def drop_override_catalog():
    addons = os.path.join(apply_ui.GAME, "ADD_ONS")
    n = 0
    for fn in ("SIMULTOR.TXT", "simultor.txt", "TD_TOURS.TXT", "TD_MISS.TXT", "MULTIPLA.TXT"):
        p = os.path.join(addons, fn)
        if os.path.isfile(p):
            bak = os.path.join(apply_ui.BACKUP, "ADD_ONS", fn)
            os.makedirs(os.path.dirname(bak), exist_ok=True)
            if not os.path.isfile(bak):
                shutil.copy2(p, bak)
            os.remove(p)
            n += 1
            print("removed override", fn)
    return n


def main():
    found = find_generated()
    if "pdl" not in found:
        print("no ADD_ONS\\adf_dmd.pdl — run 空战设计器.bat, Generate + Save, then import again")
        return 1
    for key, folder, name in (
        ("pdl", "pdl", PDL_NAME),
        ("mdl", "mdl", MDL_NAME),
        ("udl", "udl", UDL_NAME),
    ):
        if key not in found:
            print("missing", name)
            return 1
        dest = os.path.join(apply_ui.GAME, folder, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(found[key], dest)
        print("copy", dest)
    fix_pdl(os.path.join(apply_ui.GAME, "pdl", PDL_NAME))
    drop_override_catalog()
    write_briefing()
    register_simultor()
    print("import_acd done — Steam 启动后：模拟训练 → 自由飞行 → 空战设计（ACD）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
