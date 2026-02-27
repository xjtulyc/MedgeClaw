# Research Dashboard

MedgeClaw's Research Dashboard provides real-time visibility into analysis tasks. Every task gets a live web page showing progress, code, outputs, and downloadable artifacts.

## Overview

When an analysis starts, the system:
1. Creates a `dashboard/` directory inside the task folder
2. Copies `dashboard.html` and `dashboard_serve.py` from `skills/dashboard/`
3. Writes an initial `state.json` with the analysis plan
4. Starts a local HTTP server
5. Updates `state.json` after each step completes

The frontend polls `state.json` every 2 seconds and re-renders automatically.

## Quick Start

```bash
TASK_DIR=data/my_analysis
mkdir -p "$TASK_DIR/dashboard" "$TASK_DIR/output"

# Copy templates
cp skills/dashboard/dashboard.html "$TASK_DIR/dashboard/"
cp skills/dashboard/dashboard_serve.py "$TASK_DIR/dashboard/"

# Start server (serves task root directory, not dashboard/ subdir)
python "$TASK_DIR/dashboard/dashboard_serve.py" --port 7788 &

# Open: http://localhost:7788/dashboard/dashboard.html
```

## Architecture

```
Task Root (e.g., data/charls_ace/)
├── dashboard/
│   ├── dashboard.html       ← Single-file frontend (no build step)
│   ├── dashboard_serve.py   ← ThreadingHTTPServer (serves task root)
│   └── state.json           ← Data protocol (updated by AI)
├── output/
│   ├── fig1.png             ← Referenced by state.json as /output/fig1.png
│   ├── table1.csv
│   └── ...
├── analysis.py              ← Full script (referenced by code_file)
└── raw_data.csv
```

**Important:** The server serves the **task root directory**, not `dashboard/`. This allows the frontend to access files in `output/` and script files via absolute paths.

## state.json Schema

```json
{
  "title": "Task Title",
  "updated_at": "2026-02-27 05:00:00",
  "panels": [
    { "type": "progress", "label": "Overall Progress", "content": 75 },
    { "type": "text", "label": "Research Summary", "content": "..." },
    { "type": "list", "label": "Analysis Plan", "content": ["✅ Step 1", "⏳ Step 2", "..."] },
    { "type": "step", "label": "① Data Loading", "content": { "desc": "...", "code": "...", "code_file": "/analysis.py", "outputs": [...] } },
    { "type": "files", "label": "Output Files", "content": [{"name": "fig1.png", "size": "76 KB"}] }
  ]
}
```

## Panel Types

### `progress`
Renders in the sticky header as a progress bar. Not shown in the panel area.
```json
{"type": "progress", "label": "Overall Progress", "content": 85}
```

### `text`
Pre-formatted text with copy button.
```json
{"type": "text", "label": "Key Findings", "content": "ACE score negatively associated with CHD (OR=0.95)..."}
```

### `list`
Bordered list items. Use for analysis plans, completed steps, etc.
```json
{"type": "list", "label": "Analysis Plan (9 steps)", "content": ["✅ ① Data loading", "⏳ ② Baseline table", "..."]}
```

### `code`
Monospace code block with copy button.
```json
{"type": "code", "label": "Script Output", "content": "Processing 96628 rows..."}
```

### `table`
Two modes — **file reference** (recommended) or inline data.

**File reference** — frontend fetches and parses CSV at runtime:
```json
{"type": "table", "label": "Table 1", "content": {"src": "/output/table1.csv"}}
```

**Inline data** (legacy, for small tables):
```json
{"type": "table", "label": "Table 1", "content": {"headers": ["Var", "Value"], "rows": [["Age", "65.5"]]}}
```

Both modes support: sticky headers, horizontal/vertical scroll, copy as TSV, download CSV.

### `image`
Inline image preview with lightbox zoom and download button.
```json
{"type": "image", "label": "Figure 1", "content": "/output/fig1.png"}
```

Multiple images (auto-grid):
```json
{"type": "image", "label": "All Figures", "content": ["/output/fig1.png", "/output/fig2.png"]}
```

### `files`
File browser with icons, size info, and one-click actions:
- **Images** → click to lightbox preview
- **CSV/TSV** → click to parse and show as table modal
- **TXT/MD/JSON** → click to show as code modal
- **Other** → click to download

```json
{"type": "files", "label": "Output Files", "content": [
  {"name": "fig1.png", "size": "76 KB"},
  {"name": "table1.csv", "size": "599 B"}
]}
```

### `step` (core panel)

The primary panel type for analysis workflows. Each step = what was done + what code ran + what was produced.

```json
{
  "type": "step",
  "label": "① Data Loading & Cleaning",
  "content": {
    "desc": "Loaded CHARLS .dta data (5 waves), coded 8 ACE indicators...",
    "code": "import pandas as pd\ndf = pd.read_stata('charls.dta')\n...",
    "code_file": "/analysis.py",
    "outputs": [
      {"kind": "text", "value": "Original: 96,628 rows → Filtered: 46,628 rows"},
      {"kind": "image", "src": "/output/fig1.png", "caption": "ACE Score Distribution"},
      {"kind": "table", "src": "/output/table1.csv", "caption": "Baseline Characteristics"},
      {"kind": "file", "src": "/output/table1.csv"}
    ]
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `desc` | ✅ | What was done & what was found (complete sentences) |
| `code` | Optional | Key code snippet (rendered in collapsible `<details>`, collapsed by default) |
| `code_file` | Optional | Path to full script (loaded on-demand when user clicks) |
| `outputs` | Optional | List of outputs this step produced |

#### Output kinds

| kind | Fields | Rendering |
|------|--------|-----------|
| `text` | `value` | Highlighted text block with copy button |
| `image` | `src`, `caption?` | Inline image, click to zoom, download button |
| `table` | `src`, `caption?` | Fetch CSV, render as scrollable table with copy/download |
| `file` | `src` | Download link with file icon |

## Path Conventions

All resource paths use **absolute paths** relative to the serve root (= task root directory):

```
/output/fig1.png          ✅ correct
/analysis.py              ✅ correct
../output/fig1.png        ❌ wrong (relative)
output/fig1.png           ❌ wrong (no leading slash)
```

## Design

- **Color palette**: IBM color-blind safe (Blue #648FFF, Purple #785EF0, Magenta #DC267F, Orange #FE6100, Yellow #FFB000)
- **Theme**: GitHub Dark Dimmed
- **Typography**: System fonts + Noto Sans SC for CJK
- **Animations**: Cubic-bezier ease-out for smooth, damped transitions
- **Interactions**: Collapsible panels (state remembered per session), lightbox for images, modal for CSV/text preview

## Server Details

`dashboard_serve.py` uses Python's `http.server.ThreadingHTTPServer`:
- Multi-threaded (handles concurrent requests without blocking)
- `allow_reuse_address = True` (fast restart without TIME_WAIT issues)
- `daemon_threads = True` (clean shutdown)
- Serves the task root directory (auto-detected from script location)
- CORS enabled for local development
- Cache-Control: no-cache (always fresh state.json)

## Clipboard Support

Copy buttons use `navigator.clipboard.writeText()` with a fallback to `document.execCommand('copy')` for HTTP (non-secure) contexts. Both work on `http://localhost`.
