# -*- coding: utf-8 -*-
"""Render Chinese briefing cards (PNG+HTML) and burn titles onto scenario PCX thumbnails."""
from __future__ import print_function
import os, re, shutil, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_ui import GAME, BACKUP
from bodies_sim import BODIES as SIM
from bodies_tod import BODIES as TOD
from bodies_rs import BODIES as RS

LOC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(LOC, "briefing_cards")
FONT_PATH = os.path.join(GAME, "WINFONTS", "zh_ui.ttf")
if not os.path.isfile(FONT_PATH):
    FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"

TAG_RE = re.compile(r"</?c(?:=[a-z])?>|</?u>|</?b>|</?h>", re.I)
TITLE_RE = re.compile(r"<c=r>([^<]+)</c>", re.I)


def parse_lines(raw):
    title = ""
    m = TITLE_RE.search(raw)
    if m:
        title = m.group(1).strip()
    lines = []
    for line in raw.replace("\r\n", "\n").split("\n"):
        plain = TAG_RE.sub("", line).replace("\t", " ").rstrip()
        color = (220, 220, 220)
        if "<c=r>" in line.lower():
            color = (220, 48, 48)
        elif "<c=g>" in line.lower():
            color = (80, 200, 80)
        lines.append((plain, color))
    while lines and not lines[0][0]:
        lines.pop(0)
    while lines and not lines[-1][0]:
        lines.pop()
    return title, lines


def wrap(draw, text, font, width):
    if not text:
        return [""]
    out, cur = [], ""
    for ch in text:
        trial = cur + ch
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = ch
    if cur:
        out.append(cur)
    return out or [""]


def render_card(fn, raw, font_title, font_body):
    title, lines = parse_lines(raw)
    W, margin = 720, 28
    # measure
    tmp = Image.new("RGB", (W, 64), (0, 0, 0))
    d0 = ImageDraw.Draw(tmp)
    blocks = []
    h = 36
    for plain, color in lines:
        if not plain:
            h += 10
            blocks.append(("", color, 10))
            continue
        font = font_title if color == (220, 48, 48) else font_body
        for part in wrap(d0, plain, font, W - margin * 2):
            lh = 36 if font is font_title else 26
            blocks.append((part, color, lh))
            h += lh
    h = max(h + 40, 480)
    img = Image.new("RGB", (W, h), (12, 14, 18))
    dr = ImageDraw.Draw(img)
    dr.rectangle((0, 0, W - 1, h - 1), outline=(40, 70, 50))
    y = 20
    for part, color, lh in blocks:
        if part:
            font = font_title if color == (220, 48, 48) else font_body
            dr.text((margin, y), part, font=font, fill=color)
        y += lh
    dest = os.path.join(OUT, fn.replace(".txt", ".png"))
    img.save(dest, "PNG")
    return title, dest


def catalog_pcx():
    """briefing stem (tod1) -> list of pcx relative paths."""
    mapping = {}
    for cat in ("simultor.txt", "td_miss.txt", "td_tours.txt", "multipla.txt", "arcade.txt"):
        path = os.path.join(GAME, "f22data", cat)
        if not os.path.isfile(path):
            continue
        text = open(path, "rb").read().decode("latin-1")
        bitmaps = {}
        for m in re.finditer(r'DEFINE_BITMAP\s+(\d+)\s+[^\n"]*"([^"]+\.pcx)"', text, re.I):
            bitmaps[int(m.group(1))] = m.group(2).replace("/", "\\").lstrip("\\")
        for m in re.finditer(
            r'MISSION\s+\d+\s+"[^"]+"\s+"[^"]+"\s+"([^"]+)"[^\n]*USE_BITMAP\s+(\d+)',
            text,
            re.I,
        ):
            stem = m.group(1).split("\\")[-1].split("/")[-1]
            bid = int(m.group(2))
            if bid in bitmaps:
                mapping.setdefault(stem.lower(), []).append(bitmaps[bid])
        for m in re.finditer(r'END_TOUR\s+\d+\s+"([^"]+\.pcx)"\s+"([^"]+)"', text, re.I):
            stem = m.group(2).replace(".txt", "")
            mapping.setdefault(stem.lower(), []).append(m.group(1).replace("/", "\\").lstrip("\\"))
    return mapping


def burn_title(pcx_rel, title, font):
    src = os.path.join(GAME, pcx_rel)
    if not os.path.isfile(src) or not title:
        return False
    bak = os.path.join(BACKUP, pcx_rel)
    os.makedirs(os.path.dirname(bak), exist_ok=True)
    if not os.path.isfile(bak):
        shutil.copy2(src, bak)
    im = Image.open(src)
    pal = im.convert("P")
    rgb = pal.convert("RGB")
    w, h = rgb.size
    bar_h = 22
    dr = ImageDraw.Draw(rgb, "RGB")
    dr.rectangle((0, h - bar_h, w, h), fill=(8, 12, 10))
    # shrink title to fit
    t = title
    while dr.textlength(t, font=font) > w - 8 and len(t) > 1:
        t = t[:-1]
    dr.text((4, h - bar_h + 2), t, font=font, fill=(240, 240, 240))
    out = rgb.quantize(palette=pal, dither=0)
    out.save(src, format="PCX")
    return True


def write_html(items):
    rows = []
    for fn, title, png in items:
        rel = os.path.basename(png)
        rows.append(
            '<div class="card"><h2 id="%s">%s <small>%s</small></h2><img src="%s" alt="%s"></div>'
            % (fn.replace(".txt", ""), title or fn, fn, rel, title)
        )
    html = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>F-22 ADF 中文任务简报</title>
<style>
body{margin:0;background:#0b0d10;color:#ddd;font-family:SimHei,Microsoft YaHei,sans-serif}
header{position:sticky;top:0;background:#111;padding:12px 20px;border-bottom:1px solid #333}
input{width:280px;padding:6px 8px;background:#1a1a1a;border:1px solid #444;color:#eee}
main{padding:16px;display:flex;flex-direction:column;gap:24px;align-items:center}
img{max-width:100%%;height:auto;border:1px solid #2a3a30}
h2{margin:0 0 8px;font-size:18px} small{color:#888;font-weight:normal}
</style></head><body>
<header>F-22 ADF 中文任务简报（游戏内情报区无法显示汉字，在此查看）
<input id="q" placeholder="搜索任务名 / 文件名" oninput="
const v=this.value.trim();
document.querySelectorAll('.card').forEach(c=>c.style.display=c.innerText.includes(v)?'':'none')"></header>
<main>
%s
</main></body></html>
""" % "\n".join(rows)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)


def main():
    os.makedirs(OUT, exist_ok=True)
    font_title = ImageFont.truetype(FONT_PATH, 28)
    font_body = ImageFont.truetype(FONT_PATH, 18)
    font_thumb = ImageFont.truetype(FONT_PATH, 16)
    bodies = {}
    bodies.update(SIM)
    bodies.update(TOD)
    bodies.update(RS)
    pcx_map = catalog_pcx()
    items = []
    burned = set()
    n_pcx = 0
    for fn, raw in sorted(bodies.items()):
        title, dest = render_card(fn, raw, font_title, font_body)
        items.append((fn, title, dest))
        stem = fn.replace(".txt", "").lower()
        for rel in pcx_map.get(stem, []):
            key = rel.lower()
            if key in burned:
                continue
            if burn_title(rel, title, font_thumb):
                burned.add(key)
                n_pcx += 1
    write_html(items)
    print("cards", len(items), "thumbnails", n_pcx, "html", os.path.join(OUT, "index.html"))


if __name__ == "__main__":
    main()
