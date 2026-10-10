# 工作流路由与生命周期

本文件是 Hans PPT 的路由权威。先选择一条路线和一个运行模式，再读取对应路线；不要把不同路线的规则混在一起。

## 1. 确定性路由

| 请求形态 | 路线 | 读取 |
|---|---|---|
| 从主题、文章、大纲、PDF/DOCX/PPTX 素材创建新演示；或重写旧 PPT 的结构与内容 | `generate` | `generate.md` |
| 旧 PPT 的页面可见文字、页数、页序保持 1:1，只重新设计视觉 | `beautify` | `beautify.md` |
| 要在原 PPT 上局部替换内容，并要求未改页面、母版、动画保持原生不动 | 当前不支持原生补丁路线 | 说明边界；若用户接受重新生成，再进入 `generate` |

已有 PPT 既要求“内容别动”又要求拆页、并页或重排时，不属于 `beautify`；页面结构已经变化，应进入 `generate`，把旧稿当素材。

## 2. 运行模式

| 模式 | 触发 | 行为 |
|---|---|---|
| `default` | 默认 | 两阶段确认；生成可恢复的 `deck.json`、`style.json`、`plan.json` 和 `design_spec.md` |
| `quick` | 用户明确说快速、直接做、不确认或跳过策略 | 不停下来确认，代理决定未指定项；仍完成素材处理、规划、图片、原生 PPT 和 QA，不降低交付能力 |

页数少、用户暂时没回复或代理认为事情简单，都不能自动进入 Quick。

## 3. 项目初始化

先完成环境检查，再初始化工作目录：

```bash
python3 $S/setup_check.py --quick --install
python3 $S/workflow_state.py init $W --route generate --profile default
```

美化路线把 `generate` 换成 `beautify`；显式 Quick 把 `default` 换成 `quick`。一个工作目录只属于一次运行，不覆盖既有 `workflow.json`。

## 4. Default 的两个确认门

### Stage 1：沟通契约

分析素材后，给出一份推荐，不做选项堆砌。一次确认以下内容：

- 受众、交付场景和阅读距离；
- 演示目标、观众结果和核心信息；
- 页数或时长范围；
- 视觉来源：自由设计、参考图，或继承旧稿身份；
- 内容自由度和事实边界。

用户明确确认后记录：

```bash
python3 $S/workflow_state.py confirm $W stage1
```

Stage 1 前不生成 `plan.json`，不出图，不生产 PPT。

### Stage 2：完整方案

Stage 1 后完成 `deck.json`、`style.json`、`plan.json`，由 `plan_deck.py` 生成 `design_spec.md`。一次展示：

- 故事线与完整页面 roster；
- 视觉方向、色彩、字体和视觉锚点；
- 每页任务、节奏、版式、媒体槽位；
- 图片来源、演讲备注和时长计划；
- 容量或事实风险。

用户确认后记录：

```bash
python3 $S/workflow_state.py confirm $W stage2
```

Stage 2 前不得运行 `pipeline.py`。需要修改时，先修拥有问题的 `deck.json`、`style.json` 或 `plan.json`，再重新生成并展示方案。
确认时会记录四个生产输入的指纹；之后任何文件发生变化，生产门会重新关闭，必须展示更新后的完整方案并再次确认 Stage 2。

## 5. Quick 的边界

Quick 初始化后两道门标记为 `skipped`。代理仍需在当前上下文中一次性解决 Stage 1 和 Stage 2 的全部决策，并在生产前完成：

- 精确页面 roster 与每页核心信息；
- 受众、目标、故事线、节奏与内容密度；
- 色彩、字体、版式和视觉锚点；
- 图片、图标、图表、备注与时长策略；
- 事实来源和需要披露的不确定项。

Quick 不是可恢复规划模式；如果关键上下文丢失，重新开始一次 Quick，不凭残缺记忆续做。

## 6. Plan → Do·Check·Act

| 阶段 | 结束条件 |
|---|---|
| Plan | 路线与模式确定；素材就绪；Default 两个确认门关闭或 Quick 决策已在上下文闭合；四个生产输入存在 |
| Do | 图片素材生成，原生 PPT 组装，预览生成 |
| Check | 内容完整性、布局、对比度、节奏、备注和 QA 通过 |
| Act | 在拥有问题的最浅层修复：内容回 `deck.json`，视觉系统回 `style.json`，单页版式/媒体回 `plan.json`；然后重跑受影响步骤 |

流水线失败后不回到最初重问全部需求，也不能带着 QA ERROR 交付。
