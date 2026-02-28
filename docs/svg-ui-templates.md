# SVG UI Templates

Professional-grade SVG information panels for structured data display.

## Overview

Generates landscape-oriented (1200px wide) SVG panels optimized for:
- Messaging platforms (Feishu, Slack, Discord) — convert to PNG first
- Research dashboards and reports
- Team progress updates and status boards

## Templates

| Template | Use Case | Example |
|----------|----------|---------|
| **list-panel** | Data tables, parameter lists, comparison tables | Analysis results, configuration summaries |
| **checklist-panel** | Task checklists, progress tracking, TODOs | Sprint status, experiment checklist |
| **pipeline-status** | Flow diagrams, stage status, milestones | Bioinformatics pipeline, CI/CD status |
| **richtext-layout** | Mixed text+image, report summaries, data briefs | Weekly reports, analysis summaries |

## Workflow

```
1. Read template SVG from skills/svg-ui-templates/assets/
2. Replace {{PLACEHOLDER}} tokens with actual content
3. Adjust row count / viewBox height as needed
4. Save SVG → convert to PNG:
   python3 -c "import cairosvg; cairosvg.svg2png(url='in.svg', write_to='out.png', output_width=2400)"
5. (Optional) Send via Feishu Rich Card skill
```

## Design Specs

- **viewBox width**: 1200 (landscape ~16:9)
- **Font stack**: `'Inter','Helvetica Neue','Microsoft YaHei',sans-serif`
- **Status colors**: Green=#43A047, Amber=#FF8F00, Grey=#90A4AE, Red=#E53935
- **Card shadow**: `filter="url(#cardShadow)"`
- **Row spacing**: +56px (list) or +60px (checklist)

## Integration

Works seamlessly with:
- **feishu-rich-card** — upload PNG → embed in Feishu interactive card
- **Research Dashboard** — embed as inline image in step outputs
- **biomed-dispatch** — generate status panels during long-running analyses

## Detailed Reference

See `skills/svg-ui-templates/references/template-guide.md` for full placeholder lists, color system, and extension methods.
