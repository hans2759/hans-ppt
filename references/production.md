# 生产、质量门与交付

只在路线的 Plan 阶段完成后读取。生产输入是 `deck.json`、`style.json`、`plan.json`、`design_spec.md`；Default 必须关闭两个确认门。

## 1. 进入生产

```bash
python3 $S/workflow_state.py check $W --for produce
python3 $S/pipeline.py $W
```

`pipeline.py` 严格依次运行素材生成、PPT 组装、预览、QA、对比图和五维评审。旧工作目录只有在迁移时才可显式使用 `--legacy-workspace`；新任务不得绕过工作流门禁。
Default 的 Stage 2 会锁定四个生产输入的指纹；确认后若内容、风格、规划或设计规格变化，生产门自动拒绝旧确认。

## 2. 质量门

| 结果 | 行为 |
|---|---|
| QA ERROR | 流水线返回失败；不得交付 |
| QA WARN | 结合实际预览判断；会影响阅读或事实表达的必须修 |
| 高保真渲染失败、近似预览成功 | 可以继续，但交付时说明预览层级 |
| 两种预览都失败 | PPT 可组装，但视觉检查不完整；不得宣称已完成视觉验证 |

典型归属：

- 内容、事实、故事线、备注：修 `deck.json`；
- 色彩、字体、圆角、装饰语言：修 `style.json`；
- 单页版式、图标、图片提示词与槽位：修 `plan.json`；
- 生成失败的图片：修对应 prompt/配置，或明确改用程序化素材。

一次集中修复后重跑流水线；不要针对同一页边检查边零碎重跑。`pipeline.py` 成功后再检查：

```bash
python3 $S/workflow_state.py check $W --for deliver
```

## 3. 视觉复核

查看 `out/sheet.png` 和逐页 PNG，结合 `out/review.md` 检查统一、层级、细节、传达、节奏。脚本通过不等于页面已经好看；视觉判断以实际预览为准。

## 4. 交付

- `out/beautified.pptx`：可编辑原生 PowerPoint；
- `out/sheet.png`：整套预览；
- 美化路线附 `out/compare.png`（源稿预览存在时）；
- `out/review.md`：检查证据与视觉评审。

交付说明只报告实际发生的事实：路线/模式、视觉方向、字体、图片来源、QA 结果、近似预览或缺失依赖、仍需用户核实的事实。不要把程序化插画描述成 AI 生成。
