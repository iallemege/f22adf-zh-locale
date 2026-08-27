# F-22 ADF 手册汉化体例（对齐 DCS 中文飞行手册）

本文规定简体中文飞行手册与按键对照的用词、语气和排版。游戏内界面仍用 `术语表.txt`；手册比界面更书面、更接近 Eagle Dynamics / Heatblur 中文手册。

版权：译文仅供已购买正版的玩家对照阅读。原文版权归 Digital Image Design Ltd / Ocean Software Ltd 及其权利继受人所有。有异议时以英文原手册为准。

## 语气

- 用书面技术汉语，不用攻略腔、直播腔、网络缩写。
- 陈述程序用现在时祈使或客观叙述：先……，再……，然后……。
- 不要把 1997 年 DID 的设定改写成真实 F-22A 的现行条令。凡属游戏抽象，写明「本模拟中……」。
- 扫描 OCR 里的 `lnterface`、`Ouick`、`ta`、`af`、`an`（on）、`010`/`Dl□`（DID）等一律按语义还原后再译，不要把错字译进去。

## 告警等级（与 DCS / 民航手册对齐）

| 原文 | 手册标签 | 用法 |
| --- | --- | --- |
| WARNING / HEALTH WARNING | **警告** | 可能造成人员伤害或必须立即中止的情况 |
| CAUTION | **注意** | 可能损坏设备、任务失败或操作错误 |
| NOTE | **注** | 补充说明、操作提示，不构成告警 |
| Advisory | **提示** | 状态提示，低于注意 |

正文里第一次出现时写全称并括注英文，例如：平视显示器（HUD）。后文可单独用缩写。

座舱开关、灯、MFD 按钮上的英文刻字**保留原文**，必要时后附中文：`MASTER CAUTION`（主警戒）。不要把刻字翻译成无法在机内对上的中文。

## 固定译名

与 DCS《F/A-18C“大黄蜂”抢先体验指南》、Heatblur《F-14“雄猫”中文飞行手册》保持同族：

| 英文 | 手册用词 | 不要写成 |
| --- | --- | --- |
| cockpit | 驾驶舱 | 座舱（界面选项可仍用「座舱反射」） |
| stick / control column | 驾驶杆 | 摇杆（硬件外设才叫飞行摇杆） |
| throttle | 油门 | 节流阀（民航手册可用，本手册统一油门） |
| HUD | 平视显示器（HUD） | 抬头显示 |
| HMD | 头盔显示器（HMD） | 头盔瞄准具（本机不是 HMS） |
| MFD | 多功能显示器（MFD） | 多功能屏幕 |
| ILS | 仪表着陆系统（ILS） | 盲降（可在括注中出现一次） |
| waypoint | 航路点 | 路点、导航点 |
| autopilot | 自动驾驶仪 | 自动驾驶（可作动词） |
| landing gear | 起落架 | 轮子、起落架轮 |
| airbrake / speedbrake | 减速板 | 空气刹车（首次可括注） |
| toe brakes | 脚蹬刹车 | 脚趾刹车 |
| nose wheel steering | 前轮转弯 | 鼻轮转向 |
| canopy | 座舱盖 | 座舱罩 |
| bay doors | 武器舱门 | 弹舱门（可并列一次） |
| chaff | 箔条 | 干扰箔 |
| flare | 红外诱饵弹 | 热焰弹 |
| jettison | 抛离 | 丢弃、扔掉 |
| pickle / pickle button | 投放（按钮） | 酸黄瓜（禁止） |
| lock / padlock | 锁定 / 视觉锁定（padlock） | pad锁 |
| wingman | 僚机 | 队友、翅膀人 |
| shoot list | 射击清单 | 射杀列表 |
| EMCON | 电磁控制（EMCON） | 电磁静默（EMCON 1 才接近） |
| BVR | 视距外（BVR） | 超视距（可作同义，首次用视距外） |
| WVR / ACM | 视距内 / 空战机动（ACM） | 狗斗（禁止作正文） |
| RoE | 交战规则（RoE） | 交战守则 |
| AWACS | 预警机（AWACS） | 空中预警机（可作全称一次） |
| JSTARS | 联合星（JSTARS） | — |
| IRST | 红外搜索跟踪（IRST） | 红外雷达 |
| RHAW / RWR | 雷达寻的告警（RHAW） | 雷达警告器 |
| MAW | 导弹逼近告警（MAW） | — |
| IFDL | 编队内数据链（IFDL） | — |
| LANTIRN | LANTIRN | 不要意译成产品名 |
| NTIDS / DTINS | 北约目标识别符号 / 交互目标符号 | — |
| FEBA | 战斗前沿（FEBA） | 前线 |
| CAP / SEAD / BAI / CAS | 战斗空中巡逻 / 压制敌防空 / 战场遮断 / 近距空中支援 | 全称后括注缩写 |
| Quick Combat | 快速作战 | 街机（仅可在说明性括注） |
| Simulator | 模拟训练 | 模拟器（易与整个游戏混淆） |
| Tour of Duty | 战区巡航 | 战役、巡航任务（首次写全） |
| ACMI | ACMI（空战机动仪表记录） | 回放器 |
| time warp / time skip | 时间跳跃 / 时间加速 | 跳时 |
| military power | 全军用推力 | 军用功率 |
| afterburner / max | 加力 / 最大推力 | 本机油门到 140% 时写「加力（本模拟）」 |
| indicated airspeed | 指示空速 | 表速（可括注） |
| pitch ladder | 俯仰梯 | 俯仰梯子 |
| velocity vector | 速度矢量 | 飞行轨迹符 |
| G / blackout / redout | 过载 / 黑视 / 红视 | 黑屏 |
| night vision | 夜视 | 夜视仪（有护目镜时） |

## 型号与绰号

- 飞机、导弹、炸弹的北约/美制编号一律保留：F-22、AIM-9X、AIM-120C、AIM-120R、AGM-65、AGM-84、AGM-88、GBU、JDAM。
- 绰号用中文引号，且不替代型号：AIM-9X“响尾蛇”、AGM-65“小牛”、AGM-84“捕鲸叉”、AGM-88 HARM（反辐射导弹）。
- AMRAAM 保留缩写，首次可写 AIM-120 AMRAAM。
- 地名用通行译名，见 `术语表.txt`。

## 单位

- 保留原手册单位：英尺（ft）、海里（nm）、英里（miles）、节（kt，若原文出现）。
- 第一次在该章出现英制时，可在括号给近似公制，例如 50 miles（约 80 km）。不要全文改成公制，以免和机内刻度对不上。

## 按键与界面

- 键位用等宽或原样大写：`SHIFT+H`、`TAB`、`BACKSPACE`。组合键用 `+`，不用「加」。
- 菜单路径用「→」：简报 → 确定。
- 游戏按钮名若界面已汉化，手册写中文并在首次括注英文：快速作战（Quick Combat）。

## 章节标题习惯（DCS）

优先用：简介、驾驶舱简介、系统概述、武器系统、正常程序、作战使用、应急处置、缩写与术语。

本手册仍按 1997 年原书目录翻译，不重排章节，以便对照英文 PDF 页码。
