<div align="center">
  <img src="assets/banner.svg" alt="Short-Drama Factory v3.0" width="100%">
  <br><br>

  <h3>抖音 / 红果 爆款短剧 · 工业化编剧超级系统</h3>
  <p><b>把「一句创意 / 一部网文 / 一个脑洞」稳定转化为符合红果付费生态的爆款短剧剧本</b><br>
  An OpenClaw Skill — pure screenwriting engine, no production handoff.</p>

  <p>
    <img src="https://img.shields.io/badge/version-3.0.0-f5c451?style=for-the-badge" alt="version">
    <img src="https://img.shields.io/badge/OpenClaw-Skill-7c3aed?style=for-the-badge" alt="OpenClaw Skill">
    <img src="https://img.shields.io/badge/python-3.x-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="python">
    <img src="https://img.shields.io/badge/license-MIT-3da639?style=for-the-badge" alt="license">
  </p>

  <p>
    <img src="https://img.shields.io/badge/赛道-12%2B-e5484d?style=flat-square" alt="tracks">
    <img src="https://img.shields.io/badge/结构-60%20%2F%2080%20%2F%20100%20集-8b5cf6?style=flat-square" alt="structure">
    <img src="https://img.shields.io/badge/机检-单集%20%2B%20全剧-2ea043?style=flat-square" alt="linters">
    <img src="https://img.shields.io/badge/定位-纯剧本层-ff9f1c?style=flat-square" alt="scope">
  </p>
</div>

---

> **一句话**：这是给短剧 / 漫剧编剧与内容团队的**纯剧本引擎**——从一句创意或一部网文出发，自动完成「流派判定 → 人物体系 → 60–100 集大纲 → 付费墙卡点 → 分集 → 单集正文 → 医生精修 → 机检 → 合规」。**只产剧本层，不含分镜 / 资产 / 视频制作衔接。**

## ✨ 核心特性

| | 特性 | 说明 |
|:--:|:--|:--|
| 🎯 | **立项先判流派** | 情绪流走「单一矛盾往返回合表」，剧情流走「信息阶梯」；判错流派后面全白写 |
| 🔁 | **情绪流往返法** | 六档证据阶梯 × 六档反驳成本阶梯，任何执念题材十分钟拉出全剧骨架 |
| 🧱 | **60 / 80 / 100 三档结构** | 四幕占比 + 三级付费墙换算 + 中点攻守转换对位 |
| 📒 | **跨集连续性台账** | 伏笔 / 人物 / 道具 / 规则四账，`/连写` 批量生产不穿帮 |
| 📖 | **网文改编流水线** | 抽取 → 砍并 → 章集映射 → 回合化 → 入系统 |
| 👥 | **人物圣经** | 欲望 / 秘密 / 弧光 / 语言指纹四件套 + 功能位配额，先于大纲建档 |
| 🧬 | **机制级仿写** | 结构可仿、表达不可抄的三层拆解与换皮规程 |
| ✅ | **红线机器化** | 单集 + 全剧双机检脚本，硬体量 / 断章 / 复读 / 伏笔超期全兜底 |

## 🔄 七交互模式

| 模式 | 指令 | 输入 | 核心产出 |
|:--|:--|:--|:--|
| 0 · 商业立项 | `/立项大纲` `/策划` | 脑洞 / 题材 / 原著概况 | 流派判定 → 赛道锚定 → 人物体系 → 四幕大纲 + 二选一 |
| 1 · 全剧节奏 | `/全剧大纲` `/卡点规划` | 已确认大纲 | 60/80/100 节奏曲线 + 付费墙 + **核心矛盾往返回合表** |
| 2 · 分集规划 | `/分集规划 1-10` | 集数范围 | 单集冲突 + 场景铺排 + 集尾钩子 + **台账更新** |
| 3 · 单集撰写 | `/写剧本 第N集` | 集数 + 情节 | 90~120 秒标准正文 → **过 `validate_episode`** |
| 4 · 剧本医生 | `/剧本医生` `/精修` | 草稿 | 台词七维暴改 + 断章打磨 + **复读检测** |
| 5 · 极速直出 | `/极速短剧` `/直接写` | 小说片段 / 梗概 | 静默全门控，直出 1~5 集足额剧本 |
| 6 · 合规自检 | `/合规审核` `/自检` | 剧本正文 | 平台红线排查 + 敏感词转译 |
| 7 · 批量连写 | `/连写 1-10` | 集数区间 | **带台账的逐集生产**，伏笔 / 人物 / 道具全程对账 |

## 🧭 唯一执行顺序

```mermaid
flowchart LR
    A[任务理解] --> B[流派判定] --> C[赛道锚定] --> D[人物圣经]
    D --> E[全剧结构<br/>含回合表] --> F[分集规划] --> G[单集撰写]
    G --> H[医生精修] --> I[机检<br/>单集 + 台账] --> J[合规]
    style B fill:#f5c451,stroke:#c88a1e,color:#2b2200
    style E fill:#8b5cf6,stroke:#6d3fd6,color:#fff
    style I fill:#2ea043,stroke:#1f7a30,color:#fff
```

> 冲突裁决顺序：**当前用户明确要求 > 本 skill > 对应权威 reference > 其他**。

## 📂 目录结构

```text
short-drama-factory/
├── SKILL.md                       # 入口：七模式 + 8 条绝对红线 + 执行顺序
├── references/                    # 11 个权威库
│   ├── emotion-flow-roundtrip.md  # ★ 情绪流单一矛盾往返法引擎
│   ├── hongguo-beat-sheet.md      # ★ 60/80/100 三档结构 + 付费墙
│   ├── continuity-ledger.md       # ★ 跨集连续性台账
│   ├── character-bible.md         #   人物圣经四件套
│   ├── webnovel-adaptation.md     #   网文 → 分集改编流水线
│   ├── mechanism-imitation.md     #   机制级仿写与版权边界
│   ├── genre-map.md               #   12+ 赛道题材全图
│   ├── golden-3s-hook-library.md  #   黄金前 3 秒 5 母型 × 20 变体
│   ├── cliffhanger-master-formulas.md  # 四大断章公式
│   ├── dialogue-doctor-anti-ai.md #   台词七维诊断
│   └── screenplay-compliance-rules.md  # 合规红线 + 敏感词替换库
├── templates/                     # 台账空表 + 单集标准排版
├── scripts/                       # 单集机检 + 全剧台账机检（含 self-test）
├── examples/                      # 示例单集
└── assets/banner.svg
```

## 🚀 快速开始

```bash
# 1) 放入 skills 目录
cp -r short-drama-factory ~/.openclaw/workspace/skills/

# 2) 自检脚本
python3 scripts/validate_episode.py --self-test
python3 scripts/validate_series.py   --self-test
```

```text
# 3) 直接对话触发：
"写短剧" · "立项大纲：赘婿战神" · "/全剧大纲 (80集)"
"/分集规划 1-10" · "/写剧本 第1集" · "/剧本医生" · "/连写 1-5"
```

## 🧪 机身机检（红线机器化）

```bash
python3 scripts/validate_episode.py <单集剧本.md> [--prev 前集.md ...]
python3 scripts/validate_series.py  <台账.md> [--episodes 80] [--script-dir 剧本目录]
```

| 脚本 | 检查项 |
|:--|:--|
| `validate_episode.py` | 净字数 350~500 · 单句 ≤25 · 场景 ≤2 · 前 3 秒冲突 · 断章存在 · 情绪流变链 · 复读检测 · 合规红线 |
| `validate_series.py` | 伏笔超期 · 死人开口 · 断章缺失扫描 · 付费墙落位 · 四账齐全 |

> `FAIL` 必须修复后重跑，不得裸交。

## 📦 版本历史

- **v3.0**（2026-09-13）· 情绪流单一矛盾往返法 · 跨集连续性台账 · 网文改编流水线 · 人物圣经 · 机制级仿写 · 60/80/100 三档结构 · 单集 + 全剧机检脚本
- **v2.0**（2026-08-26）· 红果专精商业编剧引擎：六交互模式 · 80 集付费墙 · 黄金 3 秒钩子 · 四大断章 · 台词七维 · 单集体量控制
- **v1.x**（2026-08）· 短剧剧本工业化生产系统：机制级仿写 · 无版权合规 · 五步流水线 · 七段式主线 · 五级爽点阶梯

<div align="center">
  <br>
  <sub><b>MIT License</b> · Copyright © 2026 lixiaoxiao9888-create (老李)</sub>
</div>
