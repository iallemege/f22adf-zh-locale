# F-22 ADF 简体中文本地化

Steam 2026 版 *F-22: Air Dominance Fighter*（app **3146140**）的简体中文补丁源码。不含游戏本体。

把本仓库放到游戏目录下的 `locale_zh\`，或在已有 `locale_zh` 里同步这些文件。

## 需要的环境

- 已安装的 Steam 版 F-22 ADF
- 中文 Windows（文本按 GBK / CP936）
- 系统有黑体（SimHei），界面字体用 `WINFONTS\zh_ui.ttf`
- Python 3（用于写入译文）

## 安装

**推荐：** 运行 Release 里的 `F22ADF_zh_setup.exe`，选中带 `adf.exe` 的游戏目录，点「安装汉化」。不要把 `options.cfg` 的 FEATURE 名称改成中文。

或手动：

1. 将 `gdi_zh\DINPUT8.dll` 复制到游戏根目录（与 `adf.exe` 同级）。这是 32 位 DirectInput 代理，会把简报覆盖层的 GBK 汉字画出来。点「开始任务」闪退时请换 Release 里加固过的 DLL（延迟 hook、保存 esi/edi、只认汉字 GBK）。
2. 在 `locale_zh` 下执行 `python apply_all.py`，或分步：

```text
python apply_ui.py
python apply_briefing_bodies.py
python apply_briefing_labels.py
python apply_catalogs_gbk.py
python apply_finish.py
```

3. `windesc.win` 里 `CREATE_SYS_FONT` 只能有 3 行，且 `DEFINE_SYS_FONT` 的 STYLE 必须是 `SimHei`。不要翻译 `options.cfg` 里的 FEATURE 名称。
4. 从 Steam 启动游戏。根目录应出现 `gdi_zh.log`。

关掉汉字覆盖层：删除游戏根目录的 `DINPUT8.dll`。

重新编译包装（需要 32 位 TCC，见 `gdi_zh\build.bat`）：

```text
gdi_zh\build.bat
```

TCC 会给 `DirectInput8Create` 加上 stdcall 修饰名，`fix_export.py` 会改成游戏能找到的导出。

## 已覆盖

- 界面 GDD（按钮、标题、悬停提示）
- 座舱 HINTTEXT
- 简报正文、任务目录名（GBK + `DINPUT8.dll`）
- 术语见 `术语表.txt`（手册用词另见 `manuals/dcs_style.md`）
- 汉化教程：`汉化教程.md`（GDI / GBK / 覆盖层解码 / DINPUT8）
- 中文手册：`manuals\` 下的 Markdown 源，生成 `F-22 ADF 飞行手册 中文.pdf` 与 `F-22 ADF 按键对照 中文.pdf`（体例对齐 DCS 中文飞行手册）

## 仍是英文

- 主菜单 PCX 上的字
- `icondesc.txt` 点阵按钮
- `adf.exe` 里写死的句子（如 `MISSION OBJECTIVES`）
- 机内字幕与语音、帮助 CHM（飞行手册与按键对照已另出中文 PDF）

## 还原

```text
python restore_english.py
python restore_overlay_en.py
```

后者只把简报/目录改回英文，界面中文保留。

本补丁仅供已购买正版的玩家使用，请勿传播游戏数据文件。
