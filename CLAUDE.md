# CLAUDE.md - MedgeClaw Project Instructions

## Project Overview

MedgeClaw is a biomedical AI research assistant. You are the execution layer —
users describe analyses in natural language, and you write + run the code.

## 🔄 项目同步（重要）

**MedgeClaw 与 OpenClaw 的集成通过 `.medgeclaw-sync.yml` 配置文件管理。**

### 初始化/更新同步
```bash
cd <MedgeClaw项目目录>
python3 sync.py
openclaw gateway restart
```

### 同步内容
- 项目文档（MEDGECLAW.md, IDENTITY.md）→ OpenClaw workspace
- 自定义 skills → OpenClaw workspace/skills/
- SOUL.md / AGENTS.md 追加 MedgeClaw 身份段落
- openclaw.json 添加 MedgeClaw skills 路径

### 修改同步配置
编辑 `.medgeclaw-sync.yml`，无需改 `sync.py` 或 `medgeclaw-init.sh`。

## 📁 输出路径约束（重要）

**所有任务输出必须写入以下目录，不得写入项目根目录或其他位置：**

| 输出类型 | 路径 | 说明 |
|---------|------|------|
| 数据分析任务 | `data/<task_name>/output/` | CSV、图表、报告 |
| Dashboard | `data/<task_name>/dashboard/` | state.json, dashboard.html, serve.py |
| 科学写作 | `writing_outputs/<date>_<topic>/` | LaTeX、PDF、参考文献 |
| 临时文件 | `data/<task_name>/temp/` | 中间产物 |

**禁止写入：**
- ❌ 项目根目录
- ❌ `outputs/`（已废弃，仅保留兼容）
- ❌ OpenClaw workspace

**`.gitignore` 已配置忽略所有输出目录，确保不会误提交数据。**

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
- `data/<task_name>/output/` — per-task analysis results (CSV, images, reports)
- `data/<task_name>/dashboard/` — per-task dashboard (state.json, dashboard.html, serve.py)
- `outputs/` — legacy shared output directory (prefer per-task output/ for new tasks)
- `visualization/` — HTML dashboards and interactive visualizations
- `skills/` — OpenClaw skill definitions (dashboard, biomed-dispatch, cjk-viz)
- `scientific-skills/` — K-Dense 140 scientific skills (git submodule, read-only)

Always `mkdir -p` output and dashboard directories before writing files there.

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
| SVG 信息面板 | `svg-ui-templates`（列表、清单、流程图、报告） |
| 飞书图文汇报 | `feishu-rich-card`（图片上传 + Card Kit 交互卡片） |

如果不确定用哪个 skill，可以 `ls scientific-skills/scientific-skills/` 浏览完整列表。

## ClawBio 精准医学技能

**用户提到药物基因组、GWAS、基因组比较、营养基因组、Galaxy 工具等任务时，使用 ClawBio 技能。**

技能脚本位于 `skills/clawbio/`，在 Docker 容器内路径为 `/workspace/skills/clawbio/`。
容器已设置 `PYTHONPATH=/workspace/skills/clawbio`。

### 任务 → 技能映射

| 任务类型 | 技能 | 命令示例 |
|----------|------|----------|
| 药物基因组/用药指导 | `pharmgx-reporter` | `docker exec medgeclaw python3 /workspace/skills/clawbio/pharmgx-reporter/pharmgx_reporter.py --demo --output ...` |
| GWAS 变异查询 | `gwas-lookup` | `docker exec medgeclaw python3 /workspace/skills/clawbio/gwas-lookup/gwas_lookup.py --rsid rs3798220 --output ...` |
| 多基因风险评分 | `gwas-prs` | `docker exec medgeclaw python3 /workspace/skills/clawbio/gwas-prs/gwas_prs.py --demo --output ...` |
| ClinPGx 数据库查询 | `clinpgx` | `docker exec medgeclaw python3 /workspace/skills/clawbio/clinpgx/clinpgx.py --demo --output ...` |
| 营养基因组 | `nutrigx-advisor` | `docker exec medgeclaw python3 /workspace/skills/clawbio/nutrigx-advisor/nutrigx_advisor.py --demo --output ...` |
| 基因组比较/IBS | `genome-compare` | `docker exec medgeclaw python3 /workspace/skills/clawbio/genome-compare/genome_compare.py --demo --output ...` |
| 祖源 PCA | `claw-ancestry-pca` | `docker exec medgeclaw python3 /workspace/skills/clawbio/claw-ancestry-pca/ancestry_pca.py --demo --output ...` |
| 群体公平性/HEIM | `equity-scorer` | `docker exec medgeclaw python3 /workspace/skills/clawbio/equity-scorer/equity_scorer.py --demo --output ...` |
| Galaxy 生物信息工具 | `galaxy-bridge` | `docker exec medgeclaw python3 /workspace/skills/clawbio/galaxy-bridge/galaxy_bridge.py --demo` |
| 图表数据提取 | `data-extractor` | `docker exec medgeclaw python3 /workspace/skills/clawbio/data-extractor/data_extractor.py --input <img> --output ...` |
| 个人基因组报告 | `profile-report` | `docker exec medgeclaw python3 /workspace/skills/clawbio/profile-report/profile_report.py --demo --output ...` |

### 使用要点

- 所有技能支持 `--demo` 模式，用户无数据时直接演示
- 输出路径统一为 `/workspace/data/<task_name>/output/`
- 基因文件自动识别格式（23andMe/AncestryDNA/VCF）
- 涉及图表生成时，技能内已集成 CJK 字体检测
- 统一 runner：`docker exec medgeclaw python3 /workspace/skills/clawbio/runner.py list`

## Scientific Writer 参考（K-Dense）

**遇到学术写作、文献综述、基金申请、临床报告等写作任务时，必须查阅 Scientific Writer Skills。**

Skills 位于 `scientific-writer/skills/` 目录，每个子目录包含一个 `SKILL.md`。
项目级指令见 `scientific-writer/CLAUDE.md`。

### 常见写作任务 → Skill 映射

| 任务类型 | 推荐 Skill |
|----------|-----------|
| 科研论文（IMRaD） | `scientific-writing` |
| 文献综述 | `literature-review` |
| 基金申请书 | `research-grants` |
| 临床报告 | `clinical-reports` |
| 临床决策支持 | `clinical-decision-support` |
| 治疗方案 | `treatment-plans` |
| 市场研究报告 | `market-research-reports` |
| 引用管理/BibTeX | `citation-management` |
| 实时文献检索 | `research-lookup` |
| 科学示意图 | `scientific-schematics` |
| AI 图像生成 | `generate-image` |
| 学术幻灯片 | `scientific-slides` |
| 学术海报（LaTeX） | `latex-posters` |
| 学术海报（PPTX） | `pptx-posters` |
| 论文转网页/视频 | `paper-2-web` |
| 同行评审 | `peer-review` |
| 科学批判性思维 | `scientific-critical-thinking` |
| 学术评价 | `scholar-evaluation` |
| 期刊/会议模板 | `venue-templates` |
| 假设生成 | `hypothesis-generation` |
| 文档格式转换 | `markitdown` |

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

## Dashboard（任务可视化看板）

**每次数据分析任务都必须启动 Dashboard。** 它是用户实时了解进度和产物的唯一窗口。

详细规范见 `skills/dashboard/SKILL.md`。核心要点：

### 启动流程
```bash
TASK_DIR=data/<task_name>
mkdir -p "$TASK_DIR/dashboard"
cp skills/dashboard/dashboard.html "$TASK_DIR/dashboard/"
cp skills/dashboard/dashboard_serve.py "$TASK_DIR/dashboard/"
# 生成初始 state.json（见下文）
# 启动 server（serve 任务根目录，不是 dashboard/ 子目录）
python "$TASK_DIR/dashboard/dashboard_serve.py" --port 7788
# Dashboard URL: http://localhost:7788/dashboard/dashboard.html
```

### state.json 核心面板

| 面板 | 说明 |
|------|------|
| `progress` | 进度百分比（置顶在 header） |
| `list` (分析计划) | 总览所有步骤 + 完成状态（✅/⏳） |
| `step` | **每步一个**：desc + code（核心片段，默认折叠）+ code_file（完整脚本路径）+ outputs（图片/表格/文字产物） |
| `files` | 最终产物文件列表（可预览/下载） |

### 关键规则
1. **每完成一步就更新 state.json**，不要等全部做完再写
2. **表格用文件引用** `{"src": "/output/table1.csv"}`，前端实时加载 CSV
3. **图片路径用绝对路径**：`/output/fig1.png`（相对于 serve 根 = 任务根）
4. **step 面板要有 code 和 code_file**——核心片段帮助快速理解，完整脚本供深入查看
5. **所有预览内容都可复制/下载**（前端已内置按钮）
6. **启动后立即告诉用户 Dashboard URL**

## 交互规范：边干边说

**不要闷头干活。** 每个关键节点都要简短汇报进展。

## 飞书图文汇报

**当需要向飞书群发送分析结果或进度汇报时，优先使用图文卡片而非纯文本。**

### 工作流
```
生成图片（SVG模板/matplotlib/PIL） → cairosvg 转 PNG → 上传飞书 → Card Kit 发送
```

### 关键要点
- 使用 `skills/svg-ui-templates/` 生成专业级信息面板
- 使用 `skills/feishu-rich-card/references/send_card.py` 发送卡片
- 图片必须先上传获取 `image_key`，不能用 URL
- Card schema 必须是 `"2.0"`
- 详见 `skills/feishu-rich-card/SKILL.md` 和 `skills/svg-ui-templates/SKILL.md`

- 开始前：说一句打算怎么做
- 每步完成后：报一下结果（一两句话）
- 遇到问题：立刻说，不要自己闷头排查太久
- 长任务等待中：冒个泡，说明在等什么
- 完成后：简短总结结果

示例：
> "先看数据结构… 96628 行，5 个 wave。开始写分析脚本。"
> "Python 跑完了，7 个文件。RCS 图有 bug，修一下。"
> "发现 .ttc 字体的坑，改用 FontProperties 模式。"

**粒度：** 每个有意义的动作或发现说一句，不需要每个 tool call 都汇报。
