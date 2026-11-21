---
name: short-drama-factory
description: 抖音/红果爆款短剧工业化编剧超级系统 v5.1。纯剧本引擎（全赛道公开通用版，不含制作衔接）。核心：动态按需挂载矩阵（10交互模式x仅挂载核心文件，防Context爆炸）、情绪契约单元链往返法+四级被看见圈层阶梯（L1~L4防中后段注水）、40赛道题材全图（男频12/女频14/中性14）、立项常识与礼法逻辑排雷清单+六栏世界规则卡（支持extract_world_rules自动反填）、前三集极速进场五步拍点+女频A/B双轨进场制（前5句挑明算盘+第1集半场必亮首张反制牌）、六母型钩子库+五大断章公式、A~I九类反转手段轮换矩阵+抗上下文压缩滚动递进状态包（rolling_checkpoint）、三档篇幅（标准 90~120 秒 / 长档 150~195 秒 / 漫剧 60~90 秒）、单集15秒换挡四拍推进、强画面支撑与视听可拍性四门禁（E24/E26/E27/E37~E40）、大白话同轮直给与去括号常态套话（E25/E18c）、优化与改编路径消歧、三态交付终检闸门（final_qc: PASS/BLOCKED/INCOMPLETE）+ 结构化JSON导出。触发：写短剧/短剧大纲/立项/卡点/分集/写长档/剧本医生/剧本优化/精修/终检/极速短剧/合规审核/连写
version: "5.1"
---
# 抖音/红果爆款短剧工业化编剧超级系统 (Short-Drama Factory v5.1)

> **情绪契约单元链**：全剧锚定情绪契约而非单一矛盾 - 矛盾按单元跑（单矛盾硬帽 20~30 集必闭环），三缝合一换矛盾不断气，付费墙挂单元接缝。本引擎覆盖立项分流 -> 人物体系 -> 60/80/100 集大纲 -> 分集正文 -> 滚动防崩连写 -> 三态终检全链路。
>
> **v5.1（2026-11-19 · 跨集防崩闭环 + 视听可拍性四门禁 + 优化路径消歧 + 生态导出升级）**：
> 1. **视听可拍性四门禁（`E37~E40`）**：`scripts/validate_episode.py` 新增 **E37 否定式伪动作拦截**（FAIL，禁“非但没跪/看都没看一眼”）、**E38 道具交接来源闭环**（WARN）、**E39 台词未提先知/幽灵反问**（WARN）、**E40 同空间假切场**（WARN），不越界写分镜，但彻底治好下游拍不出来的硬伤；
> 2. **长剧防崩与三态交付终检**：新增 `scripts/rolling_checkpoint.py`（每 5~10 集生成抗上下文压缩滚动状态包，卸载旧集正文）、`scripts/final_qc.py`（联动 `validate_series.py` 台账 S1~S8 + 跨集断章接续 C1 + 单集汇总，输出 `PASS(0) / BLOCKED(1) / INCOMPLETE(3)` 三态结论）及 `templates/handover-logic-checklist.md`（30 秒一页式逻辑交接自检表）；
> 3. **「优化 ≠ 改编」路径消歧与规则卡自动反填**：新增 `/剧本优化` 模式（保留原稿剧名、主角名与外壳，严禁套用改编换壳流程），并配套 `scripts/extract_world_rules.py` 从原稿自动反填六栏世界规则卡，不再反问用户卡流程；`references/craft-quality-layer.md` 与 `references/mechanism-imitation.md` 新增第一性原理叙事降维外化法则；
> 4. **下游对接与一键全检**：新增 `scripts/export_script_json.py`（将标准老派剧本解析为结构化 JSON 对接下游分镜或平台）与 `scripts/run_all_checks.py`（一条命令跑完全套 6 个引擎自检与双标杆样章验证）。
>
> **v5.0 底座完整保留**：前三集「极速进场五步法 + 女频 A/B 双轨进场制」、立项「礼法/常识逻辑排雷 + 六栏世界规则卡」、中后段「L1~L4 四级圈层阶梯」、`E18c` 去括号常态套话与 `E27` 反机械镜头标签堆砌。
>
> **定位不变：本 skill 只产出剧本层内容，不含分镜/资产/视频制作提示词。**

---

## 档位（篇幅制式，先定档再动笔）

| 档位 | 时长（典型值；可按用户指定/内容调整） | 正文体量【参考·随【本集时长】换算】 | 场景 | 单集拍数 | 全剧集数档 | 机检 |
|---|---|---|---|---|---|---|
| **标准档**（默认） | 90~120 秒 | 480~850 / 330~620 | <=2（弹性，禁死板锁死） | 1 拍（内含15s四挡推进） | 60 / 80 / 100 | `--format standard` |
| **长档** | **150~195 秒（约 2 分半~3 分钟，按内容密度倒推）** | **820~1400 / 660~1150** | **<=3** | **2 拍 + 中段小钩** | **30 / 40 / 50** | `--format long` |
| 漫剧档 | 60~90 秒 | 330~620 | <=2 | 1 拍 | 60 / 80 / 100 | `--format manju` |

未指定档位默认标准档；用户说"长档 / 3 分钟 / 一集三分钟"即切长档。规格权威：`references/hongguo-beat-sheet.md` §三、§四。

---

## 交互模式（显式触发指令，共 10 个）

| 模式 | 指令 | 输入 | 核心产出 |
|---|---|---|---|
| 0. 商业立项 | `/立项大纲` `/策划` | 脑洞/题材/原著概况 | 流派与档位判定 -> 礼法/常识排雷 + 六栏世界规则卡 -> 人物圣经 -> 四幕大纲（含 A/B 进场轨 + L1~L4 圈层） |
| 1. 全剧节奏 | `/全剧大纲` `/卡点规划` `/长档大纲` | 已确认大纲 | 60/80/100（长档 30/40/50）集节奏曲线 + 付费墙卡点 + 情绪契约单元链 |
| 2. 分集规划 | `/分集规划 [范围]` | 如 `/分集规划 1-10` | 单集冲突、15秒四挡铺排、情绪流变词、集尾钩子 + 台账更新 |
| 3. 单集撰写 | `/写剧本 [第N集]` `/写长档 [第N集]` | 集数+情节 | 足额单集正文（前5句亮算盘+半场反制+强画面△+15s换挡+大白话直给+断章）-> 过 `validate_episode.py`（E1~E27 + E37~E40） |
| 4. 剧本医生 | `/剧本医生` `/精修` | 草稿 | 问题卡诊断 + 台词七维重构 + 去括号常态套话 + 清除伪动作（E37~E40） |
| 5. 极速直出 | `/极速短剧` `/直接写` | 小说片段/梗概 | 静默全门控，直出 1~5 集足额剧本 |
| 6. 合规自检 | `/合规审核` `/自检` | 剧本正文 | 平台红线排查 + 敏感词转译 |
| 7. **批量连写** | `/连写 [N-M]` `/连写 长档 [N-M]` | 集数区间 | 单批限写 <=5 集；每 5~10 集跑 `rolling_checkpoint.py` 生成滚动状态包，卸载旧正文防崩 |
| 8. **剧本优化**（v5.1） | `/优化` `/剧本优化` `/改本子` | 用户已有成稿 | **保留原稿剧名、主角名与外壳**；用 `extract_world_rules.py` 从原稿自动反填规则卡（不索要世界观），只提节奏、钩子、对白与可拍性 |
| 9. **交付终检**（v5.1） | `/终检` `/交付前质检` | 剧本目录 + 台账 | 跑 `final_qc.py`（联动台账 S1~S8 + 跨集 C1 接续 + 单集汇总）+ 一页式逻辑交接表，输出 `PASS` / `BLOCKED` / `INCOMPLETE` 三态报告 |

**路径消歧铁律**：`优化（模式8） ≠ 改编（仿写）`。用户拿**自己的成稿**要求优化润色时，**禁止改剧名、禁止改主角姓名、禁止要求用户重填世界规则卡**。

### 动态参考库按需挂载矩阵（Lazy Loading Router）

**严禁一次性全量载入 `references/`**，必须根据交互模式按需读取：

| 交互模式 | 仅需挂载的核心文件 |
|---|---|
| 0. 商业立项 | `references/emotion-flow-roundtrip.md` · `references/genre-map.md` · `references/hongguo-beat-sheet.md` · `references/character-bible.md` · `references/first-three-eps-beat-card.md` · `references/craft-quality-layer.md`（若涉及仿写加挂 `references/mechanism-imitation.md`） |
| 1. 全剧节奏 | `references/hongguo-beat-sheet.md` · `references/emotion-flow-roundtrip.md` |
| 2. 分集规划 | `references/golden-3s-hook-library.md` · `references/cliffhanger-master-formulas.md` · `references/continuity-ledger.md` |
| 3. 单集撰写 | `references/golden-3s-hook-library.md` · `references/cliffhanger-master-formulas.md` · `references/dialogue-doctor-anti-ai.md` · `references/craft-quality-layer.md` · `references/inner-monologue-vo.md` · `references/conflict-modes.md`（第1~3集加挂 `references/first-three-eps-beat-card.md`） |
| 4. 剧本医生 / 8. 剧本优化 | `references/dialogue-doctor-anti-ai.md` · `references/script-doctor-protocol.md` · `references/protective-counterexamples.md` · `references/craft-quality-layer.md` · `scripts/extract_world_rules.py` |
| 5. 极速直出 | 静默加载模式 1 与模式 3 最小规则子集 + `references/first-three-eps-beat-card.md` |
| 6. 合规自检 | `references/screenplay-compliance-rules.md` |
| 7. 批量连写 / 9. 交付终检 | `references/continuity-ledger.md` · `templates/handover-logic-checklist.md` · `scripts/rolling_checkpoint.py` · `scripts/final_qc.py` |

---

## 单集写作硬门禁（写前 / 写后，v5.1 补回）

**写前门禁（缺任一项不许开写）**：必须已具备【情绪契约】【本单元执念】【反派赌注】【主角主动目标】【本单元回合表】五项，缺项先补上游。

**必须先标【冲突形态】**：机检按此分型放宽阈值，**不标即按对话型死卡**——

| 形态 | 标记 | 机检放宽效果（代码实测） |
|---|---|---|
| ①对话型（默认） | 省略，或 `【冲突形态】：对话型` | 全标准卡口（E1 band 5.0~7.6 字/秒、E21 下限 25%、E9 全量、E16 动作拍×1.5s） |
| ②行动坚持型 | `【冲突形态】：行动型` | E1 band 3.5~5.5 字/秒、E9 对白行减半、E21 下限 10%、E16 动作拍×4.0s、E4 可用反常动作词、**E23 必须有【质疑者配角】** |
| 混合 | `【冲突形态】：混合` | E1 band 4.2~6.5、E9 略降、E21 下限 15%、E16 动作拍×2.5s |
| ③身份错位 / ④关系情感 / ⑤规则谜题 | 照写形态名 | 按对话型卡口 |

> ②型不标＝行动型剧本会被 E1/E9/E21/E16 冤判成体量不足、攻防不足、时长虚标；五型定义与写法见 `references/conflict-modes.md`。

**写后门禁（集内结算）**：每集必须有可见的**反将**，且**反派为本次施压付出可见代价**（当众失面 / 盘算落空 / 被架住进退两难）；伏笔或异能信号必须给「信号 → 当场可验证 → 产生作用」闭环。

**排版门禁（下游脚本依赖）**：每场必写 `[场景]` 与 `[人物]` 行——`rolling_checkpoint.py` 的角色名录、`export_script_json.py` 的 `characters` 都从 `[人物]` 行取，不写即空；头部字段照 `【本集时长】100秒` / `【本集断章卡点】…` 原样写，冒号可有可无。

---

## 唯一执行顺序 & 机检命令速查

```text
任务理解 -> 流派与档位判定 -> 礼法/常识排雷+六栏世界规则卡(优化场景由脚本自动反填) -> 人物圣经 -> 全剧结构(L1~L4圈层+回合表) -> 分集规划(前三集锁死A/B进场轨) -> 单集撰写(15秒四挡; 强视觉△; 大白话直给; 视听可拍性E37~E40) -> 医生精修 -> 滚动状态包(连写每5~10集) -> 三态终检(final_qc + validate_series) + 合规
```

```bash
# 1. 一键运行全部 6 个脚本引擎自检 + 双标杆样章校验（Windows 用 python；macOS / Linux 用 python3）
python scripts/run_all_checks.py

# 2. 单集剧本机检（含 E1~E27 + E37~E40 视听可拍性 + N12~N14 保护性反例）
python scripts/validate_episode.py <单集剧本.md> [--format auto|standard|long|manju] [--prev 前集.md]

# 3. 全剧台账机检（S1~S8）
python scripts/validate_series.py <台账.md> [--episodes 30|40|50|60|80|100]

# 4. 剧本优化起手式：自动从已有原稿反填世界规则卡（不问用户）
python scripts/extract_world_rules.py <已有剧本.md或目录> -o world-rules.json

# 5. 批量连写每 5~10 集生成抗上下文压缩滚动状态包
python scripts/rolling_checkpoint.py <剧本目录> [--ledger 台账.md] --out rolling-state.md

# 6. 交付前终检（三态强制：PASS=0 / BLOCKED=1 / INCOMPLETE=3；提供 --ledger 时自动联动 S1~S8）
python scripts/final_qc.py <剧本目录> [--ledger 台账.md] [--partial] --out 终检报告.md

# 7. 结构化 JSON 导出（纯格式解析，对接下游分镜/平台）
python scripts/export_script_json.py <单集剧本.md> -o ep01.json
```

---

## 绝对红线（10 条）

1. **严禁开篇铺垫与第 1 集纯挨打不反制**：前 3 秒必须见冲突；**前 5 句台词内必须挑明对方利益算盘与具体数字/死线**；**第 1 集半场（35~45秒）主角必须打出第一次实质反制动作**。
2. **严禁台词讲设定、打哑谜与违背礼法常识**：物证与大白话结论同轮直给；设定词当句翻译（E25）；立项过礼法排雷表（禁贬妻为妾/私拆御匾/撕自己手里原契）。
3. **单集正文体量【参考】且严禁机械八股锁死**：严禁全剧死板锁死“每集固定30句/死板双场景/刷屏【特写】【慢镜头】”（E27）。
4. **严禁站桩干聊、无效微动作与否定式伪动作**：每 2~4 句对白必插强视觉 `△`（E24），禁 `眼神微动/推半寸`（E26），禁 `非但没跪/看都没看一眼`（E37），道具交接必写来源（E38），禁幽灵反问（E39）与同空间假切场（E40）。
5. **严禁全员播音腔与括号常态套话**：快慢变速句群；括号禁写“眼神微冷/淡淡开口”（E18c）。
6. **情绪流单矛盾 <=30 集闭环且沿 L1~L4 圈层升维**（长档折半 10~15 集），严防第 3 集把全剧核心账目演完。
7. **严禁同集原地踏步与回合复读**；**优化模式严禁改剧名、主角名与原外壳**。
8. **合规一票否决类不碰**：暴力写意替代直观血腥；恶行不过 3 集受惩，严禁私刑致命救济。
9. **长档必设中段小钩（≈90秒）且守住时长双闸门**（E16/E17，>=150秒）。
10. **独白/旁白配额制**：不代替对抗、不交代设定、前 3 秒与断章处禁用（E12~E15）。

---

## 完整文件索引

| 文件 | 职责 |
|---|---|
| `references/emotion-flow-roundtrip.md` | ★情绪流单元链往返法引擎（流派判定/情绪契约/六档证据×反驳/三缝合一 + **L1~L4 四级被看见圈层阶梯**） |
| `references/hongguo-beat-sheet.md` | ★全剧结构：标准 60/80/100 + 长档 30/40/50 四幕与付费墙换算、单集 15 秒换挡四拍推进表 |
| `references/continuity-ledger.md` | ★跨集连续性台账（伏笔/人物/道具/规则四账 + A~I 九类反转轮换矩阵 + 冷热分层） |
| `references/character-bible.md` | 人物圣经四件套（动机/秘密/弧光/语言指纹）+ 全员名册 |
| `references/webnovel-adaptation.md` | 网文 -> 分集改编流水线（抽取/砍并/章改集映射） |
| `references/mechanism-imitation.md` | ★剥壳留核三层抽离仿写法 + **v5.1 第一性原理叙事降维外化法则** |
| `references/genre-map.md` | 男频/女频/中性全赛道题材图（40 赛道：男频12/女频14/中性14） |
| `references/golden-3s-hook-library.md` | 黄金前 3 秒六母型 · 20+ 变体 + 开篇禁令 |
| `references/first-three-eps-beat-card.md` | ★前三集节拍卡（**极速进场五步拍点 + 女频 A/B 双轨进场制 + 防 3 集演完大结局剥皮法则**） |
| `references/cliffhanger-master-formulas.md` | 五大断章公式 + 生活化短句金句子类 + 漫剧宝物认主断章 |
| `references/dialogue-doctor-anti-ai.md` | ★台词七维诊断与直给变速手册 + **§三 E18c 括号去常态套话替换表** |
| `references/inner-monologue-vo.md` | ★独白与旁白受控规程（三通道分工/配额/位置纪律/E12~E15 口径） |
| `references/craft-quality-layer.md` | ★戏剧工艺层（强画面三大锚点 + 礼法常识排雷 + 六栏世界规则卡 + **v5.1 视听可拍性 E37~E40 & 路径消歧**） |
| `references/conflict-modes.md` | ★冲突形态五型（对话型/行动坚持型/身份错位型/关系情感型/规则谜题型） |
| `references/script-doctor-protocol.md` | 评审官与修复器双角色 + 问题卡十一字段 + P0/P1/P2 定级 |
| `references/protective-counterexamples.md` | 保护性反例集（NOTE 级三级语义，防过度修正） |
| `references/skill-eval-protocol.md` | 升级评测规程（固定用例/盲评/证据分层） |
| `references/screenplay-compliance-rules.md` | 广电 16 号令备案分类 + 11 条内容红线 + 敏感词替换库 |
| `templates/ledger.md` | 台账空表模板（含档位行、A~I 反转矩阵与热/冷分区） |
| `templates/episode-format.md` | 单集剧本标准排版（标准/长档双模板 + 神态短语规格） |
| `templates/handover-logic-checklist.md` | ★**v5.1 新增**：30 秒一页式逻辑交接自检表（L1~L5） |
| `examples/ep01-longwang-demo.md` | 标准档单集标杆示例（0 FAIL） |
| `examples/long-format-3min-demo.md` | 长档单集标杆示例（0 FAIL） |
| `scripts/validate_episode.py` | ★**v5.1 升级**：单集分档机检（`E1~E27` + `E37~E40` 视听可拍性 + `N12~N14`） |
| `scripts/validate_series.py` | 全剧台账机检（`S1~S8`：伏笔超期/死人开口/断章缺失/付费墙落位/A~I 反转轮换） |
| `scripts/rolling_checkpoint.py` | ★**v5.1 新增**：抗上下文压缩滚动递进状态包生成器 |
| `scripts/final_qc.py` | ★**v5.1 新增**：三态交付前终检闸门（联动台账 S1~S8 + 跨集 C1，`PASS=0 / BLOCKED=1 / INCOMPLETE=3`） |
| `scripts/extract_world_rules.py` | ★**v5.1 新增**：优化场景世界规则卡自动反填器 |
| `scripts/export_script_json.py` | ★**v5.1 新增**：结构化 JSON 导出器（对接下游分镜/平台） |
| `scripts/run_all_checks.py` | ★**v5.1 新增**：统一自检入口（覆盖全套 6 个引擎 + 双标杆样章） |
