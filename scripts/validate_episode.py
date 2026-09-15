#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v3.1 单集剧本机检

用法:
    python3 validate_episode.py <单集剧本.md>
    python3 validate_episode.py --self-test

检查项 (FAIL=拦截必须修复, WARN=告警复核):
    E1  剧本净字数(对白+动作行) 350~500            FAIL(超区间)
    E2  单句台词 <=25 字                            WARN(逐句)
    E3  场景数 <=2 ([场景] 标记计数)                FAIL(>2)
    E4  黄金前3秒: 首个动作/台词行含冲突信号词       FAIL(无)
    E5  开篇禁词(起床/拉窗帘/太阳升起/走在路上等)     WARN
    E6  断章卡点: 存在【本集断章卡点】且含黑屏/悬念   FAIL(缺)
    E7  情绪流变词: 存在【情绪流变】链条(-> 或 ➔)    WARN(缺)
    E8  复读检测: 主角台词与前集传入(--prev)重复     WARN(重复句)
    E9  对白攻防回合: 存在 >=4 轮"人物:台词"对白     WARN(不足)
    E10 合规红线词(断肢/开膛/下蛊等一票否决直观描写)  FAIL
退出码: 0=通过(可含WARN), 1=FAIL, 2=用法错误
"""
import re
import sys

NET_MIN, NET_MAX = 350, 500
SENT_MAX = 25

OPEN_BAN_WORDS = ["早晨起床", "起床", "拉窗帘", "太阳升起", "醒过来", "走在路上",
                  "整理衣服", "开车上班", "喝咖啡闲聊", "悠闲的清晨", "阳光明媚的早晨"]

CONFLICT_SIGNALS = ["△", "！?", "！", "枪", "刀", "巴掌", "扔", "砸", "吼", "冷笑",
                    "逼", "跪", "撕", "拍在", "顶在", "推", "踹", "骂", "羞辱", "退婚",
                    "病危", "签字", "死", "滚", "住手", "救"]

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
    """净字数: 对白+动作指示行(△/[场景]/[人物]行与对白), 去标记与空白标点"""
    total = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        d = _is_dialogue(s)
        if d is not None:
            body = d
        elif s.startswith("△") or s.startswith("[") or s.startswith("【"):
            body = re.sub(r"^[△\[\]【】人场景物本集情绪流白动作]{0,8}", "", s)
        else:
            continue
        body = re.sub(r"[\s，。！？；：、…—\-·“”\"'‘’（）()《》!?.]", "", body)
        total += len(body)
    return total


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


def validate(text, prev_texts=()):
    fails, warns = [], []
    nc = net_chars(text)
    if not (NET_MIN <= nc <= NET_MAX):
        fails.append(f"E1 剧本净字数 {nc} 不在 {NET_MIN}~{NET_MAX} 区间")

    for line in text.splitlines():
        d = _is_dialogue(line)
        if d:
            clean = re.sub(r"[\s，。！？；：、…—]", "", d)
            if len(clean) > SENT_MAX:
                warns.append(f"E2 单句台词 {len(clean)} 字(>{SENT_MAX}): {clean[:18]}…")

    sc = scene_count(text)
    if sc > 2:
        fails.append(f"E3 场景数 {sc} >2")
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

    if not re.search(r"【情绪流变】.*(->|➔|→)", text):
        warns.append("E7 缺【情绪流变】链条(应标: 遭受刁难 ➔ … ➔ 绝命断章)")

    rounds = 0
    my_lines = [d for d in (_is_dialogue(l) for l in text.splitlines()) if d]
    rounds = len(my_lines)
    if rounds < 4:
        warns.append(f"E9 对白回合仅 {rounds} 轮(<4)，攻防结构不足")

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
    print("[+] self-test PASSED" if ok else "[-] self-test FAILED")
    return 0 if ok else 1


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 2
    if args[0] == "--self-test":
        return self_test()
    path = args[0]
    prevs = []
    if "--prev" in args:
        i = args.index("--prev")
        for p in args[i + 1:]:
            if p.startswith("--"):
                break
            prevs.append(open(p, encoding="utf-8").read())
    text = open(path, encoding="utf-8").read()
    fails, warns, nc = validate(text, prevs)
    print(f"== {path}  净字数≈{nc} ==")
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
