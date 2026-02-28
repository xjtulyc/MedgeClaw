---
name: svg-ui-templates
description: >
  Generate professional SVG UI panels for structured information display.
  Use when presenting lists, task checklists, pipeline/dependency status diagrams,
  or rich-text report layouts as SVG images. Covers four templates -
  list-panel, checklist-panel, pipeline-status, richtext-layout.
  Style is professional, business-oriented, academic-grade with Material Design color palette.
---

# SVG UI Templates

Generate professional-grade SVG information panels optimized for horizontal (landscape) display.

## Templates

| Template | File | Use Case |
|----------|------|----------|
| **list-panel** | `assets/list-panel.svg` | 数据表格、参数列表、对比表 |
| **checklist-panel** | `assets/checklist-panel.svg` | 任务清单、进度追踪、TODO |
| **pipeline-status** | `assets/pipeline-status.svg` | 流程依赖图、阶段状态、里程碑 |
| **richtext-layout** | `assets/richtext-layout.svg` | 图文混排、报告摘要、数据简报 |

## Workflow

1. Read the appropriate template SVG from `assets/`
2. Replace `{{PLACEHOLDER}}` tokens with actual content
3. Adjust row count / node count by duplicating elements with y-offset
4. Adjust `viewBox` height if content exceeds default
5. Save final SVG → convert to PNG with cairosvg for messaging platforms

**For detailed placeholder lists, color system, and extension methods:** read `references/template-guide.md`

## Key Rules

- **viewBox width = 1200** (landscape, ~16:9). Adjust height as needed.
- **Font stack:** `'Inter','Helvetica Neue','Microsoft YaHei',sans-serif` — never change order.
- **Status colors:** Green=#43A047, Amber=#FF8F00, Grey=#90A4AE, Red=#E53935
- **Shadow filter** on all cards: `filter="url(#cardShadow)"` or equivalent id.
- **Row spacing:** duplicate row blocks with +56px (list) or +60px (checklist) y-offset.
- **PNG conversion:** `python3 -c "import cairosvg; cairosvg.svg2png(url='in.svg', write_to='out.png', output_width=2400)"`
- When sending via Feishu/WeChat, always convert to PNG first (SVG not rendered inline).
- **飞书图文卡片集成:** 生成 PNG 后，使用 `feishu-rich-card` skill 将图片嵌入飞书交互式卡片，实现图文混排汇报。参见 `../feishu-rich-card/SKILL.md`。
