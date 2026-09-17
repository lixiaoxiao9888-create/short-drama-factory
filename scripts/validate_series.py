#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v3.2 全剧台账机检

用法:
    python3 validate_series.py <台账.md> [--episodes 80] [--script-dir 剧本目录]
    python3 validate_series.py --self-test

台账为 markdown 表格文件（templates/ledger.md 格式），四类账：
    伏笔账 / 人物账 / 道具账 / 世界观规则账

总集数 --episodes 决定付费墙区间：标准档 60/80/100 集；长档（约3分钟/集）30/40/50 集
（1 长档集 ≈ 2 标准集，墙集数减半，见 references/hongguo-beat-sheet.md §二/§四）。

检查项:
    S1  伏笔"拟收"超期: 状态含 埋/养/未收 且 当前集>拟收+3      WARN
    S2  伏笔废置: 状态"废"但正文未给废弃说明列               WARN
    S3  死人开口: 人物账状态含 死/失踪 但剧本目录中其后集数该角色有对白行  FAIL
    S4  人物无档案: 剧本目录出现【角色】名册外人名            WARN(需--script-dir)
    S5  断章缺失扫描: --script-dir 时逐集查【本集断章卡点】    FAIL(缺)
    S6  付费墙落位: 三档总集数下墙集区间内无"墙"标记行         WARN
    S7  台账必备四表齐全                                      FAIL(缺表)
退出码: 0=通过, 1=FAIL, 2=用法错误
"""
import re
import sys
import pathlib

WALL_RANGES = {60: [(8, 11), (21, 24), (41, 44)], 80: [(10, 15), (28, 32), (55, 58)], 100: [(13, 19), (35, 40), (68, 73)],
               # 长档（约 3 分钟/集）：集数减半，墙集区间同步折算
               30: [(4, 6), (10, 12), (20, 22)], 40: [(5, 8), (14, 16), (27, 29)], 50: [(7, 10), (17, 20), (34, 37)]}
TABLE_KEYS = {"伏笔": "伏笔账", "人物": "人物账", "道具": "道具账", "规则": "世界观规则账"}


def _rows(text, section_kw):
    """取某账小节后的 markdown 表格数据行"""
    m = re.search(r"#+.*?" + section_kw + r".*?\n(.*?)(?=\n#+\s|\Z)", text, re.S)
    if not m:
        return None
    rows = []
    for line in m.group(1).splitlines():
        s = line.strip()
        if s.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", s):
            cells = [c.strip() for c in s.strip("|").split("|")]
            rows.append(cells)
    return rows[1:] if rows else []  # 去表头


def validate_ledger(text, total_eps=80, scripts=None):
    fails, warns = [], []
    # S7 四表存在
    for kw in TABLE_KEYS.values():
        if not re.search(r"#+.*?" + kw, text):
            fails.append(f"S7 台账缺「{kw}」表")
    # 当前集 = 台账"最后更新集"或剧本最大集数
    mm = re.search(r"当前集[:：]\s*(\d+)", text)
    cur = int(mm.group(1)) if mm else (max(scripts) if scripts else total_eps)

    # S1/S2 伏笔账
    fb = _rows(text, "伏笔") or []
    for r in fb:
        if len(r) < 5:
            continue
        plan, state = r[3], r[4].strip()
        try:
            pn = int(plan)
        except ValueError:
            warns.append(f"S1 伏笔「{r[1][:12]}」拟收集数非数字: {plan}"); continue
        # 状态宽松匹配: 埋/养/未收 归为待收; "收"开头视为已收
        is_open = ("埋" in state or "养" in state or "未收" in state) and not state.startswith("收")
        if is_open and cur > pn + 3:
            warns.append(f"S1 伏笔「{r[1][:12]}」超期未收(拟收{pn}集,现{cur}集,状态{state})")
        if state.startswith("废") and (len(r) < 6 or not r[5]):
            warns.append(f"S2 伏笔「{r[1][:12]}」标废但未写原因")

    # S3 死人开口
    dead = {}
    for r in (_rows(text, "人物") or []):
        if len(r) < 3:
            continue
        if re.search(r"死|殒|失踪", r[2]):
            mm2 = re.search(r"(\d+)", r[4] if len(r) > 4 else r[2])
            dead[r[0].strip()] = int(mm2.group(1)) if mm2 else cur
    if scripts:
        for ep in sorted(scripts):
            for name, at in dead.items():
                if ep > at:
                    body = scripts[ep]
                    if re.search(r"^" + re.escape(name[:4]) + r"(\(|（|[:：])", body, re.M):
                        fails.append(f"S3 「{name}」第{at}集后状态死亡/失踪，但第{ep}集有对白")

    # S4 名册外角色
    roster = {r[0].strip() for r in (_rows(text, "人物") or []) if len(r) > 0}
    if scripts and roster:
        NOISE = {"第", "场景", "人物", "本集", "所属", "黄金", "情绪", "备注", "接上",
                 "声音", "旁白", "画外音", "内心独白", "镜头", "字幕", "提示", "音效"}
        for ep in sorted(scripts):
            seen = set()
            for m2 in re.finditer(r"^([\u4e00-\u9fa5A-Za-z0-9]{1,8})(?:（[^）]*）|\([^)]*\))?\s*[:：]", scripts[ep], re.M):
                nm = m2.group(1)
                if nm in NOISE or nm in seen:
                    continue
                seen.add(nm)
                if nm not in roster and not any(nm in x or x in nm for x in roster):
                    warns.append(f"S4 第{ep}集台词角色「{nm}」不在人物账名册")

    # S5 断章缺失
    if scripts:
        for ep in sorted(scripts):
            if not re.search(r"【本集断章卡点】|\[本集断章", scripts[ep]):
                fails.append(f"S5 第{ep}集缺【本集断章卡点】")

    # S6 付费墙标记
    ranges = WALL_RANGES.get(total_eps, WALL_RANGES[80])
    # 收集台账中"墙+集数"标记: 如 "一级墙 第12集" 或 "第12集(墙)"
    marks = []
    for m in re.finditer(r"墙[^\n]{0,12}?(\d+)\s*[-~至]?\s*(\d+)?", text):
        marks.append(int(m.group(1)))
        if m.group(2):
            marks.append(int(m.group(2)))
    for lo, hi in ranges:
        if not any(lo <= x <= hi for x in marks):
            warns.append(f"S6 未见付费墙落在第{lo}~{hi}集区间(三档各需一条'X级墙 第N集'标记)")
    return fails, warns, cur


LEDGER_GOOD = """# 台账：demo 项目
当前集: 30

## 伏笔账
| ID | 内容 | 埋于 | 拟收 | 状态 | 备注 |
|---|---|---|---|---|---|
| FB-01 | 旧怀表 | 3 | 28 | 收 | 已当众展开 |
| FB-02 | 神秘来电 | 12 | 31 | 养 | 反派内讧线 |

## 人物账
| 角色 | 首出 | 状态 | 关系 | 变动集 | 备注 |
|---|---|---|---|---|---|
| 林辰 | 1 | 存活 | 主角 | 30 | |
| 陈峰 | 1 | 死亡 | 敌 | 25 | 第25集坠楼 |

## 道具账
| 道具 | 持有 | 状态 | 变动集 |
|---|---|---|---|
| 玄铁令 | 林辰 | 怀中 | 12 |

## 世界观规则账
| 规则 | 确立集 | 引用集 | 违反 |
|---|---|---|---|
| 龙王令只一次 | 12 | 25 | 否 |

付费墙落位: 一级墙 第12集(中点转换) / 二级墙 第30集 / 三级墙 第56集
"""

EP_GOOD = """第【3】集
[场景]：内景·大堂
△ 巴掌甩到半空停住。
陈峰：签了它。
林辰：你确定？
【本集断章卡点】：门外齐跪，"参见殿下"喊到一半——（黑屏）
"""
EP_BAD = """第【4】集
[场景]：内景·大堂
△ 对峙。
林辰：滚。
陈峰：好。
"""


def self_test():
    ok = 1
    scripts = {3: EP_GOOD, 4: EP_BAD}
    f, w, cur = validate_ledger(LEDGER_GOOD, 80, scripts)
    if not any("S5" in x and "第4集" in x for x in f):
        print("FAIL self-test: 第4集缺断章应报 S5:", f); ok = 0
    if any("S1" in x for x in w):
        print("FAIL self-test: 未超期不应报 S1:", w); ok = 0
    # 死人开口: 给第30集加陈峰对白
    scripts2 = {3: EP_GOOD, 4: EP_BAD, 30: "第【30】集\n[场景]：内景·大宅\n△ 对峙。\n陈峰（阴笑）：我回来了。\n【本集断章卡点】：灯灭。（黑屏）\n"}
    f2, _, _ = validate_ledger(LEDGER_GOOD, 80, scripts2)
    if not any("S3" in x for x in f2):
        print("FAIL self-test: 死人开口应报 S3:", f2); ok = 0
    if any("S5" in x and "第30集" in x for x in f2):
        print("FAIL self-test: 第30集有断章不该报 S5"); ok = 0
    f3, _, _ = validate_ledger("空台账", 80)
    if len([x for x in f3 if x.startswith("S7")]) < 4:
        print("FAIL self-test: 空台账应报 4 条 S7:", f3); ok = 0

    # 回归: S1 状态宽松(已埋/未收 也算待收) + S4 噪音名过滤
    led2 = LEDGER_GOOD.replace("| FB-02 | 神秘来电 | 12 | 31 | 养 | 反派内讧线 |",
                               "| FB-02 | 神秘来电 | 12 | 8 | 已埋 | 反派内讧线 |")
    f4, w4, _ = validate_ledger(led2, 80, scripts)
    if not any("S1" in x and "FB" not in x or "神秘来电" in x for x in w4):
        print("FAIL self-test: 状态'已埋'超期应报 S1:", w4); ok = 0
    ep_noise = {5: "第【5】集\n[场景]：内景\n△ 拍桌。\n声音：轰鸣。\n林辰：谁？\n陈峰：我。\n【本集断章卡点】：黑屏（黑屏）\n"}
    _, w5, _ = validate_ledger(LEDGER_GOOD, 80, ep_noise)
    if any("「声音」" in x for x in w5):
        print("FAIL self-test: '声音:' 旁白不应报 S4:", w5); ok = 0

    # 回归: S4 同集同角色多行台词只报一次(去重)
    ep_dup = {9: "第【9】集\n[场景]：内景\n△ 对峙。\n陌生人：你是谁？\n陌生人：说话！\n陌生人：再不说我动手了。\n林辰：别急。\n【本集断章卡点】：黑屏（黑屏）\n"}
    _, w6, _ = validate_ledger(LEDGER_GOOD, 80, ep_dup)
    dup_cnt = sum(1 for x in w6 if "「陌生人」" in x)
    if dup_cnt != 1:
        print(f"FAIL self-test: S4 同名角色应只报 1 次，实得 {dup_cnt}", w6); ok = 0

    # 回归: 长档付费墙区间（40 集长档：一级 5~8 / 二级 14~16 / 三级 27~29）
    led_long = LEDGER_GOOD.replace(
        "付费墙落位: 一级墙 第12集(中点转换) / 二级墙 第30集 / 三级墙 第56集",
        "付费墙落位: 一级墙 第6集(中点转换) / 二级墙 第15集 / 三级墙 第28集")
    _, w7, _ = validate_ledger(led_long, 40)
    if any("S6" in x for x in w7):
        print("FAIL self-test: 长档 40 集墙落位不应报 S6:", w7); ok = 0
    _, w8, _ = validate_ledger(LEDGER_GOOD, 40)
    if not any("S6" in x for x in w8):
        print("FAIL self-test: 标准档墙集数按长档 40 集核对应报 S6:", w8); ok = 0

    print("[+] self-test PASSED" if ok else "[-] self-test FAILED")
    return 0 if ok else 1


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 2
    if args[0] == "--self-test":
        return self_test()
    try:
        led = pathlib.Path(args[0]).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"[-] 找不到台账文件: {args[0]}"); return 2
    except UnicodeDecodeError:
        print(f"[-] 台账不是 UTF-8 文本: {args[0]}"); return 2
    total = 80
    if "--episodes" in args:
        try:
            total = int(args[args.index("--episodes") + 1])
        except (IndexError, ValueError):
            print("[-] --episodes 需要一个整数"); return 2
    scripts = None
    if "--script-dir" in args:
        try:
            d = pathlib.Path(args[args.index("--script-dir") + 1])
        except IndexError:
            print("[-] --script-dir 需要一个目录路径"); return 2
        if not d.is_dir():
            print(f"[-] 剧本目录不存在: {d}"); return 2
        scripts = {}
        for p in sorted(d.glob("*.md")):
            m = re.search(r"(\d+)", p.stem)
            if m:
                try:
                    scripts[int(m.group(1))] = p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    print(f"[-] 跳过非 UTF-8 剧本: {p}")
    fails, warns, cur = validate_ledger(led, total, scripts)
    print(f"== {args[0]}  总集数={total} 当前集={cur} ==")
    for x in fails:
        print("[-] FAIL:", x)
    for x in warns:
        print("[!] WARN:", x)
    if fails:
        print("结果: FAILED"); return 1
    print("结果: PASSED" + ("（含 WARN）" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
