#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v5.1 交付前终检闸门（三态强制：PASS=0 / BLOCKED=1 / INCOMPLETE=3）

用法:
    python scripts/final_qc.py <剧本目录> [--ledger 台账.md] [--partial] [--format auto|standard|long|manju] [--out 终检报告.md]
    python scripts/final_qc.py --self-test
"""
import argparse
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import validate_episode as ve

EP_NAME_RE = re.compile(r"^(?:EP|ep|第)?0*(\d+)(?:集)?\.md$")
STOP_WORDS = {"黑屏", "下滑", "立即", "解锁", "第", "集", "画面", "定格", "定住", "突然", "众人"}


def find_episodes(script_dir):
    eps = []
    if not os.path.isdir(script_dir):
        return eps
    for fn in os.listdir(script_dir):
        m = EP_NAME_RE.match(fn)
        if m:
            eps.append((int(m.group(1)), fn, os.path.join(script_dir, fn)))
    eps.sort(key=lambda x: x[0])
    return eps


def extract_keywords(text):
    tokens = re.findall(r"[\u4e00-\u9fa5]{2,4}", text)
    return {t for t in tokens if t not in STOP_WORDS}


def opening_body_lines(text, n=10):
    """交付补丁新增: 取开场正文前 n 个非空行, 跳过头部元数据与场景/人物标注行。

    根因: 旧实现用 [非空行][:12], 而标准模板头部字段(第X集/所属阶段/钩子/冲突形态/
    情绪流变/执念/时长... + [场景] + [人物])恰好占满 12 行, 合规稿件的 △/台词正文
    永远进不了窗口 -> C1 对任何规范排版都必然误报。此处按行首特征过滤后再截取。
    """
    skip_prefixes = ("【", "[场景", "[人物", "##", "# ", ">")
    body = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # 集标题行: 第【01】集... / 第1集...
        if re.match(r"^第[【\d]", s):
            continue
        if s.startswith(skip_prefixes):
            continue
        body.append(s)
        if len(body) >= n:
            break
    return "\n".join(body)


def check_ledger_via_series(ledger_path):
    """联动 validate_series.py 对台账执行 S1~S8 机检，返回 (fails, warns)"""
    vs_path = os.path.join(SCRIPT_DIR, "validate_series.py")
    if not os.path.isfile(vs_path):
        return [], ["未找到 validate_series.py，跳过台账 S1~S8 机检"]
    # 交付补丁修复: 从台账头部读取"总集数"，透传 --episodes，避免按默认 80 集口径误报 S6 付费墙区间
    episodes = None
    try:
        head = open(ledger_path, encoding="utf-8-sig").read(4096)
        m_ep = re.search(r"总集数\s*[:：]\s*(\d{1,4})", head)
        if m_ep:
            episodes = int(m_ep.group(1))
    except OSError:
        pass
    cmd = [sys.executable, vs_path, ledger_path]
    if episodes:
        cmd += ["--episodes", str(episodes)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    l_fails, l_warns = [], []
    for line in (res.stdout + "\n" + res.stderr).splitlines():
        s = line.strip()
        if "FAIL:" in s or s.startswith("[-]"):
            l_fails.append(f"台账机检: {s}")
        elif "WARN:" in s or s.startswith("[!]"):
            l_warns.append(f"台账机检: {s}")
    if res.returncode not in (0, 1) and not l_fails:
        l_fails.append(f"台账机检异常退出 (exit={res.returncode})")
    return l_fails, l_warns


def run_final_qc(script_dir, ledger_path=None, partial=False, fmt="auto"):
    eps = find_episodes(script_dir)
    incompletes = []
    blocks = []
    warns = []

    if not eps:
        incompletes.append("目录内未找到任何剧本文件（需命名为 EP01.md / 1.md / 第1集.md）")
    else:
        nums = [x[0] for x in eps]
        if len(nums) != len(set(nums)):
            incompletes.append(f"存在重复集号: {nums}")
        expected = list(range(nums[0], nums[-1] + 1))
        missing = sorted(set(expected) - set(nums))
        if missing:
            incompletes.append(f"集号不连续，缺失集数: {missing}")
        if not partial and nums[0] != 1:
            incompletes.append(f"非局部批次（未加 --partial）但起始集号为 {nums[0]} 而非第 1 集")

    ledger_checked = False
    if ledger_path and os.path.isfile(ledger_path):
        lf, lw = check_ledger_via_series(ledger_path)
        blocks.extend(lf)
        warns.extend(lw)
        ledger_checked = True
    elif not partial:
        incompletes.append("非局部批次必须提供存在的台账文件（--ledger <台账.md>）")

    texts = []
    for num, fn, path in eps:
        txt = open(path, encoding="utf-8").read()
        prev_texts = [t for _, _, t in texts[-2:]]
        f, w, nc = ve.validate(txt, prev_texts=prev_texts, profile=fmt)
        for item in f:
            blocks.append(f"第{num}集({fn}): {item}")
        for item in w:
            warns.append(f"第{num}集({fn}): {item}")
        texts.append((num, fn, txt))

    # 跨集正文级检查 C1: 断章与下集开场前10行衔接
    for i in range(len(texts) - 1):
        n1, fn1, t1 = texts[i]
        n2, fn2, t2 = texts[i + 1]
        m = re.search(r"【本集断章卡点】\s*[:：]?\s*(.+)", t1)
        if m:
            kws = extract_keywords(m.group(1))
            head10 = opening_body_lines(t2)
            if kws and not any(k in head10 for k in kws):
                warns.append(f"C1 跨集衔接提示: 第{n1}集断章关键词({','.join(list(kws)[:4])})未在第{n2}集开场正文前10行复现，请人工确认是否接续")

    # 跨集检查 C3: 金额汇总供复核
    money_by_ep = []
    for num, fn, txt in texts:
        ms = re.findall(r"(?:[一二三四五六七八九十百千万亿]+|\d+(?:\.\d+)?)\s*(?:万|亿|千)?(?:元|两|块)", txt)
        if ms:
            money_by_ep.append(f"EP{num}: {'/'.join(list(dict.fromkeys(ms))[:4])}")

    if incompletes:
        status, code = "INCOMPLETE", 3
    elif blocks:
        status, code = "BLOCKED", 1
    else:
        status, code = "PASS", 0

    report = [
        f"# 交付前终检报告（结论：{status}）",
        "",
        "## 一、检查覆盖矩阵",
        f"- **剧本目录**：`{script_dir}`（检出 {len(eps)} 集）",
        f"- **批次模式**：{'局部批次 (--partial)' if partial else '整剧交付校验'}",
        f"- **台账 S1~S8 联检**：{'已执行 (' + ledger_path + ')' if ledger_checked else '未提供'}",
        f"- **硬阻断 (FAIL)**：{len(blocks)} 项",
        f"- **复核提示 (WARN)**：{len(warns)} 项",
        "",
    ]
    if incompletes:
        report += ["## 二、未完成项（INCOMPLETE · 不得交付）"] + [f"- [ ] {x}" for x in incompletes] + [""]
    if blocks:
        report += ["## 三、阻断硬伤（BLOCKED · 必须修复）"] + [f"- ❌ {x}" for x in blocks] + [""]
    if warns:
        report += ["## 四、人工复核提示（WARN）"] + [f"- ⚠️ {x}" for x in warns] + [""]
    report += [
        "## 五、跨集数值与人工抽检项（需人工确认）",
        f"- **跨集金额出现记录**：{'；'.join(money_by_ep) if money_by_ep else '无明显金额'}",
        "- [ ] 人工确认：退场/死亡角色在后续集数未复活或无交代开口（L2）",
        "- [ ] 人工确认：核心道具归属转移与断章悬念在下一集已兑现（L3/L4）",
    ]
    return status, code, "\n".join(report)


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ep1 = os.path.join(td, "EP01.md")
        ep2 = os.path.join(td, "EP02.md")
        open(ep1, "w", encoding="utf-8").write(ve.GOOD)
        open(ep2, "w", encoding="utf-8").write(ve.GOOD.replace("第【1】集", "第【2】集"))
        st, code, _ = run_final_qc(td, ledger_path=None, partial=False)
        assert st == "INCOMPLETE" and code == 3, f"应为 INCOMPLETE(3)，实得 {st}({code})"
        st, code, _ = run_final_qc(td, ledger_path=None, partial=True)
        assert st == "PASS" and code == 0, f"应为 PASS(0)，实得 {st}({code})"
        open(ep2, "w", encoding="utf-8").write(ve.BAD)
        st, code, _ = run_final_qc(td, ledger_path=None, partial=True)
        assert st == "BLOCKED" and code == 1, f"应为 BLOCKED(1)，实得 {st}({code})"
    print("[+] final_qc.py self-test PASSED")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description="short-drama-factory v5.1 交付前终检闸门")
    p.add_argument("script_dir", help="剧本目录")
    p.add_argument("--ledger", default=None, help="台账文件路径（提供时自动联动 validate_series.py）")
    p.add_argument("--partial", action="store_true", help="声明为局部批次（免整剧集数/台账阻断）")
    p.add_argument("--format", default="auto", choices=["auto", "standard", "long", "manju"])
    p.add_argument("--out", default=None, help="输出终检报告路径")
    args = p.parse_args()
    status, code, rep = run_final_qc(args.script_dir, args.ledger, args.partial, args.format)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(rep)
        print(f"[+] 终检完成: {status} (报告已写入 {args.out})")
    else:
        print(rep)
    return code


if __name__ == "__main__":
    sys.exit(main())
