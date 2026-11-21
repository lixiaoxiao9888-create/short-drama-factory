# CHANGELOG

## v5.1 终检联动三处补丁（终检跑通回灌 · 2026-11-19）

> **起因**：用 final 包真实跑完整流程（立项→大纲→前三集→机检→终检），终检暴露 3 处误报/漏识别。均为脚本层缺陷，不改创作规则，版本号仍为 5.1。

| # | 层 | 变更项 | 说明 |
|---|---|---|---|
| 1 | **终检层** P1 | `final_qc.py` 联动台账时透传集数 | `check_ledger_via_series` 调 `validate_series.py` 未传 `--episodes`，60 集台账被按默认 80 集口径检查，误报 2 条 S6 付费墙 WARN。现从台账头部解析「总集数: N」透传，实测终检 WARN 归零 |
| 2 | **终检层** P1 | C1 跨集衔接窗口改为正文前 10 行 | 旧实现取「前 12 个非空行」，而标准模板头部元数据恰好占满 12 行，合规稿件正文永远进不了窗口 → C1 对任何规范排版都必然误报。新增 `opening_body_lines()` 跳过【字段】/[场景]/[人物]/标题行后再截取 |
| 3 | **状态包层** P2 | `rolling_checkpoint.py` 金额识别兼容中文数字 | 正则由仅阿拉伯数字改为中文+阿拉伯数字（与 `final_qc.py` 口径统一）；实测「八十万两」不再显示「暂无」 |

**回归**：两份 self-test PASSED；三集样章单机检全 PASSED；真实 60 集台账 + 三集终检 PASS 且 0 WARN；`run_all_checks.py` 全绿。

## v5.1 打包修复与 v4.9.1 修复回植（full build · 2026-11-19）

> **起因**：v5.1 增量包只带出 11 个文件，references 仅剩 1 个，其余 28 个依赖文件未随包；且该包从 v4.9 分叉，v4.9.1 的 7 项修复全部回退。本次为**打包完整性 + 代码修复**，不新增创作规则，版本号仍为 5.1，以文件数量与本节记录区分。

| # | 层 | 变更项 | 说明 |
|---|---|---|---|
| 1 | **打包完整性** P0 | 补齐 28 个依赖文件 | references 17 个（含 genre-map / golden-3s-hook-library / first-three-eps-beat-card / dialogue-doctor-anti-ai / continuity-ledger / webnovel-adaptation 等）、templates 2 个（episode-format / ledger）、examples 2 个、assets 4 个、LICENSE、.sosoclaw-market.json、validate_series.py。README banner 与脚本内 4 处指引不再指向空文件 |
| 2 | **机检层** P0 | E26 消除长度盲区（回植 v4.9.1） | 恢复 `STRONG_ACT_MARKERS`：弱微动作被凑长氛围描写包裹（净字数>14）仍告警；行内含强动作标记的组合 △ 不误报 |
| 3 | **机检层** P0 | E16 恢复全档生效 + 「秒」字可省（回植 v4.9.1） | 正则改 `(?:\s*秒)?`；E16 由仅长档扩为全档（凡标注【本集时长】即校验），E17 仍仅长档 |
| 4 | **机检层** P1 | E1 体量带恢复按无冒号时长推导 | `net_band` 正则改 `[：:]?`：`【本集时长】95秒`（模板实际写法）也能按字数/秒换算参考带，不再退回档位默认带 |
| 5 | **健壮性** P1 | 读写改 `utf-8-sig`（回植 v4.9.1） | 6 个脚本 8 处读取；`first_content_lines` 剥离 BOM，防 WINDOWS 记事本/WPS 存盘 BOM 挤占 E4 前 3 秒检测窗口 |
| 6 | **导出层** P1 | `export_script_json.py` 支持无冒号头部字段 | 原正则要求【键】：值，模板实为【键】值，导致 `meta` 与 `cliffhanger` 恒为空；现兼容两种写法并排除【场景】【人物】与镜头标签 |
| 7 | **文档层** P1 | 补回「单集写作硬门禁」章 | 写前门禁五项、**【冲突形态】五型标记及机检放宽效果表**（代码依赖该标记，不标则行动型剧本被 E1/E9/E21/E16 冤判）、写后集内结算、`[人物]` 行等下游解析依赖 |
| 8 | **挂载矩阵** P1 | 补 `webnovel-adaptation.md` 与连写核心规则（回植 v4.9.1） | 模式 0/5 输入为网文时加挂；模式 7 连写补挂 golden-3s-hook / dialogue-doctor / craft-quality-layer / conflict-modes |
| 9 | **元数据** P2 | frontmatter `name` 去前缀、市场卡升版 | `user:short-drama-factory` → `short-drama-factory`；.sosoclaw-market.json version → 5.1 并补 v5.1 能力摘要 |

**回归**：`run_all_checks.py` 5 项自检 PASSED；官方双标杆样章 `ep01-longwang-demo.md`（标准档 754 字）与 `long-format-3min-demo.md`（长档 1210 字）均 **PASSED（0 FAIL / 0 WARN）**；E37~E40 四门禁、E16 全档、E26 盲区、BOM、JSON 导出逐项复测通过。

## v5.1 跨集防崩闭环 + 视听可拍性四门禁 + 优化路径消歧 + 生态导出升级（2026-11-19）

| # | 变更层 | 变更项 | 说明 |
|---|---|---|---|
| 1 | **视听可拍性层** P0 | `validate_episode.py` 新增 **E37~E40** | `E37` 拦截否定式伪动作（FAIL，如“非但没跪/看都没看一眼”）；`E38` 道具交接缺来源（WARN）；`E39` 台词未提先知幽灵反问（WARN）；`E40` 同空间假切场（WARN） |
| 2 | **长剧防崩与交付层** P0 | 新增 `rolling_checkpoint.py` + `final_qc.py` + 一页式交接表 | 每 5~10 集提取抗上下文压缩滚动状态包；交付前跑三态终检（`PASS=0 / BLOCKED=1 / INCOMPLETE=3`）核对跨集断章接续 `C1` 与完整性；新增 `templates/handover-logic-checklist.md`（L1~L5） |
| 3 | **优化与排雷层** P1 | 新增模式 8 `/剧本优化` + `extract_world_rules.py` + 降维外化 | 写死「优化 ≠ 改编」（保留原稿剧名/主角名/外壳），并由脚本从原稿自动反填六栏世界规则卡；`craft-quality-layer.md` 新增第一性原理降维外化法则 |
| 4 | **生态与工程层** P1 | 新增 `export_script_json.py` + `run_all_checks.py` | 一键将标准剧本解析为结构化 JSON 对接下游分镜/平台；统一入口一条命令跑完全部引擎 `--self-test` |

## v5.0 粉丝实战剧本对标与女频扒剧融合升级：极速进场双轨制 + 礼法常识排雷 + 四级圈层阶梯 + 反机械模板（2026-10-25）

> **起因**：粉丝反馈高快节奏女频参考剧本（《和离当天，侯府库房被我搬空了》），指出我方原有前三集进场节奏略偏慢。经综合评估，提炼吸收四大高价值工程机制，同时规避“3集把核心矛盾全演完”及“全剧机械锁死30句/刷屏【慢镜头】”的八股弊端，升级至 **v5.0**。

| # | 变更层 | 变更项 | 说明 |
|---|---|---|---|
| 1 | **进场层** P0 | 第 1 集「极速进场五步拍点表」+ 女频「A/B 双轨进场制」 | `references/first-three-eps-beat-card.md` 重构升级：0~3s 强视觉 ➔ 前 5 句挑明算盘 ➔ 半场必亮首张反制牌；女频分流 A/B 双轨 |
| 2 | **立项层** P0 | 立项「常识与礼法/现实逻辑排雷清单 + 六栏世界规则卡」 | `references/craft-quality-layer.md` §六·补二：排除降智老梗，锁定金手指代价锁 |
| 3 | **结构层** P1 | 中后段防注水「L1~L4 四级被看见/掉马圈层阶梯」 | `references/emotion-flow-roundtrip.md` §二·六：单元链绑定 L1~L4 空间与裁判圈层 |
| 4 | **台词与机检层** P1 | 新增 **E18c 括号去常态套话** 与 **E27 反机械镜头标签堆砌** | `references/dialogue-doctor-anti-ai.md` §三 & `scripts/validate_episode.py` |

## v4.9 实战观众反馈重铸升级：强画面支撑 + 15秒换挡 + 大白话直给 + 剥壳留核仿写（2026-10-22）

- 补全「台词七维」（物证结论同轮直给、黑话当句翻译、快慢变速）、强画面三大视觉锚点、单集 15 秒四拍推进表、剥壳留核仿写、机检 `E24~E26`。

## v4.3 ~ v3.0 历史版本

- **v4.3（2026-09-28）**：参考语速 4.5 字/s；E16 容差 ±20%；冲突形态五型（`references/conflict-modes.md`）。
- **v4.2 ~ v3.0**：动态按需挂载矩阵、A~I 反转轮换矩阵、冷热台账分层、40 赛道全图、独白旁白受控规程（E12~E15）、广电 16 号令合规红线。
