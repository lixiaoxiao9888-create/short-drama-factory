#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v5.1 结构化 JSON 导出器（纯格式解析，方便对接下游分镜/平台）

用法:
    python scripts/export_script_json.py <单集剧本.md> [-o ep01.json]
    python scripts/export_script_json.py --self-test
"""
import argparse
import json
import re
import sys


def parse_episode_to_json(text):
    meta = {}
    scenes = []
    current_scene = {"scene": "未标注场景", "characters": [], "beats": []}
    hook = ""

    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("第【") or s.startswith("# "):
            meta["title"] = s
            continue
        # 头部字段：【键】值 与 【键】：值 两种写法都要认（模板实际用的是无冒号写法）；
        # 排除【场景】【人物】以及镜头标签，避免被误吞成 meta
        m_meta = re.match(r"^【(?!场景|人物|特写|慢镜头|镜头)([^】]+)】\s*[:：]?\s*(.+)$", s)
        if m_meta:
            k, v = m_meta.group(1).strip(), m_meta.group(2).strip()
            if k == "本集断章卡点":
                hook = v
            else:
                meta[k] = v
            continue
        if s.startswith(("[场景]", "【场景】")):
            if current_scene["beats"] or current_scene["scene"] != "未标注场景":
                scenes.append(current_scene)
            sc_name = re.sub(r"^(?:\[场景\]|【场景】)\s*[:：]?\s*", "", s)
            current_scene = {"scene": sc_name, "characters": [], "beats": []}
            continue
        if s.startswith(("[人物]", "【人物】")):
            ch_raw = re.sub(r"^(?:\[人物\]|【人物】)\s*[:：]?\s*", "", s)
            current_scene["characters"] = [c.strip() for c in re.split(r"[、,，/]", ch_raw) if c.strip()]
            continue
        if s.startswith("△"):
            current_scene["beats"].append({"type": "action", "text": re.sub(r"^△\s*", "", s)})
            continue
        m_dlg = re.match(r"^([\u4e00-\u9fa5A-Za-z0-9]{1,10})(?:（([^）]*)）|\(([^)]*)\))?\s*[:：]\s*(.+)$", s)
        if m_dlg:
            speaker = m_dlg.group(1)
            cue = (m_dlg.group(2) or m_dlg.group(3) or "").strip()
            line = m_dlg.group(4).strip()
            kind = "voiceover" if speaker in ("内心独白", "独白", "心声", "旁白", "画外音", "画面字幕", "字幕") else "dialogue"
            current_scene["beats"].append({
                "type": kind,
                "speaker": speaker,
                "cue": cue,
                "text": line,
            })

    if current_scene["beats"] or current_scene["scene"] != "未标注场景":
        scenes.append(current_scene)

    return {
        "schema": "short-drama-factory/episode-v1",
        "meta": meta,
        "scenes": scenes,
        "cliffhanger": hook,
    }


def self_test():
    sample = (
        "第【1】集：【开局】\n【本集时长】：100 秒\n"
        "[场景]：内景·正堂·日\n[人物]：甲、乙\n"
        "△ 甲把令牌拍在桌上。\n"
        "甲（拍桌｜厉声）：把账本交出来！\n"
        "内心独白：今天必须拿回属于我的东西。\n"
        "【本集断章卡点】：门被踹开。（黑屏）\n"
    )
    data = parse_episode_to_json(sample)
    assert data["meta"]["title"].startswith("第【1】集")
    assert len(data["scenes"]) == 1
    assert data["scenes"][0]["beats"][1]["type"] == "dialogue"
    assert data["scenes"][0]["beats"][2]["type"] == "voiceover"
    assert "门被踹开" in data["cliffhanger"]
    print("[+] export_script_json.py self-test PASSED")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description="short-drama-factory v5.1 结构化 JSON 导出器")
    p.add_argument("script_file", help="单集剧本 .md 文件")
    p.add_argument("-o", "--out", default=None, help="输出 JSON 路径")
    args = p.parse_args()
    txt = open(args.script_file, encoding="utf-8-sig").read()
    js = json.dumps(parse_episode_to_json(txt), ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(js)
        print(f"[+] 已导出结构化 JSON: {args.out}")
    else:
        print(js)
    return 0


if __name__ == "__main__":
    sys.exit(main())
