#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v5.1 世界规则卡自动反填器（专治剧本优化/精修场景卡流程）

用法:
    python scripts/extract_world_rules.py <剧本.md或目录> [-o world-rules.json]
    python scripts/extract_world_rules.py --self-test
"""
import argparse
import json
import os
import re
import sys


def load_texts(target):
    if os.path.isfile(target):
        return open(target, encoding="utf-8-sig").read()
    if os.path.isdir(target):
        chunks = []
        for fn in sorted(os.listdir(target)):
            if fn.endswith(".md"):
                chunks.append(open(os.path.join(target, fn), encoding="utf-8-sig").read())
        return "\n".join(chunks)
    raise FileNotFoundError(target)


def extract_rules(text):
    is_ancient = any(w in text for w in ("侯府", "皇上", "太后", "王爷", "侍卫", "丫鬟", "银票", "圣旨", "公堂"))
    is_xianxia = any(w in text for w in ("灵力", "宗门", "修仙", "金丹", "元婴", "飞剑", "仙尊"))
    era = "架空古装/礼法社会" if is_ancient else ("玄幻/修仙体系" if is_xianxia else "现代都市/法治社会")

    chars = []
    for m in re.finditer(r"^(?:\[人物\]|【人物】)\s*[:：]?\s*(.+)$", text, re.M):
        for c in re.split(r"[、,，/]", m.group(1)):
            c = re.sub(r"（[^）]*）|\([^)]*\)", "", c).strip()
            if c and c not in chars:
                chars.append(c)

    money = list(dict.fromkeys(re.findall(r"(?:[一二三四五六七八九十百千万亿]+|\d+(?:\.\d+)?)\s*(?:万|亿|千)?(?:元|两|块|灵石)", text)))[:6]
    scenes = list(dict.fromkeys(
        re.sub(r"^(?:\[场景\]|【场景】)\s*[:：]?\s*", "", l.strip())
        for l in text.splitlines() if l.strip().startswith(("[场景]", "【场景】"))
    ))[:6]

    return {
        "schema": "world-rules/1",
        "auto_extracted": True,
        "1_power_ceiling": "朝廷三司/皇权（不可越级私刑）" if is_ancient else ("宗门长老会/天道契约" if is_xianxia else "司法机关/董事会与法定监管机构"),
        "2_stakes_currency": "、".join(money) if money else "（自动反填兜底：待人工核对核心利益标的）",
        "3_spatial_ladder": " -> ".join(scenes) if scenes else "L1 局部冲突空间 -> L2 行业/城际 -> L3 核心圈层 -> L4 终局公审",
        "4_core_evidence": "从原稿提取关键信物/契约/录音（优化时保留原物证名称）",
        "5_golden_finger_cost": "（保留原稿设定；若无明确代价锁，优化时严禁无端新增外挂）",
        "6_address_hierarchy": f"角色名录（锁定禁止改名）：{'、'.join(chars) if chars else '保留原稿全员姓名'}",
        "era_detected": era,
    }


def self_test():
    sample = "第【1】集\n[场景]：内景·侯府正堂·日\n[人物]：沈知微、萧景珩\n△ 沈知微拍出十万两银票和离书。\n"
    res = extract_rules(sample)
    assert res["era_detected"] == "架空古装/礼法社会"
    assert "沈知微" in res["6_address_hierarchy"]
    assert "十万两" in res["2_stakes_currency"]
    print("[+] extract_world_rules.py self-test PASSED")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description="short-drama-factory v5.1 世界规则卡自动反填器")
    p.add_argument("target", help="已有剧本文件或目录")
    p.add_argument("-o", "--out", default=None, help="输出 JSON 路径")
    args = p.parse_args()
    txt = load_texts(args.target)
    data = extract_rules(txt)
    js = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(js)
        print(f"[+] 已反填世界规则卡: {args.out}")
    else:
        print(js)
    return 0


if __name__ == "__main__":
    sys.exit(main())
