# -*- coding: utf-8 -*-
"""Apply Chinese UI strings, CJK font, and backups. Encode game files as GBK."""
from __future__ import print_function
import os, re, shutil, sys

_ALIAS_MODULES = (
    "paint_pcx",
    "restore_english",
    "apply_finish",
    "import_acd",
    "repair_ui",
    "apply_briefing_bodies",
    "apply_briefing_labels",
    "apply_catalogs_gbk",
    "render_briefing_cards",
    "to_utf8_overlay",
    "apply_all",
)


def bind_game(path):
    """Point GAME/BACKUP at a folder that contains adf.exe."""
    global GAME, BACKUP, LOC
    GAME = os.path.abspath(path)
    os.environ["F22ADF_GAME"] = GAME
    LOC = os.path.join(GAME, "locale_zh")
    os.makedirs(LOC, exist_ok=True)
    BACKUP = os.path.join(LOC, "en_backup")
    os.makedirs(BACKUP, exist_ok=True)
    for name in _ALIAS_MODULES:
        mod = sys.modules.get(name)
        if not mod:
            continue
        if hasattr(mod, "GAME"):
            mod.GAME = GAME
        if hasattr(mod, "BACKUP"):
            mod.BACKUP = BACKUP


def _boot_paths():
    here = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        here = os.path.dirname(sys.executable)
    env = os.environ.get("F22ADF_GAME")
    if env and os.path.isfile(os.path.join(env, "adf.exe")):
        bind_game(env)
        return
    for cand in (here, os.path.dirname(here)):
        if os.path.isfile(os.path.join(cand, "adf.exe")):
            bind_game(cand)
            return
    fallback = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    )
    bind_game(fallback)


_boot_paths()

# Longest-first replacements for quoted UI strings (TEXT / TITLE / TOOLTIP TEXT / FEATURE / LEVEL)
UI = [
    ("Switch cockit reflections On/Off", "开/关座舱反射"),
    ("Switch Blackout/Redout effects On/Off", "开/关黑视/红视过载视效"),
    ("Switch Light Sourced Shading On/Off", "开/关光源着色"),
    ("Switch Anti-Aliasing On/Off", "开/关抗锯齿"),
    ("Switch building texture On/Off", "开/关建筑物纹理"),
    ("Switch aircraft shadows On/Off", "开/关飞机阴影"),
    ("Switch Enhanced Night Vision On/Off", "开/关增强夜视"),
    ("Switch Water Effects On/Off", "开/关水面特效"),
    ("Switch Lens Flare On/Off", "开/关镜头光晕"),
    ("Switch Wipes And Fades On/Off", "开/关转场与淡入淡出"),
    ("LIGHT SOURCED SHADING", "光源着色"),
    ("COCKPIT REFLECTIONS", "座舱反射"),
    ("AIRCRAFT SHADOWS", "飞机阴影"),
    ("BUILDING TEXTURE", "建筑物纹理"),
    ("ANTI-ALIASING", "抗锯齿"),
    ("ENHANCED NV", "增强夜视"),
    ("WATER EFFECTS", "水面特效"),
    ("LENS FLARE", "镜头光晕"),
    ("WIPES AND FADES", "转场与淡入淡出"),
    ("G EFFECTS", "过载视效"),
    ("Display SAM, EWR, Radar and Comms Installations", "显示地空导弹、预警雷达、雷达与通信设施"),
    ("Display Ground Vehicles And Military Bases", "显示地面车辆与军事基地"),
    ("Switch NATO Target Identification Symbology", "切换北约目标识别符号（NTIDS）"),
    ("Switch DiD Target Interaction Symbology", "切换交互目标符号（DTINS）"),
    ("Display Allied Waypoint Routes", "显示己方航线"),
    ("Display Forward Edge of Battle", "显示战斗前沿（FEBA）"),
    ("Switch Stylized Symbology", "切换示意符号"),
    ("Switch Flight Info Boxes", "切换编队信息框"),
    ("Display Ships And Ports", "显示舰船与港口"),
    ("Return To The Previous Screen", "返回上一屏幕"),
    ("Return To Previous Screen", "返回上一屏幕"),
    ("Return To the Main Screen", "返回主菜单"),
    ("Return To The Main Screen", "返回主菜单"),
    ("Return To Mission Selection", "返回任务选择"),
    ("Return To Small ACMI Window", "返回小窗口 ACMI"),
    ("Confirm New Selection And Return", "确认新设置并返回"),
    ("Discard New Selection And Return", "放弃新设置并返回"),
    ("Confirm Selection & Enter the Game", "确认选择并进入对局"),
    ("Confirm Selection & Enter Game", "确认选择并进入对局"),
    ("Confirm Completion & Continue", "确认完成并继续"),
    ("Confirm completion & continue", "确认完成并继续"),
    ("Confirm Warning & Continue", "确认警告并继续"),
    ("Create a New Multiplayer Game", "创建新的多人对局"),
    ("Join the Current Multiplayer Game", "加入当前多人对局"),
    ("Cancel the Multiplayer Game", "取消多人对局"),
    ("Reject Player From Your Game", "拒绝该玩家加入"),
    ("Play The Selected Mission", "执行所选任务"),
    ("Display The Full Screen ACMI", "全屏显示 ACMI"),
    ("Display The Last Plane", "显示上一架飞机"),
    ("Display The Next Plane", "显示下一架飞机"),
    ("Display Previous Plane", "显示上一架飞机"),
    ("Display Next Plane", "显示下一架飞机"),
    ("Display All Object Types", "显示全部目标类型"),
    ("Display The Weapon Types", "显示武器类型"),
    ("Display Each Planes Targets", "显示各机攻击目标"),
    ("Display Plane Heights", "显示飞机高度"),
    ("Load A New ACMI Recording", "载入新的 ACMI 记录"),
    ("Save The Current ACMI Recording", "保存当前 ACMI 记录"),
    ("Rewind Recording To The Start", "倒回记录起点"),
    ("Stop Recording/Playback", "停止录制/回放"),
    ("Fast Forward Playback", "快进回放"),
    ("Standard Playback", "正常回放"),
    ("Track Plane From The Side", "侧向跟踪飞机"),
    ("Player Defined Free View", "玩家自由视角"),
    ("Spin The View Around The Plane", "绕机旋转视角"),
    ("Spin The View Around Plane", "绕机旋转视角"),
    ("ACMI Cockpit View", "ACMI 座舱视角"),
    ("Satellite View", "卫星视角"),
    ("Display Personal Number Of Kills", "显示个人击毁数"),
    ("Display Personal Statistics", "显示个人统计"),
    ("Display Team Statistics ", "显示小队统计"),
    ("Display Personal Log", "显示个人日志"),
    ("Display personal log", "显示个人日志"),
    ("Display Hi-Score Table", "显示高分榜"),
    ("Display High Scores", "显示高分"),
    ("Cancel High-Score Display", "取消高分显示"),
    ("Display Attack Pattern", "显示攻击航线"),
    ("Display Mission Rating", "显示任务评级"),
    ("Display Mission Log", "显示任务日志"),
    ("Display Target", "显示目标"),
    ("Display Briefing", "显示任务简报"),
    ("Display briefing", "显示任务简报"),
    ("Display Map", "显示地图"),
    ("Display map", "显示地图"),
    ("Re-draw Map Display", "重绘地图"),
    ("Re-Draw Map", "重绘地图"),
    ("Re-draw map", "重绘地图"),
    ("Launch ACMI", "启动 ACMI"),
    ("Display stats", "显示统计"),
    ("Display events", "显示事件"),
    ("Display goals", "显示目标"),
    ("Air-To-Air Combat Training", "空战训练"),
    ("AWACS Mission Training", "预警机任务训练"),
    ("Basic Flight Training", "基础飞行训练"),
    ("Wingmen Training", "僚机协同训练"),
    ("Weapons Training", "武器训练"),
    ("Tour The F22ADF World", "红海战区航线游览"),
    ("Move Mission Time Forward", "任务时刻后移"),
    ("Move Mission Time Back", "任务时刻前移"),
    ("Mission Start Time", "任务起飞时刻"),
    ("Set Difficulty Level To Medium", "难度设为中等"),
    ("Set Difficulty Level To Hard", "难度设为困难"),
    ("Set Difficulty Level To Easy", "难度设为简单"),
    ("Alter Sound Effects Volume", "调节音效音量"),
    ("Alter Speech Volume", "调节语音音量"),
    ("Alter Music Volume", "调节音乐音量"),
    ("Select USAF Pac West Camouflage", "选择美国空军太平洋西部迷彩"),
    ("Select YF22 Camouflage", "选择 YF-22 迷彩"),
    ("Zoom To MFD On/Off", "开/关快速调出多功能显示器"),
    ("Calibrate Joystick", "校准操纵杆"),
    ("Select One On One ", "选择单挑（无阵营）"),
    ("Selcet Blue Team", "选择蓝方"),
    ("Select Blue Team", "选择蓝方"),
    ("Select Green Team", "选择绿方"),
    ("Select Yellow Team", "选择黄方"),
    ("Select Red Team", "选择红方"),
    ("End AWACS Mission", "结束预警机任务"),
    ("Return to AWACS", "返回预警机界面"),
    ("Abort current AWACS mission?", "中止当前预警机任务？"),
    ("Switch Speed Up Time", "切换时间加速"),
    ("Switch 3D Display", "切换三维显示"),
    ("Switch Map Scale", "切换地图比例"),
    ("Display Airbases", "显示空军基地"),
    ("Display Nations", "显示国家"),
    ("Suspend Game", "暂停游戏"),
    ("Center Map", "地图居中"),
    ("Map Detail", "地图细节"),
    ("Track Plane ", "跟踪飞机"),
    ("Confirm & Exit", "确认并退出"),
    ("Save High Score", "保存高分"),
    ("Enter Name", "输入姓名"),
    ("Full Screen ACMI", "全屏 ACMI"),
    ("ACMI Viewer", "ACMI 回放"),
    ("Quick Combat De-Briefing", "快速作战讲评"),
    ("MultiPlay Debrief", "多人讲评"),
    ("MultiPlay Client", "多人客户端"),
    ("Mission Information", "任务情报"),
    ("Training Missions", "训练任务"),
    ("Training Program", "训练大纲"),
    ("Combat Manouvres", "战斗机动"),
    ("Combat Tactics", "战斗战术"),
    ("Free Flight", "自由飞行"),
    ("Tour of Duty", "战区巡航"),
    ("Mission Selection", "任务选择"),
    ("Tour Selection", "巡航选择"),
    ("Quick Combat", "快速作战"),
    ("Weapon Selection", "武器选择"),
    ("Team Selection", "阵营选择"),
    ("Current Players", "当前玩家"),
    ("Games in Progress", "进行中的对局"),
    ("Game Details", "对局详情"),
    ("Chat Area", "聊天区"),
    ("Personal Log", "个人日志"),
    ("Players Log", "飞行员日志"),
    ("Mission Scores", "任务评分"),
    ("Attack Pattern", "攻击航线"),
    ("Re-Draw Map", "重绘地图"),
    ("Kill Table", "战果表"),
    ("Global Options", "全局选项"),
    ("Sound Options", "声音选项"),
    ("Effects/Game Detail", "特效/画面细节"),
    ("Ground Detail", "地面细节"),
    ("Aircraft Shadows", "飞机阴影"),
    ("F-22 Camouflage", "F-22 迷彩"),
    ("Quick Draw M.F.Ds", "快速调出多功能显示器"),
    ("Map Controls...", "控制器校准..."),
    ("Display Controls", "显示控制"),
    ("Recording Data", "记录数据"),
    ("Takeoff Base:", "起飞基地："),
    ("Mission Type:", "任务类型："),
    ("Flight Role:", "编队任务："),
    ("Game Type:", "游戏类型："),
    ("Next Plane", "下一架"),
    ("Last Plane", "上一架"),
    ("Object ID", "目标识别"),
    ("Weapon ID", "武器识别"),
    ("New Game", "新建对局"),
    ("Join Game", "加入对局"),
    ("Reject Player", "拒绝玩家"),
    ("No Team", "无阵营"),
    ("Side Trk", "侧视跟踪"),
    ("Hi Score", "高分"),
    ("High Score", "高分"),
    ("End Mission", "结束任务"),
    ("AWACS Control", "预警机指挥"),
    ("AWACS Map", "预警机态势图"),
    ("Flight Map", "飞行地图"),
    ("Air Defense", "防空"),
    ("Time Warp", "时间加速"),
    ("InfoBox", "信息框"),
    ("Airforce", "空军"),
    ("Stylized", "示意符号"),
    ("Descriptions", "说明"),
    ("Description", "说明"),
    ("3D View", "三维视图"),
    ("Scenarios", "想定"),
    ("Satellite", "卫星"),
    ("Cockpit", "座舱"),
    ("Heading", "航向"),
    ("Weapon", "武器"),
    ("Mission", "任务"),
    ("Personal", "个人"),
    ("Briefing", "简报"),
    ("Details", "详情"),
    ("Events", "事件"),
    ("Goals", "目标"),
    ("Stats", "统计"),
    ("Target:", "目标："),
    ("Target", "目标"),
    ("Targets", "目标"),
    ("Height", "高度"),
    ("Medium", "中等"),
    ("Speech", "语音"),
    ("Music", "音乐"),
    ("Sound FX ", "音效"),
    ("Nation", "国家"),
    ("Center", "居中"),
    ("Routes", "航线"),
    ("Scale", "比例"),
    ("Pause", "暂停"),
    ("Army", "陆军"),
    ("Navy", "海军"),
    ("Track", "跟踪"),
    ("Spin", "环绕"),
    ("Free", "自由"),
    ("Small", "小窗"),
    ("Prev", "上一个"),
    ("Next", "下一个"),
    ("Load", "载入"),
    ("Save", "保存"),
    ("Full", "全屏"),
    ("Exit", "退出"),
    ("Easy", "简单"),
    ("Hard", "困难"),
    ("High", "高"),
    ("Low", "低"),
    ("Med", "中"),
    ("Off", "关"),
    ("Map", "地图"),
    ("Team", "小队"),
    ("Blue", "蓝方"),
    ("Green", "绿方"),
    ("Yellow", "黄方"),
    ("Red ", "红方"),
    ("Mode", "模态"),
    ("Plane", "飞机"),
    ("Fuel", "燃油"),
    ("Score", "分数"),
    ("Warning", "警告"),
    ("Error!", "错误！"),
    ("Debrief", "讲评"),
    ("Credits", "制作人员"),
    ("Options", "选项"),
    ("Simulator", "模拟训练"),
    ("MultiPlay", "多人游戏"),
    ("Arcade", "快速作战"),
    ("NewGame", "新建对局"),
    ("Weapons", "武器"),
    ("Flight", "飞行"),
    ("AWACS", "预警机"),
    ("Record", "录制"),
    ("Jog", "逐帧"),
    ("Spd", "速度"),
    ("Pos", "位置"),
    ("Alt", "高度"),
]

# icondesc uses bitmap font; keep English. Catalog / HINTTEXT below.

CATALOG = {
    # simultor.txt
    "Free Flight": "自由飞行",
    "GTT Air Combat Scenario": "空战设计（ACD）",
    "Flight Training": "飞行训练",
    "Weapons Training": "武器训练",
    "Air-to-Air Tactics": "空战战术",
    "Wingmen": "僚机",
    "AWACS Missions": "预警机任务",
    "Ar Rub al Khali": "鲁卜哈利沙漠",
    "Harrat al Kishb": "基什布熔岩原",
    "Nile": "尼罗河",
    "Khartoum To Lake Tana": "喀土穆至塔纳湖",
    "Ethiopia": "埃塞俄比亚",
    "Red Sea Gate": "红海门户",
    "Take-Off": "起飞",
    "Landing": "着陆",
    "Refueling": "空中加油",
    "Engine Failure": "发动机故障",
    "Hydraulic Failure": "液压故障",
    "Electrical Failure": "电气故障",
    "BVR AMRAAM": "视距外 AMRAAM",
    "Dogfight Sidewinder": "近距格斗响尾蛇",
    "Maverick Mobile Attack": "小牛导弹机动目标攻击",
    "Cannon Strafe CAS": "航炮扫射近距支援",
    "Harpoon Ship Kill": "捕鲸叉反舰",
    "Rocket Attack": "火箭弹攻击",
    "Bomb BAI": "航空炸弹战场遮断",
    "Bomb LGB": "激光制导炸弹",
    "Cluster CAS": "集束弹药近距支援",
    "HARM SEAD": "反辐射导弹压制防空",
    "JDAM Interdiction": "联合直接攻击弹药遮断",
    "Cluster Airfield": "集束弹药封锁机场",
    "Using EMCON": "电磁控制运用",
    "Using The IRST": "红外搜索跟踪运用",
    "Eyeball And Shooter": "目视识别与射击手",
    "Drag Left": "左拖诱饵",
    "Offensive Split": "进攻分离",
    "Sandwich Left": "左侧夹击",
    "Defensive Split": "防御分离",
    "The Grinder": "绞磨战术",
    "Stealth Attack": "隐身突袭",
    "Pickle": "投放",
    "Engage My Target": "攻击我的目标",
    "Engage Bandits": "攻击敌机",
    "Engage Hostiles": "攻击敌对目标",
    "CAP Intercept": "战斗巡逻拦截",
    "Vis-Ident": "目视识别",
    "Refuel Strike": "打击编队加油",
    "Covert Mission": "隐蔽行动",
    # td_tours / td_miss
    "Tour of Duty": "战区巡航",
    "Red Sea Tour": "红海巡航",
    "Eritrea Tour": "厄立特里亚巡航",
    "Saudi Arabia Tour": "沙特阿拉伯巡航",
    "Ethiopia/Yemen Tour": "埃塞俄比亚/也门巡航",
    "Egyptian Tour": "埃及巡航",
    "Red Sea Ops Egyptian Tour": "红海作战埃及巡航",
    "AWACS Tour": "预警机巡航",
    "Saudi Tour": "沙特巡航",
    "Prelude": "序幕",
    "Close Hostile": "近距敌情",
    "Bill's Limo": "总统车队",
    "Arabian Sword": "阿拉伯之剑",
    "Strike Sudan": "打击苏丹",
    "SAMs": "地空导弹",
    "Fighters": "歼击机",
    "Air Egypt": "埃及空中力量",
    "Threat Kill": "清除威胁",
    "Raid Egypt": "突袭埃及",
    "Deny Flight": "禁飞",
    "Essential Supplies": "必需补给",
    "CAP UK": "英军战斗巡逻",
    "Armed Recce": "武装侦察",
    "Power Down": "切断电力",
    "Force Green": "开辟通道",
    "Tower 3": "三号塔台",
    "15 Down!": "两架 F-15 坠海！",
    "Para Watch": "伞降掩护",
    "Air Cover": "空中掩护",
    "Border Patrol": "边境巡逻",
    "Air Rebels": "空中叛军",
    "Sea CAP": "海上战斗巡逻",
    "Air Force": "空军突击",
    "Scramble!": "紧急起飞！",
    "Rebel Jizan": "吉赞叛军",
    "City 1 Yemen": "也门首都",
    "Roulette": "轮盘",
    "Final Missile": "最后的导弹",
    "Deployment": "兵力投送",
    "Recon Flight": "侦察护航",
    "Air Superiority": "制空",
    "Operation Titanic": "泰坦尼克行动",
    "LGB Attack": "激光制导炸弹攻击",
    "Counter AWACS": "反预警机",
    "AWACS Kill": "击毁预警机",
    "CAS Support": "近距空中支援",
    "Deep Strike": "纵深打击",
    "Final Kill": "最后一击",
    "Relocation": "转场",
    "Dam Defence": "大坝防空",
    "Operation Blackout": "灯火管制行动",
    "Divide & Conquer": "分割歼灭",
    "Logistics Strike AWACS": "后勤打击（预警机）",
    "Downtown AWACS": "城区作战（预警机）",
    "Armour Busting": "反装甲",
    "Airfield Strike": "机场打击",
    "Scud U Like": "飞毛腿警戒",
    "Deep Throat": "纵深斩首护航",
    "Decapitation": "斩首",
    "Intrusion": "入侵演练",
    "Resupply": "再补给",
    "Counter Air": "制空反击",
    "Paralyzing": "瘫痪",
    "Deliver the Message": "传达信息",
    "Counter-Recce": "反侦察",
    "First Moves": "先手",
    "Embassy Evacuation": "使馆撤离",
    "Special Forces Rescue": "特种部队救援",
    "Fighter Sweep": "歼击机清场",
    "Downtown SEAD": "城区压制防空",
    "Beachhead Preparation": "登陆场准备",
    "Beachhead Isolation": "登陆场隔绝",
    "Fleet Defence": "舰队防空",
    "Good Bye!": "告别！",
    # misssel
    "Planner": "任务规划",
    "Interdiction: Airfields": "遮断：机场",
    "Interdiction: Choke Points": "遮断：咽喉要点",
    "Interdiction: EWR SAMs (SEAD)": "遮断：预警雷达与地空导弹（SEAD）",
    "Interdiction: Oil Sites": "遮断：石油设施",
    "Interdiction: Oil Rigs": "遮断：海上油井",
    "Interdiction: Political Industrial": "遮断：政治工业目标",
    "Interdiction: Dams": "遮断：水坝",
    "Interdiction: Cities": "遮断：城市",
    "Interdiction: Ports": "遮断：港口",
    "Interdiction: Antiquities": "遮断：古迹",
    "Interdiction: Military": "遮断：军事设施",
    "BAI": "战场遮断（BAI）",
    "Base Capture": "夺占基地",
    "Ground Mobile Strike: Tanks": "对地机动打击：坦克",
    "Ground Mobile Strike: SAMs": "对地机动打击：地空导弹",
    "Ground Mobile Strike: Trains": "对地机动打击：列车",
    "Ground Mobile Strike: Boats": "对地机动打击：艇只",
    "Ground Mobile Strike: Ships": "对地机动打击：舰船",
    "Ground Mobile Strike: Military": "对地机动打击：军事目标",
    "Ground Mobile Strike: Other": "对地机动打击：其他",
    "CAS": "近距空中支援（CAS）",
    "HVA Attack": "高价值目标攻击",
    "CAP": "战斗空中巡逻（CAP）",
    "AWACS Patrol": "预警机巡逻",
    "JSTARS Patrol": "联合星巡逻",
    "ABCCC": "空中战场指挥控制（ABCCC）",
    "Refueler Patrol": "加油机巡逻",
    "Aurora Recce": "极光侦察",
    "Drone Recce": "无人机侦察",
    "EC130 Recce": "EC-130 侦察",
    "Rescue cap": "救援战斗巡逻",
    "Decap": "斩首",
    "Civillian": "民用目标",
    "Supply": "补给",
    # multipla
    "Custom": "自定义",
    "Canyon Chaos": "峡谷混战",
    "Seaside Slaughter": "滨海厮杀",
    "Mountain Madness": "山地狂飙",
    "Forest Fight": "密林交战",
    "River Battle": "河谷之战",
    "Battle For The Isle": "岛屿争夺",
    "Battle For Lahij": "拉希杰争夺",
    "Mountain Battle": "山地会战",
    "Base Attack": "基地突击",
}

HINT = [
    ("CYCLE RADIO FRQ", "循环无线电频率"),
    ("DATA TEXT ON/OFF", "开/关数据文字"),
    ("SYSTEMS REPORT", "系统报告"),
    ("AUTO EMCON", "自动电磁控制"),
    ("HUD MODE", "平显模态"),
    ("RADIO FRQ 1", "无线电频率 1"),
    ("RADIO FRQ 2", "无线电频率 2"),
    ("RADIO FRQ 3", "无线电频率 3"),
    ("RADIO FRQ 4", "无线电频率 4"),
    ("LANTIRN DISPLAY", "LANTIRN 显示"),
    ("ZOOM IMAGE", "缩放图像"),
    ("WEAPON IMAGE", "武器图像"),
    ("IRST IMAGE", "红外搜索跟踪图像"),
    ("LOCK IMAGE TO SELECTED WEAPON", "图像锁定至所选武器"),
    ("MANUAL ACMI ON/OFF", "开/关手动 ACMI"),
    ("TOGGLE GEAR", "收放起落架"),
    ("BAY DOORS", "武器舱门"),
    ("ARTIFICIAL HORIZON", "人工地平"),
    ("PITCH LADDER ON/OFF", "开/关俯仰梯"),
    ("DISPLAY AUTOPILOT", "显示自动驾驶"),
    ("LAUNCH CHAFF", "投放箔条"),
    ("LAUNCH FLARE STRING", "投放红外诱饵串"),
    ("CYCLE EMCON BACKWARDS", "反向循环电磁控制"),
    ("CYCLE EMCON FORWARDS", "正向循环电磁控制"),
    ("DEFENCE DISPLAY", "防御显示"),
    ("ENEMY RADAR RANGE", "敌雷达作用距离"),
    ("INCREASE SENSOR RANGE", "增大传感器作用距离"),
    ("DECREASE SENSOR RANGE", "减小传感器作用距离"),
    ("WAYPOINT EDITOR", "航路点编辑"),
    ("FILTER OWN SENSORS ONLY", "仅显示本机传感器"),
    ("DISPLAY GROUND TARGETS", "显示地面目标"),
    ("DISPLAY AIR TARGETS", "显示空中目标"),
    ("SITUATION DISPLAY", "态势显示"),
    ("MAP ON / OFF", "开/关地图"),
    ("SHOW PLACE NAMES", "显示地名"),
    ("WAYPOINT DISPLAY ON/OFF", "开/关航路点显示"),
    ("DISPLAY LANTIRN IMAGE", "显示 LANTIRN 图像"),
    ("LANTIRN RESET", "LANTIRN 复位"),
    ("TOGGLE ZOOM", "切换缩放"),
    ("LANTIRN TRACK", "LANTIRN 跟踪"),
    ("CHANGE LANTIRN MODE", "切换 LANTIRN 模态"),
    ("AUTO CYCLE TARGETS", "自动循环目标"),
    ("MANUAL CYCLE TARGETS", "手动循环目标"),
    ("ATTACK DISPLAY", "攻击显示"),
    ("DISPLAY WEAPONS IMAGE", "显示武器图像"),
    ("DISPLAY ALTITUDE DATA", "显示高度数据"),
    ("GENERATE SHOOT LIST", "生成射击清单"),
    ("DISPLAY RANGE DATA", "显示距离数据"),
    ("CYCLE FIRE MODE", "循环射击模态"),
    ("DECREASE FIRE NUMBER", "减少发射数量"),
    ("INCREASE FIRE NUMBER", "增加发射数量"),
    ("DECREASE FIRE DELAY", "缩短发射间隔"),
    ("INCREASE FIRE DELAY", "延长发射间隔"),
    ("MAIN SYSTEMS DISPLAY", "主系统显示"),
    ("FUEL SYSTEMS DISPLAY", "燃油系统显示"),
    ("CYCLE WINGMAN SYSTEMS DISPLAY", "循环僚机系统显示"),
    ("DISPLAY SYSTEMS CHECK", "显示系统检查"),
    ("VOCAL WARNINGS ON/OFF", "开/关语音告警"),
    ("DISPLAY ILS MARKERS", "显示仪表着陆系统标记"),
]

WPTASK = [
    ("Paddy's Perfect CAP route", "标准战斗空中巡逻航线"),
    ("Escort CAP over Strike Target", "打击目标上空护航巡逻"),
    ("Search 50Km X 50Km box with 4 aircraft", "四机搜索 50 千米见方空域"),
    ("Search 15Km X 15Km box with 4 a/c in formation", "四机编队搜索 15 千米见方空域"),
    ("Helicopter Search 5Km X 5Km box ", "直升机搜索 5 千米见方空域"),
    ("One pass Search of 10Km X 30Km box with 4 aircraft", "四机单次通过搜索 10×30 千米空域"),
    ("FreeFall Weapon Attack Pattern 1000ft	above target", "自由落体弹药攻击航线，目标上空 1000 英尺"),
    ("JDAM/LGB Attack Pattern 15000ft above target", "联合直接攻击弹药/激光制导炸弹攻击航线，目标上空 15000 英尺"),
    ("Cluster Bomb Attack Pattern 2500ft above target", "集束炸弹攻击航线，目标上空 2500 英尺"),
    ("Toss bomb attack Pattern for JDAMS/GBU'S", "联合直接攻击弹药/制导炸弹上抛投弹航线"),
    ("JDAM/LGB Attack Pattern 25000ft above target", "联合直接攻击弹药/激光制导炸弹攻击航线，目标上空 25000 英尺"),
    ("Maverick/kh29/kh59m attack pattern", "小牛/Kh-29/Kh-59M 攻击航线"),
    ("HARM/KH58/ALARM attack pattern", "反辐射导弹/Kh-58/ALARM 攻击航线"),
    ("Harpoon/kh31/seaeagle attack pattern", "捕鲸叉/Kh-31/海鹰攻击航线"),
    ("Straight Run Air Drop at 250ft", "250 英尺直线空投"),
    ("Helicopters busying themselves over the battlefield", "直升机战场活动航线"),
    ("Large circuit for refuellers on patrol", "加油机巡逻大航线"),
    ("Large circuit for Awacs on Patrol", "预警机巡逻大航线"),
    ("Large circuit for Jstars on Patrol", "联合星巡逻大航线"),
    ("Holding pattern", "等待航线"),
]

CREDIT_ROLES = [
    ("Executive Producer", "执行制作人"),
    ("Technical Director", "技术总监"),
    ("Additional Art", "附加美术"),
    ("Special Thanks to", "特别感谢"),
    ("Managing Director", "常务董事"),
    ("Projects Director", "项目总监"),
    ("Creative Director", "创意总监"),
    ("Development Director", "开发总监"),
    ("Director of R&D", "研发总监"),
    ("Software Developments Director", "软件开发总监"),
    ("Associate Producers", "联合制作人"),
    ("Game Programming", "游戏程序"),
    ("Lead Programmer", "主程序"),
    ("Senior Programmer", "资深程序"),
    ("AI Programming", "人工智能程序"),
    ("Head of AI", "人工智能主管"),
    ("Senior AI Programmer", "资深人工智能程序"),
    ("Manual Art", "手册美术"),
    ("Graphic Designer", "平面设计师"),
    ("Interface Art", "界面美术"),
    ("Interface Art Director", "界面美术总监"),
    ("Senior Artist", "资深美术"),
    ("Interface Artist", "界面美术"),
    ("Game Art", "游戏美术"),
    ("Head of Art & Design", "美术与设计主管"),
    ("Head of R&D", "研发主管"),
    ("Head of Audio", "音频主管"),
    ("Quality Assurance", "质量保证"),
    ("Quality Control Manager", "质量控制经理"),
    ("Military Projects", "军方项目"),
    ("Press and Media Relations", "新闻与媒体关系"),
    ("Administration", "行政"),
    ("Network Supervisor", "网络主管"),
    ("Network Support", "网络支持"),
    ("With thanks to...", "同时感谢……"),
    ("A very special thanks to the partners and children of team members", "特别感谢制作组成员的伴侣与子女"),
    ("without your patience, and support this project would never have been possible", "没有你们的耐心与支持，本项目不可能完成"),
    ("Special thanks to everyone around the world who bought or commented on DID products.", "特别感谢世界各地购买或评论过 DID 作品的每一位"),
    ("Your criticism, enthusiasm and suggestions have been noted", "你们的批评、热情与建议我们都已记下"),
    ("Testing", "测试"),
    ("Directors", "总监"),
    ("Producer", "制作人"),
    ("Audio", "音频"),
    ("Network", "网络"),
]


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def decode_src(raw):
    if raw.startswith(b"\xff\xfe"):
        return raw.decode("utf-16-le")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8")
    # Never try latin-1 first: it always succeeds and a later GBK encode turns 汉字 into '?'.
    for enc in ("utf-8", "gbk", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "replace")


def write_gbk(path, text):
    # GDD gadget TEXT: engine draws via GDI + system ANSI (GBK on Chinese Windows).
    data = text.encode("gbk", errors="replace")
    with open(path, "wb") as f:
        f.write(data)


def write_utf8(path, text):
    # Briefing / catalog overlay text: remaster walks 8-bit or UTF-8, not GBK.
    if "\r\n" not in text:
        text = text.replace("\n", "\r\n")
    data = text.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)


def backup_file(rel):
    src = os.path.join(GAME, rel)
    dst = os.path.join(BACKUP, rel)
    if not os.path.isfile(src):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.isfile(dst):
        shutil.copy2(src, dst)


def quoted_replace(text, pairs):
    # Replace only inside double quotes, longest first already
    for en, zh in pairs:
        text = text.replace('"' + en + '"', '"' + zh + '"')
    return text


# WINDOW-level TEXT / TITLE are remaster lookup keys (Confirm → Brief/Simulator).
# Only the header before the first GADGET; gadget labels stay Chinese.
WINDOW_LOOKUP = [
    ("模拟训练", "Simulator"),
    ("制作人员", "Credits"),
    ("多人游戏", "MultiPlay"),
    ("选项", "Options"),
    ("快速作战讲评", "Quick Combat De-Briefing"),
    ("多人讲评", "MultiPlay Debrief"),
    ("新建对局", "NewGame"),
    ("高分", "High Score"),
    ("讲评", "Debrief"),
    ("简报", "Brief"),
    ("战区巡航", "Tour of Duty"),
    ("快速作战", "Quick Combat"),
]


def restore_lookup_fields(text):
    m = re.search(r"(?i)\n[ \t]*GADGET\s", text)
    if not m:
        head, tail = text, ""
    else:
        head, tail = text[: m.start() + 1], text[m.start() + 1 :]
    for zh, en in WINDOW_LOOKUP:
        head = head.replace('TEXT "' + zh + '"', 'TEXT "' + en + '"')
        head = head.replace('TITLE "' + zh + '"', 'TITLE "' + en + '"')
        head = head.replace('HELP_PAGE "' + zh + '"', 'HELP_PAGE "' + en + '"')
    return head + tail


# Gadget OK/Cancel/Accept are remaster action keys (Confirm / start mission).
# Draw Chinese at GDI time via DINPUT8 lookup_ui.
ACTION_LOOKUP = [
    ("确定", "OK"),
    ("取消", "Cancel"),
    ("接受", "Accept"),
    ("自由飞行", "Free Flight"),
    ("飞行训练", "Flight"),
    ("武器训练", "Weapons"),
    ("战斗战术", "Combat Tactics"),
    ("战斗机动", "Combat Manouvres"),
    ("预警机", "AWACS"),
    ("训练任务", "Training Missions"),
    ("训练大纲", "Training Program"),
]


def restore_action_text(text):
    for zh, en in ACTION_LOOKUP:
        text = text.replace('TEXT "' + zh + '"', 'TEXT "' + en + '"')
    return text


def apply_file(rel, transform, writer=None):
    path = os.path.join(GAME, rel)
    if not os.path.isfile(path):
        print("missing", rel)
        return
    backup_file(rel)
    raw = read_bytes(path)
    text = decode_src(raw)
    new = transform(text)
    out = writer or write_gbk
    if new != text or writer is write_utf8:
        out(path, new)
        print("updated", rel)
    else:
        print("unchanged", rel)


def main():
    os.makedirs(BACKUP, exist_ok=True)

    # Font
    src_font = r"C:\Windows\Fonts\simhei.ttf"
    dst_font = os.path.join(GAME, "WINFONTS", "zh_ui.ttf")
    if os.path.isfile(src_font):
        if not os.path.isfile(os.path.join(BACKUP, "WINFONTS", "zh_ui.ttf")):
            os.makedirs(os.path.join(BACKUP, "WINFONTS"), exist_ok=True)
        shutil.copy2(src_font, dst_font)
        print("copied zh_ui.ttf")
    else:
        print("WARNING: simhei.ttf not found")

    def windesc(t):
        # Engine: CreateWinFont max 3 files. Keep HUD TTF as the third slot.
        t = t.replace('CREATE_SYS_FONT "winfonts\\f22_1.ext"', 'CREATE_SYS_FONT "winfonts\\zh_ui.ttf"')
        t = t.replace('CREATE_SYS_FONT "winfonts\\f22_2.ext"', 'CREATE_SYS_FONT "winfonts\\zh_ui.ttf"')
        t = t.replace('STYLE "Univers"', 'STYLE "SimHei"')
        t = t.replace('STYLE "MS Sans Serif"', 'STYLE "SimHei"')
        t = t.replace('STYLE "OPUnivers-FiftySeven"', 'STYLE "SimHei"')
        t = t.replace('STYLE "Arial Black"', 'STYLE "SimHei"')
        return t

    apply_file(os.path.join("f22data", "windesc.win"), windesc)

    gdd_dir = os.path.join("f22data")
    for fn in os.listdir(os.path.join(GAME, gdd_dir)):
        if fn.lower().endswith((".gdd", ".win")) and fn.lower() != "windesc.win":
            apply_file(
                os.path.join("f22data", fn),
                lambda t, p=UI: restore_action_text(restore_lookup_fields(quoted_replace(t, p))),
            )

    # options.cfg FEATURE names are engine lookup keys (e.g. COCKPIT REFLECTIONS). Do not translate.

    def catalog(t):
        return quoted_replace(t, sorted(CATALOG.items(), key=lambda kv: -len(kv[0])))

    for fn in ("simultor.txt", "td_miss.txt", "td_tours.txt", "misssel.txt", "multipla.txt", "arcade.txt"):
        apply_file(os.path.join("f22data", fn), catalog, writer=write_gbk)

    apply_file(os.path.join("huddle", "f22.ins"), lambda t: quoted_replace(t, HINT))
    apply_file(os.path.join("f22data", "wptasks.txt"), lambda t: quoted_replace(t, WPTASK), writer=write_gbk)

    def credits(t):
        for en, zh in sorted(CREDIT_ROLES, key=lambda kv: -len(kv[0])):
            t = t.replace(en, zh)
        return t

    apply_file(os.path.join("briefing", "credits1.txt"), credits, writer=write_utf8)

    bak_menu = os.path.join(BACKUP, "f22data", "adfmenu.txt")
    dst_menu = os.path.join(GAME, "f22data", "adfmenu.txt")
    if os.path.isfile(bak_menu):
        backup_file(os.path.join("f22data", "adfmenu.txt"))
        shutil.copy2(bak_menu, dst_menu)
        print("adfmenu.txt English TEXT (labels via DINPUT8)")
    print("UI apply done")


if __name__ == "__main__":
    main()
