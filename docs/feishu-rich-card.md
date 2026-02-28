# Feishu Rich Card — 飞书图文混排卡片

Send image-rich interactive cards in Feishu group chats for progress reports, analysis results, and team updates.

## Overview

Combines any image source (SVG templates, matplotlib charts, PIL-generated graphics) with Feishu Card Kit API to deliver mixed text+image messages.

## Architecture

```
Generate image (SVG→PNG / matplotlib / PIL / existing file)
        ↓
Upload image to Feishu → get image_key
        ↓
Build Card JSON (schema 2.0) → embed img + markdown elements
        ↓
Call Feishu API → send interactive message
```

## Quick Start

```python
from send_card import FeishuCardSender

sender = FeishuCardSender()  # reads credentials from openclaw.json

# Full card with multiple elements
sender.send_rich_card(
    chat_id="oc_xxx",
    title="📊 Analysis Report",
    elements=[
        {"type": "markdown", "content": "## Summary\n\nFound **3** DEGs"},
        {"type": "image", "path": "/tmp/volcano.png", "alt": "Volcano plot"},
        {"type": "hr"},
        {"type": "markdown", "content": "**Conclusion:** Significant differences found."},
    ],
    header_template="blue"
)

# Simple image + text report
sender.send_image_report(
    chat_id="oc_xxx",
    title="🧬 scRNA-seq Complete",
    intro="UMAP done, 12 clusters identified:",
    image_path="/tmp/umap.png",
    conclusion="Cluster 5 = target cells (CD8A, GZMB, PRF1)",
    header_template="indigo"
)
```

## Card Elements

| Element | Description |
|---------|-------------|
| `markdown` | Bold, italic, links, lists, blockquotes, code blocks |
| `img` | Image (requires `image_key` from upload) |
| `hr` | Horizontal divider |
| `column_set` | Multi-column layout |
| `note` | Grey footer note |

## Header Colors

`blue` `wathet` `turquoise` `green` `yellow` `orange` `red` `carmine` `violet` `purple` `indigo` `grey`

## Key Rules

1. Images **must be uploaded** to Feishu to get `image_key` — URLs don't work
2. Card schema must be `"2.0"`
3. Max 50 elements per card
4. Recommended image width: 600–1200px (Feishu auto-scales)
5. Markdown cannot embed images — use separate `img` elements
6. After sending via this skill, reply `NO_REPLY` to avoid duplicate messages

## Integration with SVG UI Templates

```bash
# 1. Generate SVG (from template or custom)
# 2. Convert to PNG
python3 -c "import cairosvg; cairosvg.svg2png(url='report.svg', write_to='report.png', output_width=2400)"
# 3. Send via this skill
```

## Helper Script

`skills/feishu-rich-card/references/send_card.py` — handles credential loading, image upload, card construction, and API calls.
