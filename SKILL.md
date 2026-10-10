---
name: hans-ppt
description: 生成、重构或视觉重制可编辑的原生 .pptx。用于把主题、文章、大纲、PDF/DOCX/PPTX 等素材做成有故事线、原生图形和演讲备注的演示稿，或在页面文字、页数、页序保持 1:1 时重新设计旧 PPT。用户说“做个 PPT”“把材料做成演示稿”“快速生成”“美化/重做 PPT”“make slides”“beautify my deck”，或提供演示素材时使用。不适用于要求在原 PPT 上做字节级原生补丁、且未修改页面必须完全不动的任务。
---

# Hans PPT

Hans PPT 是一个路由式演示工作流。入口只负责选择路线、运行模式和全局纪律；具体路线负责自己的步骤。

下文 `$S` 是本 Skill 的 `scripts` 绝对路径，`$W` 是本次独立工作目录。每条命令都展开成绝对路径，不依赖先前终端的当前目录。Windows 没有 `python3` 时使用 `python`。

## 强制读取顺序

1. 读取本文件。
2. 运行环境检查：
   ```bash
   python3 $S/setup_check.py --quick --install
   ```
   必需项失败就停止；只缺推荐项可继续并如实说明限制。
3. 读取 `references/workflow.md`，确定唯一的路线和运行模式。
4. 初始化 `workflow.json`。
5. 只读取选中的路线：
   - `generate` → `references/presentation_contract.md`、`references/generate.md`
   - `beautify` → `references/beautify.md`、`references/deck_schema.md`
6. Plan 完成后才读取 `references/production.md` 并进入生产。

不要同时加载两条路线的程序。支持性参考只细化当前路线，不与路线竞争。

## 路由摘要

| 路线 | 请求 | 生产模型 |
|---|---|---|
| Generate | 新建演示；从素材重写；旧 PPT 需要拆页、并页、改文案或重组故事 | 分析素材 → 沟通契约 → `deck/style/plan` → 原生 PPT |
| Beautify | 旧 PPT 的页面可见文字、页数、页序保持 1:1，只重新设计视觉 | 提取旧稿 → 冻结可见内容 → `deck/style/plan` → 原生 PPT |

要求保留原 PPT 原生结构、未改页面、母版或动画并只做局部补丁时，当前 Skill 不具备该路线。说明边界；只有用户接受重新生成时才进入 Generate。

## Default 与 Quick

- 默认是 `default`：Stage 1 确认沟通契约与视觉来源；Stage 2 确认完整页面/视觉/媒体/备注方案。只有用户能关闭确认门。
- 用户明确说快速、直接做、不用确认或跳过策略时才用 `quick`。Quick 不停下来确认，但不能省略事实核对、内容规划、视觉能力、图片准备和 QA。
- 页数少、用户沉默或代理觉得简单，都不能自动切换 Quick。

初始化示例：

```bash
python3 $S/workflow_state.py init $W --route generate --profile default
```

## 全局执行纪律

1. 串行推进 Plan → Do·Check·Act；每个门的前置条件满足后才能进入下一阶段。
2. Default 的确认门是阻塞门。用户未确认就不替用户确认，不提前出图或组装。
3. 修复发生在拥有问题的最浅层：内容回 `deck.json`，视觉系统回 `style.json`，单页构图/媒体回 `plan.json`。
4. 新任务必须使用 `workflow.json`。`--legacy-workspace` 只迁移旧工作目录，不用于绕过新任务门禁。
5. 每个项目的四个生产输入是：
   - `deck.json`：沟通契约、页面 roster、可见内容、来源、节奏、结构化备注；
   - `style.json`：色彩、字体、形状、装饰和插画语言；
   - `plan.json`：逐页版式、图标、图片槽位和资源；
   - `design_spec.md`：Stage 1 契约与 Stage 2 完整方案的人类可读快照。

## 不可破坏的交付规则

1. 页面文字使用可编辑文本框；卡片、分隔线、表格和图表优先使用 PowerPoint 原生对象。只有背景、插画、图标和笔刷可用图片。
2. 参考图只用于提取设计语言，不直接裁切贴进页面。
3. AI 图片不生成页眉、页脚、页码、主标题、logo 或长段文字；文字密集信息回到原生文本/形状/图表。
4. 事实和数字只来自用户素材或已查证来源；查不到就不写。图表数据变化时，标题和洞察同步更新。
5. 每页必须有 `id`、`purpose`、`audience_move` 和节奏角色；没有观众变化也不承担必要结构作用的页要合并、重写或删除。
6. 旧稿字符串备注默认不进入成品。成品以结构化 `talk / transition / minutes` 新备注为主；只有用户明确要求时才开启 `preserve_notes`。
7. `pipeline.py` 返回失败或 QA 仍有 ERROR 时不得交付。脚本通过后仍要查看实际预览。
8. 做用户 PPT 时不修改 Skill 本身；遇到 Skill 问题先绕开完成用户任务，再报告问题。

## 按需参考

| 任务 | 读取 |
|---|---|
| 字段与页型 | `references/deck_schema.md` |
| 版式容量或 free 版式 | `references/layouts.md`，必要时运行 `layout_info.py` |
| 参考图提取 | `references/style_extraction.md` |
| 图片角色、槽位与提示词 | `references/image_prompts.md` |
| 图片模型配置 | `references/imagegen_config.md` |
| 字体 | `references/fonts.md` |
| 图标 | `references/icons.md` |
| 五维视觉评审 | `references/critique.md` |
