# F-22 ADF 简体中文本地化

Steam 2026 版 *F-22: Air Dominance Fighter*（app **3146140**）的简体中文补丁源码。不含游戏本体。

把本仓库放到游戏目录下的 `locale_zh\`，或在已有 `locale_zh` 里同步这些文件。

## 需要的环境

- 已安装的 Steam 版 F-22 ADF
- 中文 Windows（文本按 GBK / CP936）
- 系统有黑体（SimHei），界面字体用 `WINFONTS\zh_ui.ttf`

玩家只需要 `F22ADF_zh_setup.exe`。改译文或重新打包才需要 Python 3。

## 安装

运行 `F22ADF_zh_setup.exe`（Release 或本目录 `dist\`），选中带 `adf.exe` 的游戏目录，点「安装全部」。不要把 `options.cfg` 的 FEATURE 名称改成中文。

安装器会写入界面中文、菜单 PCX、`DINPUT8.dll`、中文手册和空战设计器。简报正文与任务目录保持英文（重制层 walker 画汉字会在点确定时闪退）。从 Steam 启动后，`gdi_zh.log` 应有 `inline hooks off (confirm-safe)`。

关掉汉字覆盖层：删除游戏根目录的 `DINPUT8.dll`。

## 空战设计器（ACD 1.0）

安装全部之后：`空战设计器.bat` → Generate + Save → 再开安装器点「导入ACD」（或 `导入ACD任务.bat`）。出现在模拟训练 / 自由飞行。同时装上 AGE（`界面编辑器.bat`）、BAM（`BAM任务管理.bat`），以及 `ADD_ONS\TrackIR\`（2009 TAW 补丁，勿覆盖重制版）。座舱作弊：按住 Alt 再敲 D I D I T，见 `作弊说明.txt`。

## 离线研究包

`python pack_offline.py` 打出 `locale_zh\\dist\\F22ADF_research_zh.zip`。解压到已有游戏目录即可装汉化与 ACD，不需要 Steam 登录。**运行** 2026 重制版仍要 Steam（或 Steam 离线模式）。本仓库不提供绕过 `steam_api` 的补丁。

重新编译包装（需要 32 位 TCC，见 `gdi_zh\build.bat`）：

```text
gdi_zh\build.bat
```

TCC 会给 `DirectInput8Create` 加上 stdcall 修饰名，`fix_export.py` 会改成游戏能找到的导出。

## 已覆盖

- 界面 GDD（按钮、标题、悬停提示）
- 座舱 HINTTEXT
- 简报正文、任务目录名保持英文（点确定进任务安全）
- 主菜单选项与加载条（exe 原文 + DINPUT8 画时替换，文件里的 TEXT 保持英文）
- 主菜单 / 制作人员 / 印章 PCX（`paint_pcx.py`）
- 术语见 `术语表.txt`（手册用词另见 `manuals/dcs_style.md`）
- 汉化教程：`汉化教程.md`（GDI / GBK / 覆盖层解码 / DINPUT8）
- 中文手册：`manuals\` 下的 Markdown 源，生成 `F-22 ADF 飞行手册 中文.pdf` 与 `F-22 ADF 按键对照 中文.pdf`（体例对齐 DCS 中文飞行手册）

## 仍是英文

- 简报正文、任务列表名（完整中文见 `briefing_cards\`）
- `icondesc.txt` 点阵按钮
- `adf.exe` 里写死的句子（如 `MISSION OBJECTIVES`）
- 机内字幕与语音、帮助 CHM（飞行手册与按键对照已另出中文 PDF）

## 还原

同一安装器点「卸载汉化」。开发者也可在源码目录运行 `restore_english.py` / `restore_overlay_en.py`（后者只把简报/目录改回英文）。

本补丁仅供已购买正版的玩家使用，请勿传播游戏数据文件。
