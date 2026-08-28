# -*- coding: utf-8 -*-
"""Burn Chinese onto 8-bit menu/credits/stamp PCX. Always paints from en_backup."""
from __future__ import print_function
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_ui

def font_path():
    p = os.path.join(apply_ui.GAME, "WINFONTS", "zh_ui.ttf")
    if os.path.isfile(p):
        return p
    return r"C:\Windows\Fonts\simhei.ttf"

# Circular photos only. Labels are GDI TEXT in adfmenu.txt (MENU_FONT 3 / SimHei).
MENU_BUTTONS_RESTORE = [
    r"pcx\mainmenu\menuadf\sim.pcx",
    r"pcx\mainmenu\menuadf\quickcom.pcx",
    r"pcx\mainmenu\menuadf\tourduty.pcx",
    r"pcx\mainmenu\menuadf\multipla.pcx",
    r"pcx\mainmenu\menuadf\acmi.pcx",
    r"pcx\mainmenu\menuadf\options.pcx",
    r"pcx\mainmenu\menuadf\credits.pcx",
    r"pcx\mainmenu\menuadf\quit.pcx",
    r"pcx\mainmenu\menuadf\help.pcx",
    r"pcx\mainmenu\menuadf\f22demo.pcx",
]

# White subtitle baked under the F22 logo.
BACKDROP = (r"pcx\mainmenu\menuadf\backdrop.pcx", (170, 336, 590, 368), "空中霸权战机", 20)
CREDITS = (r"pcx\credits\credits.pcx", (280, 80, 490, 102), "空中霸权战机", 13)

# stamps.pcx is three 64x64 cells: PASSED / FAILED / DENIED
STAMPS = (r"pcx\stamps\stamps.pcx", [("通过", (48, 210, 48)), ("失败", (210, 48, 48)), ("拒绝", (235, 235, 235))])


def font(size):
    return ImageFont.truetype(font_path(), size)


def original(rel):
    src = os.path.join(apply_ui.GAME, rel)
    bak = os.path.join(apply_ui.BACKUP, rel)
    if not os.path.isfile(src):
        return None, None
    os.makedirs(os.path.dirname(bak), exist_ok=True)
    if not os.path.isfile(bak):
        shutil.copy2(src, bak)
    return Image.open(bak), src


def save_pcx(rgb, pal, dest):
    rgb.quantize(palette=pal, dither=0).save(dest, format="PCX")


def fit_text(draw, text, face, max_w):
    t = text
    while t and draw.textlength(t, font=face) > max_w and len(t) > 1:
        t = t[:-1]
    return t


def paint_button(rel, label):
    im, dest = original(rel)
    if im is None:
        print("missing", rel)
        return False
    pal = im.convert("P")
    rgb = pal.convert("RGB")
    w, h = rgb.size
    bar_h = 20
    dr = ImageDraw.Draw(rgb)
    dr.rectangle((0, h - bar_h, w, h), fill=(8, 12, 10))
    face = font(15)
    t = fit_text(dr, label, face, w - 8)
    tw = dr.textlength(t, font=face)
    x = max(4, int((w - tw) / 2))
    y = h - bar_h + 2
    dr.text((x + 1, y + 1), t, font=face, fill=(0, 0, 0))
    dr.text((x, y), t, font=face, fill=(240, 240, 240))
    save_pcx(rgb, pal, dest)
    return True


def cover_band(rgb, box):
    x0, y0, x1, y1 = box
    px = rgb.load()
    w, h = rgb.size
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(w, x1)
    y1 = min(h, y1)
    # sample camo from below the letters so the F22 outline is not cloned down
    src_y0 = min(h - 1, y1 + 3)
    src_y1 = min(h, src_y0 + 8)
    if src_y1 <= src_y0:
        src_y0 = max(0, y0 - 8)
        src_y1 = max(src_y0 + 1, y0)
    span = max(1, src_y1 - src_y0)
    for y in range(y0, y1):
        sy = src_y0 + ((y - y0) % span)
        for x in range(x0, x1):
            px[x, y] = px[x, sy]
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if r > 170 and g > 170 and b > 170:
                px[x, y] = px[x, src_y0]


def paint_subtitle(rel, box, label, size):
    im, dest = original(rel)
    if im is None:
        print("missing", rel)
        return False
    pal = im.convert("P")
    rgb = pal.convert("RGB")
    cover_band(rgb, box)
    dr = ImageDraw.Draw(rgb)
    face = font(size)
    x0, y0, x1, y1 = box
    t = fit_text(dr, label, face, x1 - x0 - 4)
    tw = dr.textlength(t, font=face)
    try:
        bbox = face.getbbox(t)
        th = bbox[3] - bbox[1]
        to = bbox[1]
    except AttributeError:
        th, to = size, 0
    x = x0 + max(0, int((x1 - x0 - tw) / 2))
    y = y0 + max(0, int((y1 - y0 - th) / 2) - to)
    dr.text((x + 1, y + 1), t, font=face, fill=(0, 0, 0))
    dr.text((x, y), t, font=face, fill=(248, 248, 248))
    save_pcx(rgb, pal, dest)
    return True


def paint_stamps(rel, cells):
    im, dest = original(rel)
    if im is None:
        print("missing", rel)
        return False
    pal = im.convert("P")
    rgb = pal.convert("RGB")
    cell = 64
    face = font(16)
    for i, (label, ink) in enumerate(cells):
        x0 = i * cell
        tile = rgb.crop((x0, 0, x0 + cell, cell)).convert("RGBA")
        # smear the diagonal English word with nearby stamp ink
        px = tile.load()
        for y in range(18, 48):
            for x in range(8, 56):
                r, g, b, a = px[x, y]
                # letter strokes are brighter / more saturated than the wash
                if r + g + b > 120:
                    nx, ny = min(cell - 1, x + 6), min(cell - 1, max(0, y - 8))
                    px[x, y] = px[nx, ny]
        overlay = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        tw = od.textlength(label, font=face)
        tx, ty = (cell - tw) / 2, 22
        od.text((tx + 1, ty + 1), label, font=face, fill=(0, 0, 0, 220))
        od.text((tx, ty), label, font=face, fill=ink + (255,))
        overlay = overlay.rotate(28, resample=Image.BICUBIC, expand=False)
        tile = Image.alpha_composite(tile, overlay)
        rgb.paste(tile.convert("RGB"), (x0, 0))
    save_pcx(rgb, pal, dest)
    return True


def main():
    if not os.path.isfile(font_path()):
        print("WARNING: no SimHei at", font_path())
        return 1
    n = 0
    for rel in MENU_BUTTONS_RESTORE:
        bak = os.path.join(apply_ui.BACKUP, rel)
        dst = os.path.join(apply_ui.GAME, rel)
        if os.path.isfile(bak) and os.path.isfile(dst):
            shutil.copy2(bak, dst)
            n += 1
            print("restore", rel)
    rel, box, label, size = BACKDROP
    if paint_subtitle(rel, box, label, size):
        n += 1
        print("backdrop", label)
    rel, box, label, size = CREDITS
    if paint_subtitle(rel, box, label, size):
        n += 1
        print("credits", label)
    rel, cells = STAMPS
    if paint_stamps(rel, cells):
        n += 1
        print("stamps")
    print("paint_pcx", n, "files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
