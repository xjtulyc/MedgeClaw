# CLAUDE.md - MedgeClaw Project Instructions

## Project Overview

MedgeClaw is a biomedical AI research assistant. You are the execution layer —
users describe analyses in natural language, and you write + run the code.

## Execution Environment

**You run on the host, but execute code inside the Docker container.**

The analysis environment (Python, R, RStudio, JupyterLab, all scientific packages)
lives in the `medgeclaw` Docker container. Always execute scripts via:

```bash
# Python
docker exec medgeclaw python3 /workspace/path/to/script.py

# R
docker exec medgeclaw Rscript /workspace/path/to/script.R

# Install packages if needed
docker exec medgeclaw pip install <package>
docker exec medgeclaw Rscript -e 'install.packages("<package>", repos="https://cran.r-project.org")'
```

If `docker exec` fails with a permission error, use `sg docker -c "docker exec ..."` instead:

```bash
sg docker -c "docker exec medgeclaw python3 /workspace/path/to/script.py"
```

**Path mapping:** The host path `./data/` maps to `/workspace/data/` inside the container.
Write scripts using `/workspace/` paths. The host path `./outputs/` maps to `/workspace/outputs/`.

**Never run analysis scripts directly on the host** — it may lack R, specific Python
packages, or have different versions. The container is the canonical environment.

## Directory Conventions

- `data/` — input data files (read-only, user-provided)
- `outputs/` — analysis results (CSV, Excel, images, reports)
- `visualization/` — HTML dashboards and interactive visualizations
- `skills/` — OpenClaw skill definitions
- `scientific-skills/` — K-Dense 140 scientific skills (git submodule, read-only)

Always `mkdir -p outputs visualization` before writing files there.

## Code Style

- Python preferred for data analysis. Use pandas, scipy, matplotlib, seaborn.
- R available for bioinformatics packages (DESeq2, Seurat, edgeR, etc.)
- Chinese labels in all visualizations (this is a Chinese user base)
- matplotlib: use `Droid Sans Fallback` or similar CJK font, `backend: Agg`
- HTML dashboards: self-contained (base64-embed all images), professional CSS

## Third-Party API Proxy

This project is commonly used with third-party API proxies (not api.anthropic.com).
If you encounter `BashTool Pre-flight check is taking longer than expected`, it means
the `ANTHROPIC_SMALL_FAST_MODEL` environment variable needs to be set to a model the
proxy supports. Tell the user to:

1. Add `ANTHROPIC_SMALL_FAST_MODEL=<model>` to their `.env`
2. Re-run `bash setup.sh`

## Completion Notification

When finishing a long-running task, notify the user:
```bash
openclaw system event --text "Done: <summary>" --mode now
```
