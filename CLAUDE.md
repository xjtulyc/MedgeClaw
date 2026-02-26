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
- matplotlib: **绘图前必须执行 CJK 字体检测**，参考 `skills/cjk-viz/SKILL.md`。
  不要硬编码字体名，使用 `skills/cjk-viz/scripts/setup_cjk_font.py` 自动检测。
  backend 使用 `Agg`。
- HTML dashboards: self-contained (base64-embed all images), professional CSS

## Scientific Skills 参考（K-Dense）

**无论是否使用 Claude Code，遇到生物医药或科研场景任务时，必须主动查阅相关的
K-Dense Scientific Skills 作为参考。**

Skills 位于 `scientific-skills/scientific-skills/` 目录，每个子目录包含一个
`SKILL.md`，描述了该工具/领域的最佳实践、代码模板和注意事项。

### 使用流程

1. **识别任务涉及的工具或领域**（如 RNA-seq → `deseq2`、单细胞 → `scanpy`、
   分子对接 → `diffdock`、文献检索 → `biorxiv-database`）
2. **读取对应的 SKILL.md**：`scientific-skills/scientific-skills/<skill-name>/SKILL.md`
3. **参考其中的代码模板、参数建议、注意事项**来编写代码
4. 如果涉及可视化，同时参考 `skills/cjk-viz/SKILL.md` 确保中文正常显示

### 常见任务 → Skill 映射

| 任务类型 | 推荐 Skill |
|----------|-----------|
| 差异表达分析 | `deseq2`, `edger` |
| 单细胞分析 | `scanpy`, `anndata` |
| 通路富集 | `gseapy`, `enrichr` |
| 蛋白结构预测 | `esm`, `alphafold-database` |
| 分子对接 | `diffdock`, `deepchem` |
| 药物数据库查询 | `drugbank-database`, `chembl-database` |
| 临床试验检索 | `clinicaltrials-database` |
| 变异注释 | `clinvar-database`, `cosmic-database` |
| 文献检索 | `biorxiv-database`, `citation-management` |
| 生存分析 | `lifelines`（在 `exploratory-data-analysis` 中） |
| 科研绘图 | `scientific-visualization`, `matplotlib`, `plotly` |
| 数据探索 | `exploratory-data-analysis` |

如果不确定用哪个 skill，可以 `ls scientific-skills/scientific-skills/` 浏览完整列表。

### 重要原则

- Skills 是**参考资料**，不是死板的模板。根据实际需求灵活运用。
- 优先使用 skill 中推荐的参数和方法，它们经过验证。
- 如果 skill 中的方法不适用于当前场景，说明原因并采用更合适的方案。

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
