# -*- coding: utf-8 -*-
"""Build DCS-style Chinese PDFs from manuals/*.md source."""
from __future__ import print_function

import os
import re
import shutil
from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.abspath(os.path.join(HERE, "..", ".."))
ZH_DIR = os.path.join(HERE, "zh")

NAVY = HexColor("#1b2838")
GOLD = HexColor("#c9a227")
WARN_BG = HexColor("#f8e6e6")
WARN_BD = HexColor("#a32020")
CAUT_BG = HexColor("#fff4d6")
CAUT_BD = HexColor("#b8860b")
NOTE_BG = HexColor("#e8eef5")
NOTE_BD = HexColor("#3d5a80")
RULE = HexColor("#c4c4c4")
ROW = HexColor("#f3f6f8")


def find_font():
    candidates = [
        os.path.join(GAME, "WINFONTS", "zh_ui.ttf"),
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    raise SystemExit("No Chinese TTF found (need SimHei / zh_ui.ttf)")


def register_fonts():
    path = find_font()
    if path.lower().endswith(".ttc"):
        pdfmetrics.registerFont(TTFont("ZH", path, subfontIndex=0))
    else:
        pdfmetrics.registerFont(TTFont("ZH", path))
    return path


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(
        name="CoverTitle", fontName="ZH", fontSize=22, leading=30,
        alignment=TA_CENTER, textColor=white, spaceAfter=6,
    ))
    s.add(ParagraphStyle(
        name="CoverSub", fontName="ZH", fontSize=12, leading=18,
        alignment=TA_CENTER, textColor=HexColor("#d8dde3"),
    ))
    s.add(ParagraphStyle(
        name="H1", fontName="ZH", fontSize=16, leading=22,
        textColor=NAVY, spaceBefore=16, spaceAfter=8,
    ))
    s.add(ParagraphStyle(
        name="H2", fontName="ZH", fontSize=13, leading=18,
        textColor=NAVY, spaceBefore=12, spaceAfter=6,
    ))
    s.add(ParagraphStyle(
        name="H3", fontName="ZH", fontSize=11, leading=16,
        textColor=HexColor("#2c3e50"), spaceBefore=9, spaceAfter=4,
    ))
    s.add(ParagraphStyle(
        name="Body", fontName="ZH", fontSize=9.5, leading=15,
        alignment=TA_JUSTIFY, textColor=black, spaceAfter=6,
        firstLineIndent=0,
    ))
    s.add(ParagraphStyle(
        name="Callout", fontName="ZH", fontSize=9.5, leading=14,
        textColor=black, spaceAfter=0,
    ))
    s.add(ParagraphStyle(
        name="CalloutTitle", fontName="ZH", fontSize=9.5, leading=13,
        textColor=NAVY, spaceAfter=3,
    ))
    s.add(ParagraphStyle(
        name="Cell", fontName="ZH", fontSize=8.2, leading=12,
        textColor=black,
    ))
    s.add(ParagraphStyle(
        name="CellHead", fontName="ZH", fontSize=8.2, leading=12,
        textColor=white,
    ))
    s.add(ParagraphStyle(
        name="Footer", fontName="ZH", fontSize=8, leading=10,
        textColor=HexColor("#555555"), alignment=TA_CENTER,
    ))
    s.add(ParagraphStyle(
        name="Pre", fontName="ZH", fontSize=8.5, leading=12,
        textColor=HexColor("#222222"), backColor=HexColor("#f4f4f4"),
        leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=8,
    ))
    return s


def esc(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font face='Courier' size='8'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def callout(title, body, bg, bd, sty):
    inner = [
        Paragraph("<b>%s</b>" % esc(title), sty["CalloutTitle"]),
        Paragraph(esc(body), sty["Callout"]),
    ]
    data = [[inner]]
    t = Table(data, colWidths=[160 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.4, bd),
        ("LINEBEFORE", (0, 0), (0, -1), 3.2, bd),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return KeepTogether([Spacer(1, 4), t, Spacer(1, 8)])


def parse_table(lines, sty):
    rows = []
    for line in lines:
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols and set("".join(cols)) <= set("-: "):
            continue
        rows.append(cols)
    if not rows:
        return None
    n = max(len(r) for r in rows)
    for r in rows:
        while len(r) < n:
            r.append("")
    width = 168 * mm
    col_w = [width / n] * n
    flow = []
    for i, r in enumerate(rows):
        st = sty["CellHead"] if i == 0 else sty["Cell"]
        flow.append([Paragraph(esc(c), st) for c in r])
    t = Table(flow, colWidths=col_w, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, -1), "ZH"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(flow)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ROW))
    t.setStyle(TableStyle(cmds))
    return t


def md_to_flow(md, sty):
    story = []
    lines = md.replace("\r\n", "\n").split("\n")
    i = 0
    para = []
    in_code = False
    code = []
    bullets = []

    def flush_para():
        if para:
            story.append(Paragraph(esc("".join(para).strip()), sty["Body"]))
            para.clear()

    def flush_bullets():
        if not bullets:
            return
        items = [ListItem(Paragraph(esc(b), sty["Body"]), leftIndent=12) for b in bullets]
        story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=16, bulletFontName="ZH"))
        bullets.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_para()
            flush_bullets()
            if in_code:
                story.append(Preformatted("\n".join(code), sty["Pre"]))
                code = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code.append(line)
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            flush_para()
            flush_bullets()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            t = parse_table(block, sty)
            if t:
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 8))
            continue

        m_box = re.match(r"^\*\*(警告|注意|注|提示)\*\*\s*[：:]?\s*(.*)$", stripped)
        if m_box:
            flush_para()
            flush_bullets()
            title, rest = m_box.group(1), m_box.group(2)
            body = rest
            i += 1
            extra = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith("|") and not re.match(r"^\*\*(警告|注意|注|提示)\*\*", lines[i].strip()):
                extra.append(lines[i].strip())
                i += 1
            if extra:
                body = (body + " " + " ".join(extra)).strip()
            colors = {
                "警告": (WARN_BG, WARN_BD),
                "注意": (CAUT_BG, CAUT_BD),
                "注": (NOTE_BG, NOTE_BD),
                "提示": (NOTE_BG, NOTE_BD),
            }
            bg, bd = colors[title]
            story.append(callout(title, body, bg, bd, sty))
            continue

        if stripped == "---":
            flush_para()
            flush_bullets()
            story.append(Spacer(1, 6))
            i += 1
            continue

        if stripped.startswith("# "):
            flush_para()
            flush_bullets()
            story.append(Paragraph(esc(stripped[2:]), sty["H1"]))
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            flush_bullets()
            story.append(CondPageBreak(40 * mm))
            story.append(Paragraph(esc(stripped[3:]), sty["H2"]))
            i += 1
            continue
        if stripped.startswith("### "):
            flush_para()
            flush_bullets()
            story.append(Paragraph(esc(stripped[4:]), sty["H3"]))
            i += 1
            continue

        if re.match(r"^[-*]\s+", stripped):
            flush_para()
            bullets.append(re.sub(r"^[-*]\s+", "", stripped))
            i += 1
            continue

        if not stripped:
            flush_para()
            flush_bullets()
            i += 1
            continue

        para.append(stripped)
        i += 1

    flush_para()
    flush_bullets()
    return story


def header_footer(canvas, doc, header_title):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 14.6 * mm, w, 1.2, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("ZH", 8)
    canvas.drawString(16 * mm, h - 9 * mm, header_title)
    canvas.drawRightString(w - 16 * mm, h - 9 * mm, "简体中文 · DCS 手册体例")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 12 * mm, w, 1.0, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("ZH", 8)
    canvas.drawString(16 * mm, 5 * mm, "仅供正版玩家对照阅读")
    canvas.drawRightString(w - 16 * mm, 5 * mm, str(doc.page))
    canvas.restoreState()


def cover_page(story, sty, title, subtitle, extra_lines):
    story.append(Spacer(1, 48 * mm))
    data = [[Paragraph(esc(title), sty["CoverTitle"])],
            [Paragraph(esc(subtitle), sty["CoverSub"])]]
    for line in extra_lines:
        data.append([Paragraph(esc(line), sty["CoverSub"])])
    t = Table(data, colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(t)
    story.append(PageBreak())


def build(md_path, pdf_path, header_title, cover):
    sty = styles()
    md = open(md_path, encoding="utf-8").read()
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=20 * mm, bottomMargin=18 * mm,
        title=header_title, author="F-22 ADF 简体中文补丁",
    )
    story = []
    cover_page(story, sty, cover["title"], cover["subtitle"], cover.get("extra", []))
    story.extend(md_to_flow(md, sty))

    def hf(canvas, doc_):
        header_footer(canvas, doc_, header_title)

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print("wrote", pdf_path)


def concat_manual():
    names = [
        "00_front.md",
        "01_legal.md",
        "02_getting_started.md",
        "03_overview.md",
        "04_avionics.md",
        "05_basic_flight.md",
        "06_aa_combat.md",
        "07_ag_combat.md",
        "08_maneuvers.md",
        "09_acmi.md",
        "10_views.md",
        "11_multiplayer.md",
        "12_awacs.md",
        "13_modes.md",
        "14_airfields.md",
        "15_recognition.md",
        "16_keyboards.md",
        "17_backmatter.md",
    ]
    parts = []
    missing = []
    for name in names:
        path = os.path.join(ZH_DIR, name)
        if os.path.isfile(path):
            parts.append(open(path, encoding="utf-8").read().rstrip() + "\n\n")
        else:
            missing.append(name)
    out = os.path.join(HERE, "flight_manual_zh.md")
    open(out, "w", encoding="utf-8").write("".join(parts))
    return out, missing


def main():
    font = register_fonts()
    print("font", font)
    os.makedirs(ZH_DIR, exist_ok=True)

    keys_md = os.path.join(HERE, "keys_guide_zh.md")
    keys_pdf = os.path.join(HERE, "F-22 ADF 按键对照 中文.pdf")
    build(
        keys_md, keys_pdf,
        "F-22: Air Dominance Fighter  按键对照",
        {
            "title": "F-22 ADF 按键对照",
            "subtitle": "简体中文 · 对齐 DCS 中文飞行手册体例",
            "extra": [
                "原文 Keys Guide English.pdf（Digital Image Design / Ocean，1997）",
                "译文仅供已购买正版的玩家对照使用",
            ],
        },
    )

    manual_md, missing = concat_manual()
    if missing:
        print("manual chapters still missing:", ", ".join(missing))
    if os.path.getsize(manual_md) > 80:
        manual_pdf = os.path.join(HERE, "F-22 ADF 飞行手册 中文.pdf")
        build(
            manual_md, manual_pdf,
            "F-22: Air Dominance Fighter  飞行手册",
            {
                "title": "F-22 Air Dominance Fighter",
                "subtitle": "飞行手册  简体中文译本",
                "extra": [
                    "对齐 DCS 中文飞行手册的术语与告警等级",
                    "据 1997 年印刷手册 OCR 转写，有异议时以英文原手册为准",
                    "Digital Image Design Ltd / Ocean Software Ltd",
                ],
            },
        )
        for src, name in (
            (keys_pdf, "F-22 ADF 按键对照 中文.pdf"),
            (os.path.join(HERE, "F-22 ADF 飞行手册 中文.pdf"), "F-22 ADF 飞行手册 中文.pdf"),
        ):
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(GAME, name))
                print("copied", name)
    else:
        dest = os.path.join(GAME, "F-22 ADF 按键对照 中文.pdf")
        shutil.copy2(keys_pdf, dest)
        print("copied keys only")


if __name__ == "__main__":
    main()
