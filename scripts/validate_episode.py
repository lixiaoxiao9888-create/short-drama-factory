#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v3.2 单集剧本机检（分档）

用法:
    python3 validate_episode.py <单集剧本.md> [--format auto|standard|long|manju] [--prev 前集.md ...]
    python3 validate_episode.py --self-test

档位 profile (--format; 默认 auto = 按正文自检: 含"长档"→long, 含"漫剧"→manju, 否则 standard):
    standard  标准档 90~120 秒   正文体量 实拍 350~500 / 漫剧 260~400   场景 <=2   对白行 >=4
    long      长档   165~195 秒  正文体量 实拍 650~850 / 漫剧 520~680   场景 <=3   对白行 >=8   必设【本集中段小钩】
    manju     漫剧档 60~90 秒    正文体量 260~400                       场景 <=2   对白行 >=4

检查项 (FAIL=拦截必须修复, WARN=告警复核):
    E1  剧本文本体量(对白+动作行+断章画面, 不含【】字段行/[场景][人物])  FAIL(超区间)
          标准档 实拍 350~500 / 漫剧 260~400 ；长档 实拍 650~850 / 漫剧 520~680
    E2  单句台词(常规 12~18 字 / 爆发金句 8~12) 硬上限 25 字   WARN(逐句 >25)
    E3  场景数 <=2 ([场景] 标记计数)                FAIL(>2)
    E4  黄金前3秒: 首个动作/台词行含冲突信号词       FAIL(无)
    E5  开篇禁词(起床/拉窗帘/太阳升起/走在路上等)     WARN
    E6  断章卡点: 存在【本集断章卡点】且含黑屏/悬念   FAIL(缺)
    E7  情绪流变词: 存在【情绪流变】链条(-> 或 ➔)    WARN(缺)
    E8  复读检测: 主角台词与前集传入(--prev)重复     WARN(重复句)
    E9  对白行数: >= 本档位下限(标准/漫剧 4 行, 长档 8 行)  WARN(不足)
    E10 合规红线词(断肢/开膛/下蛊等一票否决直观描写)  FAIL
    E11 长档中段小钩: 存在【本集中段小钩】(long 档)      FAIL(长档缺)
退出码: 0=通过(可含WARN), 1=FAIL, 2=用法错误
"""
import re
import sys

# 剧本文本体量阈值(仅计正文: 对白行 + △动作行 + 断章卡点画面描述)
NET_MIN, NET_MAX = 350, 500          # 实拍短剧
NET_MIN_ANIME, NET_MAX_ANIME = 260, 400  # 漫剧/竖屏动画
NET_LONG_MIN, NET_LONG_MAX = 650, 850          # 长档(约3分钟) 实拍
NET_LONG_ANIME_MIN, NET_LONG_ANIME_MAX = 520, 680  # 长档 漫剧/竖屏动画
SENT_MAX = 25                        # 单句台词硬上限(常规 12~18)

# 档位 profile（体量区间另按 profile + 是否漫剧解析，见 net_band()）
PROFILES = {
    "auto":     {"scenes": 2, "lines": 4, "midhook": False, "label": "自动分档"},
    "standard": {"scenes": 2, "lines": 4, "midhook": False, "label": "标准档 90~120 秒"},
    "long":     {"scenes": 3, "lines": 8, "midhook": True,  "label": "长档 约3分钟"},
    "manju":    {"scenes": 2, "lines": 4, "midhook": False, "label": "漫剧档 60~90 秒"},
}

OPEN_BAN_WORDS = ["早晨起床", "起床", "拉窗帘", "太阳升起", "醒过来", "走在路上",
                  "整理衣服", "开车上班", "喝咖啡闲聊", "悠闲的清晨", "阳光明媚的早晨"]

# 注: 不含 "△" —— 动作行本身不等于冲突, 否则任何以动作开场的剧本恒过 E4
CONFLICT_SIGNALS = ["！?", "！", "枪", "刀", "巴掌", "扔", "砸", "吼", "冷笑",
                    "逼", "跪", "撕", "拍在", "顶在", "推", "踹", "骂", "羞辱", "退婚",
                    "病危", "签字", "死", "滚", "住手", "救", "断裂", "炸", "烧", "血"]

BREAK_WORDS = ["断章", "卡点", "黑屏", "悬念"]

REDLINE_WORDS = ["断肢", "开膛", "破肚", "身首异处", "凌迟", "活埋", "注射死刑", "吸毒",
                 "制毒", "自杀方法", "下蛊害人", "蛊毒害人", "真实的国家机关"]


def _is_dialogue(line):
    """对白行: 角色名(可选括号提示): 台词  —— 不以[ △ 【开头"""
    s = line.strip()
    if not s or s.startswith(("[", "△", "【", "#", ">")):
        return None
    m = re.match(r"^([\u4e00-\u9fa5A-Za-z0-9]{1,8})(（[^）]*）|\([^)]*\))?\s*[:：]\s*(.+)$", s)
    return m.group(3) if m else None


def net_chars(text):
    """剧本文本体量: 仅计
        - 对白行台词
        - △ 动作指示行内容
        - 【本集断章卡点】画面描述
    剔除: 【所属阶段】【黄金前3秒钩子】【情绪流变】【本集时长】等字段行,
          以及 [场景]/[人物] 标记行(结构性元数据, 非剧本正文)
    """
    total = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        d = _is_dialogue(s)
        if d is not None:
            body = d
        elif s.startswith("△"):
            body = re.sub(r"^△\s*", "", s)
        elif s.startswith("【本集断章卡点】"):
            body = re.sub(r"^【本集断章卡点】\s*[:：]?\s*", "", s)
        else:
            continue  # 字段行【】/标记行[]/普通行 一律不计
        body = re.sub(r"[\s，。！？；：、…—\-·“”\"'‘’（）()《》!?.]", "", body)
        total += len(body)
    return total


def is_anime(text):
    """漫剧/竖屏动画项目: 文本含 '漫剧' 即按漫剧体量档判 E1"""
    return "漫剧" in text


def is_long(text):
    """长档项目: 文本含 '长档' 即按长档体量判 E1/E3/E9/E11"""
    return "长档" in text


def resolve_profile(text, profile="auto"):
    """auto 档按正文自检: 含"长档"→long, 含"漫剧"→manju, 否则 standard"""
    if profile != "auto":
        return profile if profile in PROFILES else "standard"
    if is_long(text):
        return "long"
    if is_anime(text):
        return "manju"
    return "standard"


def net_band(text, profile):
    """按档位 + 是否漫剧返回正文体量区间"""
    if profile == "long":
        return (NET_LONG_ANIME_MIN, NET_LONG_ANIME_MAX) if is_anime(text) else (NET_LONG_MIN, NET_LONG_MAX)
    if profile == "manju":
        return NET_MIN_ANIME, NET_MAX_ANIME
    return (NET_MIN_ANIME, NET_MAX_ANIME) if is_anime(text) else (NET_MIN, NET_MAX)


def scene_count(text):
    return len(re.findall(r"^\[场景\]|^【场景】|^##?\s*场景", text, re.M))


def first_content_lines(text, n=3):
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", ">", "第", "【所属", "【黄金", "【情绪", "【本集时长", "[场景", "[人物", "【场景", "【人物")):
            continue
        out.append(s)
        if len(out) >= n:
            break
    return out


def validate(text, prev_texts=(), profile="auto"):
    profile = resolve_profile(text, profile)
    prof = PROFILES[profile]
    fails, warns = [], []
    nc = net_chars(text)
    lo, hi = net_band(text, profile)
    if not (lo <= nc <= hi):
        kind = "漫剧" if is_anime(text) else "实拍"
        fails.append(f"E1 [{profile}] 剧本文本体量 {nc} 不在 {lo}~{hi} 区间（{kind}档）")

    for line in text.splitlines():
        d = _is_dialogue(line)
        if d:
            clean = re.sub(r"[\s，。！？；：、…—]", "", d)
            if len(clean) > SENT_MAX:
                warns.append(f"E2 单句台词 {len(clean)} 字(>{SENT_MAX}): {clean[:18]}…")

    sc = scene_count(text)
    if sc > prof["scenes"]:
        fails.append(f"E3 [{profile}] 场景数 {sc} >{prof['scenes']}")
    if sc == 0:
        warns.append("E3 未检出 [场景] 标记，无法核对场景数")

    head = "".join(first_content_lines(text))
    banned_hit = any(w in head for w in OPEN_BAN_WORDS)
    if banned_hit or not any(w in head for w in CONFLICT_SIGNALS):
        fails.append("E4 前3秒无冲突/命中开篇废镜头词(须直接切入冲突顶点，禁铺垫)")
    for w in OPEN_BAN_WORDS:
        if w in head:
            warns.append(f"E5 开篇疑似废镜头禁词「{w}」")

    if not re.search(r"【本集断章卡点】|\[本集断章", text):
        fails.append("E6 缺【本集断章卡点】段")
    else:
        seg = re.search(r"【本集断章卡点】(.{0,200})", text, re.S)
        if seg and not any(w in seg.group(1) for w in ["黑屏", "悬念", "下滑", "解锁"]):
            warns.append("E6 断章卡点缺黑屏/下滑解锁落点词")

    if not re.search(r"【情绪流变】.*(->|➔|➔|→)", text):
        warns.append("E7 缺【情绪流变】链条(应标: 遭受刁难 ➔ … ➔ 绝命断章)")

    rounds = 0
    my_lines = [d for d in (_is_dialogue(l) for l in text.splitlines()) if d]
    rounds = len(my_lines)
    if prof["midhook"] and not re.search(r"【本集中段小钩】|\[本集中段小钩", text):
        fails.append("E11 长档缺【本集中段小钩】(≈90 秒处必设新信息/新威胁，防滑走)")
    if rounds < prof["lines"]:
        warns.append(f"E9 [{profile}] 对白行仅 {rounds} 行(<{prof['lines']})，攻防结构不足")

    for prev in prev_texts:
        prev_set = set(re.sub(r"\s", "", p) for p in (_is_dialogue(l) for l in prev.splitlines()) if p)
        for d in my_lines:
            dd = re.sub(r"\s", "", d)
            if dd in prev_set and len(dd) >= 8:
                warns.append(f"E8 台词与前集复读: {dd[:16]}…")

    for w in REDLINE_WORDS:
        if w in text:
            fails.append(f"E10 合规一票否决类直观描写「{w}」")

    return fails, warns, nc


GOOD = """第【1】集：【龙王令·开局羞辱】
【黄金前3秒钩子】：极端羞辱
【情绪流变】：当众受辱 ➔ 隐忍握拳 ➔ 亮令反杀 ➔ 绝命断章
【本集时长】：105 秒
[场景]：内景·顶级私人会所·夜
[人物]：林辰（隐忍龙王）、陈峰（嚣张富二代）、苏清雪（未婚妻）

△ 特写：点燃的雪茄狠狠摁在林辰洗得发白的衣领上，青烟直冒，火星坠落。
△ 中景：陈峰搂着苏清雪，满脸鄙夷，包厢内保镖环立。
陈峰（吐出烟圈）：跪下，把这杯脏水喝了，十万块救命钱，本少当场转给你。
苏清雪（冷漠）：林辰，别不知好歹，认清你自己的身份。
△ 特写：林辰低垂的眼眸骤抬，垂在身侧的右拳缓缓握紧，指节泛白。
林辰（声音极低）：三年前你陈家跪着求我救命时，也是这副嘴脸？
陈峰（恼羞成怒）：你找死！给我废了他双手！
△ 四名保镖暴起扑上，林辰反手抓住领头手腕顺势一拧，骨裂声起，保镖倒飞砸碎整面酒柜。
△ 玻璃碎裂，酒水横流，全场死寂，陈峰踉跄后退撞翻茶几。
陈峰（色厉内荏）：你……你敢动手？你知道我爸是谁吗？
林辰：在江城，能让我跪的，只有已故的先人。
△ 林辰从怀中掏出一枚九龙玄铁令，重重拍在桌上，震得酒杯齐齐炸裂。
林辰（字字如刀）：传我龙王令，十分钟内，让江城陈氏集团彻底破产。
△ 特写：陈峰死死盯着令牌上的九龙图腾，双腿剧烈发抖，手机疯狂震动，来电显示"父亲"。

【本集断章卡点】：陈峰颤抖着接通电话，那头传来绝望哭嚎："逆子，你到底得罪了谁？陈家彻底完了！"林辰一步踏出，居高临下逼近。（黑屏：下滑立即解锁第2集）
"""

BAD = """第【1】集
清晨，林辰起床拉开窗帘，太阳升起。他在路上慢慢走。
陈峰：林辰，你要知道，三年前你害死了我父亲，侵占了我们家三千万的财产，今天我一定要让你血债血偿，把我的东西全部还回来！
林辰：好的。
△ 他把断肢捡起来。
"""


def self_test():
    ok = 1
    f, w, nc = validate(GOOD)
    if f:
        print("FAIL self-test: GOOD 样例不应 FAIL:", f); ok = 0
    if nc < 100:
        print("FAIL self-test: GOOD 净字数异常", nc); ok = 0
    f, w, _ = validate(BAD)
    if not any("E1" in x for x in f):
        print("FAIL self-test: BAD 应报 E1 或字数异常"); ok = 0
    if not any("E4" in x for x in f):
        print("FAIL self-test: BAD 应报 E4 前3秒无冲突"); ok = 0
    if not any("E6" in x for x in f):
        print("FAIL self-test: BAD 应报 E6 缺断章"); ok = 0
    if not any("E10" in x for x in f):
        print("FAIL self-test: BAD 应报 E10 红线词"); ok = 0
    if not any("E5" in x for x in w):
        print("FAIL self-test: BAD 应报 E5 开篇禁词"); ok = 0

    # 回归1: 字段行不应灌入 E1 体量
    hdr_only = "第【1】集\n【所属阶段】：第X幕・（第 1/80 集 ｜ 往返第 N 回合）\n【黄金前3秒钩子】：极端羞辱型（婚礼当众）\n【情绪流变】：受辱 ➔ 隐忍 ➔ 反杀 ➔ 绝命断章\n【本集时长】：108 秒\n[场景]：内景·会所·夜\n[人物]：林辰、陈峰\n"
    if net_chars(hdr_only) != 0:
        print("FAIL self-test: 纯字段/标记行应计 0 字，实得", net_chars(hdr_only)); ok = 0

    # 回归2: 以 △ 开场的废镜头剧本，E4 必须拦截
    boring = "第【1】集\n[场景]：内景·客厅·日\n[人物]：甲、乙\n△ 他慢慢走进客厅，端起茶杯喝了一口。\n△ 他看了看窗外。\n甲：今天天气不错。\n乙：是啊。\n甲：那先这样。\n乙：好。\n【本集断章卡点】：两人告别。（黑屏）\n"
    f, w, _ = validate(boring)
    if not any("E4" in x for x in f):
        print("FAIL self-test: △ 开场的废镜头剧本应报 E4"); ok = 0

    # 回归3: 漫剧档体量(260~400)应可用
    anime = "第【1】集：漫剧\n【情绪流变】：受辱 ➔ 隐忍 ➔ 反杀 ➔ 绝命断章\n[场景]：内景·堂·日\n[人物]：甲、乙\n" + "".join(f"△ 具体的物理动作行编号{i}，可被镜头拍到的行为事件推进本集冲突。\n" for i in range(9)) + "甲：你确定要这么做？\n乙：我确定。\n甲：那就别怪我。\n乙：来吧。\n【本集断章卡点】：灯灭人散，只余一击。（黑屏：下滑解锁）\n"
    f, w, _ = validate(anime)
    if any("E1" in x for x in f):
        print("FAIL self-test: 漫剧档不应报 E1 区冲突:", [x for x in f if 'E1' in x]); ok = 0

    # 回归4: 台词硬上限 25
    longline = "第【1】集\n[场景]：内景\n[人物]：甲\n△ 拍桌。\n甲：这是超过二十五个字的长复合句用来触发告警检查是否生效一二三四五六七八。\n【本集断章卡点】：黑屏（黑屏）\n"
    f, w, _ = validate(longline)
    if not any("E2" in x for x in w):
        print("FAIL self-test: >25 字台词应报 E2"); ok = 0

    # 回归5: 长档（约3分钟）—— 双回合 + 中段小钩 + 体量 650~850，auto 档自检
    long_body = ("".join(f"△ 特写：巴掌扇到半空被反手抓住，第{i}个受力事件推进冲突升级。\n" for i in range(18))
                 + "".join(f"林辰：第{i}句短台词，带新信息与代价。\n" for i in range(14)))
    long_good = ("第【1】集：长档样例（长档·约3分钟）\n【本集时长】：180 秒\n"
                 "[场景]：内景·会所·夜\n[场景]：内景·走廊·夜\n[人物]：林辰、陈峰\n"
                 + long_body
                 + "【本集中段小钩】：手机亮起病危通知单，缴费截止今晚，对面按下挂断键。\n"
                 + "△ 林辰反手拧腕，骨裂声起，铁棍滚落。\n"
                 + "【本集断章卡点】：电话那头传来绝望哭嚎，陈峰双腿发抖。（黑屏：下滑解锁第2集）\n")
    f, w, nc = validate(long_good)
    if f:
        print("FAIL self-test: 长档样例不应 FAIL:", f, "体量", nc); ok = 0
    if not (NET_LONG_MIN <= nc <= NET_LONG_MAX):
        print(f"FAIL self-test: 长档样例体量 {nc} 应在 {NET_LONG_MIN}~{NET_LONG_MAX}"); ok = 0
    # 长档缺中段小钩 → E11
    f, _, _ = validate(long_good.replace("【本集中段小钩】", "【中段】"))
    if not any("E11" in x for x in f):
        print("FAIL self-test: 长档缺中段小钩应报 E11"); ok = 0
    # 显式 --format long 检标准档样本 → E1 + E11
    f, w, _ = validate(GOOD, profile="long")
    if not any("E1" in x for x in f):
        print("FAIL self-test: 标准档样本按 long 显式机检应报 E1"); ok = 0
    if not any("E11" in x for x in f):
        print("FAIL self-test: 标准档样本按 long 显式机检应报 E11"); ok = 0
    # 长档场景上限 3：4 场应报 E3
    f, _, _ = validate(long_good + "[场景]：内景·车库·夜\n[场景]：内景·天台·夜\n")
    if not any("E3" in x for x in f):
        print("FAIL self-test: 长档 4 场景应报 E3"); ok = 0

    print("[+] self-test PASSED" if ok else "[-] self-test FAILED")
    return 0 if ok else 1


def parse_args(args):
    """返回 (path, profile, prev_paths)；用法错误抛 SystemExit(2)"""
    path, profile, prevs = None, "auto", []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--prev":
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                prevs.append(args[i]); i += 1
            continue
        if a == "--long":
            profile = "long"
        elif a == "--manju":
            profile = "manju"
        elif a == "--format" or a.startswith("--format="):
            val = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
            if "=" not in a:
                i += 1
            if val not in PROFILES:
                print(f"[-] --format 只接受 {'/'.join(PROFILES)}，收到「{val}」"); raise SystemExit(2)
            profile = val
        elif a.startswith("--"):
            print(f"[-] 未知参数「{a}」"); raise SystemExit(2)
        elif path is None:
            path = a
        i += 1
    return path, profile, prevs


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 2
    if args[0] == "--self-test":
        return self_test()
    try:
        path, profile, prevs = parse_args(args)
    except SystemExit as e:
        return e.code or 2
    if not path:
        print(__doc__); return 2
    # 友好处理缺文件/编码错误（避免裸 traceback）
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"[-] 找不到剧本文件: {path}"); return 2
    except UnicodeDecodeError:
        print(f"[-] 文件不是 UTF-8 文本，无法读取: {path}"); return 2
    for p in prevs:
        try:
            open(p, encoding="utf-8").read()
        except (FileNotFoundError, UnicodeDecodeError):
            print(f"[-] 找不到或无法读取前集文件: {p}"); return 2
    prev_texts = [open(p, encoding="utf-8").read() for p in prevs]
    profile = resolve_profile(text, profile)
    fails, warns, nc = validate(text, prev_texts, profile)
    print(f"== {path}  [{profile} {PROFILES[profile]['label']}]  正文体量≈{nc} ==")
    for x in fails:
        print("[-] FAIL:", x)
    for x in warns:
        print("[!] WARN:", x)
    if fails:
        print("结果: FAILED（修复后重跑）"); return 1
    print("结果: PASSED" + ("（含 WARN 请复核）" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
