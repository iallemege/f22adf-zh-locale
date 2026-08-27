# 中文手册

体例对齐 DCS 中文飞行手册（官方《F/A-18C“大黄蜂”抢先体验指南》、Heatblur《F-14“雄猫”》），详见 `dcs_style.md`。

## 生成 PDF

需要 Python 3 与 `reportlab`，系统有黑体（或游戏目录 `WINFONTS\zh_ui.ttf`）。

```text
pip install reportlab
python build_pdfs.py
```

会写出：

- `F-22 ADF 按键对照 中文.pdf`
- `F-22 ADF 飞行手册 中文.pdf`（需 `zh\` 下各章齐备）

并复制到游戏根目录（与 `Manual English.pdf` 同级）。

## 源文件

| 文件 | 内容 |
| --- | --- |
| `keys_guide_zh.md` | 按键对照全文 |
| `zh\00_front.md` … `17_backmatter.md` | 飞行手册分章 |
| `../manual_src\` | 英文 OCR 底稿，仅供译者，不要整本上传公开仓库 |

原文版权归 Digital Image Design Ltd / Ocean Software Ltd。译本仅供正版玩家对照。
