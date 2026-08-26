# 抖音/红果爆款短剧工业化编剧超级系统 v2.0（Short-Drama Factory）

> 专精红果短剧生态的**商业编剧引擎** · 抖音/红果爆款短剧工业化编剧超级系统
> AI Short-Drama Commercial Screenwriting Engine for Douyin & Hongguo — v2.0

一个把「一句创意 / 一部网文 / 一个脑洞」稳定转化为**符合红果付费生态的爆款短剧剧本**的 OpenClaw Skill。核心差异化：**聚焦纯剧本定位，只产出编剧层内容，不含制作衔接**——把碎片灵感或原著高效转化为符合实拍标准的爆款剧本。

An OpenClaw Skill that turns a one-line idea, a web novel, or a creative spark into a hit short-drama script optimized for the Hongguo/Douyin paid-content ecosystem. It is a **pure screenwriting engine** — no production handoff — built around completion rate, emotional density, anti-exposition dialogue, and commercial paywall design.

---

## ✨ 特性 / Features (v2.0)

- **六交互模式**：`/立项大纲` `/全剧大纲` `/分集规划` `/写剧本` `/剧本医生` `/极速短剧` `/合规审核`
- **红果 80 集付费墙排布**：第 10-15 / 28-32 / 55-58 三级卡点 + 付费墙三法则（前置蓄水 / 断在反击前 0.5 秒 / 付费后即时兑现）
- **黄金前 3 秒五大母型 × 20 变体钩子库**：生死绝境 / 极端羞辱 / 身份暴涨 / 物证背叛 / 规则悬念
- **四大断章公式**：掉马前一秒 / 物理悬停 / 反差金句 / 绝境二选一 + 标准断章格式
- **剧本医生台词七维诊断**：语言指纹 / 反向灌输死刑法 / 攻防对白回合制 / 单句 ≤15 字 + 实战改写案例库
- **单集硬性体量控制**：90-120 秒 / 净字数 350-500 / 语速 3.5-4.5 字/秒 / 场景 ≤2 个
- **微表情应激反应**：只写生理可观测动作，拒绝抽象心理词
- **平台合规体系**：敏感词替换库 + 平台一票否决红线

## 🚀 快速开始 / Quick Start

```bash
# 放到 OpenClaw 的 skills 目录
cp -r short-drama-factory ~/.openclaw/workspace/skills/

# 然后直接对话触发：
# "写短剧" / "短剧大纲" / "立项大纲" / "写第1集" / "剧本医生" / "极速短剧"
```

## 📁 目录结构 / Structure

```
short-drama-factory/
├── SKILL.md                          # 入口：定位、铁律、五阶编剧工作流、红线、合规
├── references/
│   ├── genre-tropes-and-emotions.md      # 男频/女频赛道爽点、套路与人物弧光
│   ├── hongguo-80ep-beat-sheet.md        # 红果/抖音 80-100 集架构、节奏与付费墙排布
│   ├── golden-3s-hook-library.md         # 黄金前 3 秒五大母型 × 20 变体钩子库
│   ├── cliffhanger-master-formulas.md    # 红果爆款绝命断章四大公式
│   ├── dialogue-doctor-anti-ai.md        # 剧本医生台词七维诊断与去 AI 反灌输
│   └── screenplay-compliance-rules.md    # 平台合规与敏感词替换转译库
```

## 📜 版本历史 / Changelog

- **v2.0（2026-08-26）**：覆盖升级为红果专精商业编剧引擎。新增六交互模式、红果 80 集付费墙排布、黄金前 3 秒钩子库、四大断章公式、剧本医生台词七维诊断、单集硬性体量控制。聚焦纯剧本定位，移除旧版制作衔接/生产机制层。
- **v1.x（2026-08）**：短剧剧本工业化生产系统（机制级仿写、无版权合规、五步流水线、七段式主线、五级爽点阶梯、合规门禁）。

## 📄 许可 / License

MIT License · Copyright (c) 2026 lixiaoxiao9888-create (老李)
