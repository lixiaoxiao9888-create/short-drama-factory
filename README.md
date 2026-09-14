# Short-Drama Factory v3.0 · 抖音/红果爆款短剧工业化编剧超级系统

纯剧本引擎：把一句创意 / 一部网文 / 一个脑洞，稳定转化为符合红果付费生态的爆款短剧剧本。**只产剧本层，不含分镜/资产/视频制作衔接。**

## v3.0 相对 v2.0 的升级

1. **情绪流单一矛盾往返法**（`references/emotion-flow-roundtrip.md`）：立项先判流派（情绪流⇄剧情流）；核心执念钉死、六档证据阶梯×六档反驳成本阶梯、几集一回合、中点攻守转换对位第一付费墙；含下沉题材批量生成器。
2. **跨集连续性台账**（`references/continuity-ledger.md` + `templates/ledger.md` + `/连写 N-M` 模式）：伏笔/人物/道具/规则四账，无台账不开写，多集连写不穿帮。
3. **网文改编流水线**（`references/webnovel-adaptation.md`）：抽取→砍并→章集映射→回合化→入系统，兑现"网文→剧本"。
4. **人物圣经**（`references/character-bible.md`）：欲望/秘密/弧光/语言指纹四件套 + 功能位配额，先于大纲建档。
5. **机制级仿写**（`references/mechanism-imitation.md`）：结构可仿、表达不可抄的三层拆解与换皮规程。
6. **结构三档化**（`references/hongguo-beat-sheet.md`）：60/80/100 集变体、付费墙换算、剧情流变体、漫剧适配位；题材扩至 12+ 赛道（`genre-map.md`）。
7. **红线机器化**：`scripts/validate_episode.py`（净字数 350~500 / 单句 ≤25 / 场景 ≤2 / 前3秒冲突 / 断章存在 / 复读检测 / 合规红线）与 `scripts/validate_series.py`（伏笔超期 / 死人开口 / 断章缺失扫描 / 付费墙落位 / 四账齐全），均含 self-test。

## 七交互模式

`/立项大纲` `/全剧大纲` `/分集规划` `/写剧本 第N集` `/剧本医生` `/极速短剧` `/合规审核` + v3.0 新增 **`/连写 N-M`**（带台账批量生产）。

## 快速开始

```bash
# 安装到技能目录后直接对话："写短剧" "立项：赘婿战神" "/连写 1-5"
python3 scripts/validate_episode.py --self-test
python3 scripts/validate_series.py --self-test
```

## 结构

```text
short-drama-factory/
├── SKILL.md                    # 入口：流派判定门+七模式+8红线+执行顺序
├── references/                 # 11 个权威库（往返法/台账/改编/圣经/仿写/题材/结构/钩子/断章/台词/合规）
├── templates/                  # 台账空表 + 单集排版
├── scripts/                    # 单集机检 + 全剧台账机检
└── examples/ep01-longwang-demo.md
```

MIT · 基于 v2.0（GitHub lixiaoxiao9888-create/short-drama-factory）升级。
