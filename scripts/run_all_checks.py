#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v5.1 统一自检入口（覆盖全套 6 个引擎 + 双标杆样章校验）

用法:
    python scripts/run_all_checks.py
"""
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SCRIPTS = [
    "validate_episode.py",
    "validate_series.py",
    "rolling_checkpoint.py",
    "final_qc.py",
    "extract_world_rules.py",
    "export_script_json.py",
]
EXAMPLES = [
    ("examples/ep01-longwang-demo.md", "standard"),
    ("examples/long-format-3min-demo.md", "long"),
]


def main():
    failed = []
    for name in SCRIPTS:
        path = os.path.join(SCRIPT_DIR, name)
        if not os.path.isfile(path):
            print(f"[-] 缺失脚本: {name}")
            failed.append(name)
            continue
        res = subprocess.run([sys.executable, path, "--self-test"], capture_output=True, text=True)
        sys.stdout.write(res.stdout)
        if res.stderr:
            sys.stderr.write(res.stderr)
        if res.returncode != 0:
            failed.append(name)

    ve_path = os.path.join(SCRIPT_DIR, "validate_episode.py")
    for rel, fmt in EXAMPLES:
        ex_path = os.path.join(ROOT_DIR, rel)
        if not os.path.isfile(ex_path):
            print(f"[-] 缺失标杆样章: {rel}")
            failed.append(rel)
            continue
        res = subprocess.run([sys.executable, ve_path, ex_path, "--format", fmt], capture_output=True, text=True)
        sys.stdout.write(res.stdout)
        if res.stderr:
            sys.stderr.write(res.stderr)
        if res.returncode != 0:
            failed.append(rel)

    if failed:
        print(f"[-] 自检未全部通过: {failed}")
        return 1
    print(f"[+] 全部 {len(SCRIPTS)} 项引擎自检 + {len(EXAMPLES)} 份标杆样章校验 PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
