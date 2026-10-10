# 美化路线

适用于“页面可见文字、页数、页序保持 1:1，只重新设计视觉”的旧 PPT。路线与运行模式先由 `workflow.md` 确定。

## 内容契约

- 页面可见文字逐字保留；局部加粗用 `**片段**` 表示。
- 页数与页序不变，不拆页、不并页、不补页。
- 图表数据、表格单元格、公式和截图中的关键信息不得改写。
- 旧备注不是保真对象：默认只作参考，必须重写成结构化新备注；未重写的字符串不会进入成品。
- 只有用户明确要求旧备注逐字保留时，才设置 `meta.preserve_notes: true`。
- 用户若要重写内容、改变页面结构或重新组织故事，退出本路线并进入 `generate`。

## Step 1：解析旧稿

```bash
python3 $S/extract_deck.py 原稿.pptx $W
```

检查 `source_png/sheet.png`、`deck.draft.json`、`source_text.json` 和提取的媒体。LibreOffice 不可用时允许继续，但必须说明旧稿视觉判断来自近似预览或结构数据。

## Step 2：Stage 1 或 Quick 决策

Default 推荐并确认：受众/用途、视觉身份来源、制作力度、允许忽略的装饰、备注策略和验证严格度。继承旧稿身份时，以实际观察到的色彩、字体和强调层级为依据；参考图只提取设计语言，不直接贴成页面。

确认后运行：

```bash
python3 $S/workflow_state.py confirm $W stage1
```

Quick 直接作出同样决策，不停下来确认。

## Step 3：建立生产输入

1. 从 `deck.draft.json` 整理 `deck.json`，按 `deck_schema.md` 逐页核对可见内容。
2. 参考图走 `extract_style.py` + `style_card.py`；没有参考图时，基于旧稿身份或预设写 `style.json`。
3. 旧备注重写为 `{talk, transition, minutes}`；不需要备注则删除，不把旧字符串换壳带入。
4. 运行规划：

```bash
python3 $S/plan_deck.py $W --level full
```

页面小标签写入 `kicker`，条目编号写入 `num`；公式转为可见可编辑文字公式；SVG 使用提取的 PNG 兼容副本；logo 等非文字品牌小图可放入 `stamps`；软件截图使用 `screenshot` / `screenshots` 页型。

## Step 4：Stage 2

Default 展示 `design_spec.md`：完整页面 roster、视觉方向、逐页版式/节奏、图片处理、备注策略和风险。确认后运行：

```bash
python3 $S/workflow_state.py confirm $W stage2
```

Quick 不停下来，但生产前必须在当前上下文闭合这些决定。

## Step 5：生产

读取 `production.md`，执行共享的组装、QA、修复和交付流程。最终必须逐页核对源文字；任何缺字、改字或跨页错位都是 ERROR。
