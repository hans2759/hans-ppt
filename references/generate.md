# 从零生成 PPT

输入可以是一篇文章或口播稿、一个题目、一份大纲，也可以是 .docx / .pdf / .pptx 素材。
本路线创建一份新的原生 PPT。素材里的文字可以改写、精简、重组；已有 PPT 需要拆页、并页或重构时，也把它作为素材进入本路线。

开始前已由 `workflow.md` 选定本路线和 Default/Quick；再读 `presentation_contract.md`，先确定沟通契约和每页观众变化。

## 流程总览

| 步 | 做什么 | 产物 / 工具 | Default 门 |
|---|---|---|---|
| 1 | 分析素材和事实缺口 | `analysis.md` | 否 |
| 2 | 推荐沟通契约与视觉来源 | Stage 1 摘要 | 是 |
| 3 | 写内容、风格和逐页规划 | `deck.json`、`style.json`、`plan.json`、`design_spec.md` | 否 |
| 4 | 确认完整演示解决方案 | `design_spec.md` | 是 |
| 5 | 生产、QA、修复、交付 | `production.md` | 否 |

Quick 只有显式触发：不展示 Stage 1/2，也不等待，但必须在当前上下文完成同等决策并生成四个生产输入。

## Step 1：素材分析

```bash
python3 $S/analyze_source.py $W --file 文章.md --scenario oral
python3 $S/analyze_source.py $W --topic "题目" --minutes 3
```

得到 `analysis.md`：字数、原文标题结构、数字、风格线索和建议页数。只有题目或素材存在规划所需的事实缺口时才搜索查证；封闭素材任务不扩展事实范围。

## Step 2：Stage 1 沟通契约

Default 根据素材给出一个明确推荐，一次确认：

- 场景、受众和阅读距离；
- 演示目标、观众结果和核心信息；
- 页数/时长范围与内容自由度；
- 自由设计或参考图；
- 事实边界与备注策略。

用户确认后运行 `python3 $S/workflow_state.py confirm $W stage1`。Quick 直接决定。场景决定密度：口播和演讲用 low，阅读和汇报用 high。

## Step 3：完整方案

先写 `deck.json`，字段格式见 `deck_schema.md`：

```json
{"meta": {"title": "…", "scenario": "oral", "audience": "小白", "density": "low",
          "objective": "让观众理解并愿意试用", "audience_outcome": "能说清价值并知道第一步怎么做",
          "storyline": "一句话讲清这份 PPT 的来龙去脉", "duration_minutes": 8,
          "notes": true, "auto_page": true,
          "series": "页眉小字，可选", "anchor": {"description": "…", "glyph": "M"}},
 "slides": [{"n": 2, "id": "core-definition", "type": "big_number", "rhythm": "breathing",
             "purpose": "让观众一句话记住它是什么", "audience_move": "从陌生变成能复述核心定义",
             "title": "…", "…": "…", "notes": {"talk": ["口播要点"], "transition": "…", "minutes": 0.7},
             "source": "数据出处，可选"}]}
```

### 先搭故事线

按场景挑一条主线，再往里填页。

- **讲解型**（口播科普默认）：开场钩子 → 它是什么 → 为什么值得关注（证据、数据）→ 怎么用 → 坑和边界 → 行动号召
- **方案型**（汇报）：现状和问题 → 目标 → 方案 → 计划和资源 → 风险 → 需要拍板的事
- **清单型**（技巧合集）：为什么需要 → 第一条到第 N 条 → 怎么组合 → 行动号召

把主线写进 `meta.storyline`，每页写 `purpose`（这一页在故事里负责什么）和 `audience_move`（观众发生什么变化）。稳定页 ID、节奏角色和图片槽位规则见 `presentation_contract.md`。

### 标题写结论

每页标题是一句能单独成立的结论，不是话题名。

| 话题名（不要） | 结论式（要） |
|---|---|
| 数据表现 | 它火得数据很硬 |
| 使用方法 | 上手先改权限，再连账号 |
| 注意事项 | 它会犯错，别把判断交出去 |

写完把所有标题按顺序连起来读，读下来是一个完整的故事才算过关；读不通就调整顺序或补页，别急着做设计。长度控制在 4 到 22 个字。

### 一页一件事

- 一页只讲一个观点。装不下就拆页，不缩字号硬塞。
- low 密度：屏幕上约 100 字以内、要点最多 4 条；high 密度：约 200 字以内、要点最多 6 条。
- 屏幕放关键词和短句，完整的话放 `notes`。
- 结尾页放结论或行动号召，不放"谢谢观看"。
- 超过 15 页时加章节分隔页（type: section）。

### 口播备注

`notes` 是演讲者在台上需要的内容，不是页面文案的复制。默认写结构化对象：`talk` 放 3–5 条提词卡，`transition` 解释下一页为什么紧接着出现，`minutes` 写计划时长；只有用户明确要求逐字稿时才写长段落。一页口播约 40 到 260 字（约 15 到 60 秒）。
从文章改写时，备注尽量保留作者原句和语气，屏幕文字再从备注里提炼。
环境里如果有用户自己的写作风格 skill，备注按那个风格写。

有目标总时长时，每页都写 `minutes`，总计划不超过 `meta.duration_minutes` 的 90%。缺少现场信息时不要猜 `cue`、互动或备用方案。

### 内容形状决定页型

| 内容长什么样 | type | 默认版式 |
|---|---|---|
| 一个核心数字或一句话定义 | big_number | statement_number |
| 两到四个数据 | stats | stats_row |
| 有先后顺序的两到五步 | process | steps_flow |
| 做法建议，一条重点一条补充 | steps | side_cards |
| 两种东西对比、前后对比 | compare | compare_split |
| 循环往复的环节 | cycle | cycle |
| 有层级、有基础和上层 | layers | pyramid |
| 几个并列概念的解释 | definitions | rows_side |
| 三到六个短要点 | list / grid | grid_cards |
| 例句、提示词、原话 | quotes | quote_cards |
| 风险和坑，加一句总结 | warnings | cards_quote |
| 一句主张加解释 | statement | statement_hero |
| 示意图加讲解 | diagram_text | media_text |
| 一张截图讲清几个操作点 | screenshot | shot_notes |
| 几张截图走完一个流程，或电脑和手机对照 | screenshots | shot_stack |
| 按时间排的里程碑、发展历程 | timeline | timeline |
| 一层层转化、筛选、流失 | funnel | funnel |
| 一个核心辐射出几个部分 | hub | hub |
| 按两个维度给事情分类、排优先级 | matrix | matrix |
| 多个方案在多个维度上比较 | table | table |
| 数字之间比大小、看趋势、看占比 | chart | chart |
| 优劣势、外部环境、竞争格局、商业模式 | framework | framework |
| 章节开头 | section | section |
| 分了章节的稿子，封面后面 | toc | toc |
| 抛出一个问题，下一页再回答 | question | question |
| 一句值得单独成页的原话 | big_quote | big_quote |

同一种页型别连续出现三次，换一种讲法。各页型的字段见 `deck_schema.md`，每个版式装得下多少用 `python3 $S/layout_info.py <版式名>` 查，里面还带一段能直接改的示例。

节奏用 `anchor / dense / breathing` 标记。连续四页 `dense` 通常会像流水账，优先插入真正承担转折、结论或结构作用的呼吸页，不为配额加空页。

数据页的取舍：只想让人记住一两个数字，用 big_number 或 stats；要让人看出谁大谁小、往哪走、占多少，才上 chart。chart 的标题就是图里最重要的那个结论，insights 补一两条标题没说完的发现。

分析框架别为了显得专业硬套。SWOT 四格里有一格只能凑出空话，就说明这页该换成 compare 或 warnings。

标题里最关键的一个词可以用 `**…**` 包起来，它会变成强调色；一个标题最多标一处，标多了就没有重点。

### 从三种输入出发的要点

- **文章或口播稿**：先按段落切出故事线，一段往往就是一页；数字优先做成数据页；原文金句可以直接当标题或 takeaway。
- **大纲**：每个二级标题至少一页；带顺序的列表用 process，"坑""误区"类用 warnings，"写在最后"做结尾页。大纲通常没有展开的话，备注需要补写，补写的事实要查证。
- **题目**：见 Step 1，先查证再写。

### 检查内容方案

```bash
python3 $S/outline_check.py $W
```

它会打印幽灵稿（只读标题），检查话题式标题、密度、要点条数、备注长度、页数、页型重复和结尾页，还会按版式容量报出装不下的页，并给出能装下的替代版式。
修到没有 ERROR、所有 WARN 都判断过为止。`outline.md` 是 Stage 2 的页面 roster 输入，不再单独增加一次确认门。

### 定视觉方向

- 用户给了参考图：运行 `extract_style.py`，看图写 `style.json`，再用 `style_card.py` 检查。
- 没有参考图：
  ```bash
  python3 $S/style_previews.py $W --auto          # 或 --presets a,b,c 自己挑三套
  python3 $S/style_previews.py $W --apply <id>    # 用户选定后
  ```
  Default 可把样张作为 Stage 2 的视觉证据，但不单独制造第三个确认门；Quick 直接选择最适合内容的一套。预设清单见 `styles/index.json`，每套硬规则在对应 JSON 中。

### 版式规划与 Stage 2

```bash
python3 $S/plan_deck.py $W --level full            # 有生图模型时可加 --sheets，一张大图切多张小插画
```

它写出 `plan.json` 和 `design_spec.md`。审一遍：页面任务能否推动观众变化、版式是否贴合内容、节奏是否有呼吸、视觉焦点是否清楚、图片槽位与提示词是否具体（见 `image_prompts.md`）。
可以在 plan.json 每页补 `relation`（和前后页的关系，比如"承接上页的数据，转入怎么做"），帮助统一节奏。
Default 把完整 `design_spec.md` 作为一次 Stage 2 方案展示；用户确认后运行：

```bash
python3 $S/workflow_state.py confirm $W stage2
```

Quick 不停下来，但必须先完成同样的内容/视觉/媒体/备注决定。

## Step 4：生产与交付

读取 `production.md`。生成路线的 QA 以 `deck.json` 为准，检查每段可见文字都进入页面。AI 图片最终提示词写入 `prompts/`；局部改图时修对应 prompt，再运行 `make_assets.py $W --only hero_05 --force` 和后续流水线。
