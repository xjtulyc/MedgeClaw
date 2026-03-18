---
name: biomed-dispatch
description: >
  Dispatch biomedical research and data analysis tasks to Claude Code with
  K-Dense Scientific Skills. Use this skill when the user asks to run any
  bioinformatics, genomics, drug discovery, clinical data analysis,
  proteomics, multi-omics, medical imaging, or scientific computation task.
  Also use for literature search (PubMed, bioRxiv), pathway analysis,
  protein structure prediction, or scientific writing tasks.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🧬"
    requires:
      bins: ["claude"]
---

# Biomedical Analysis Dispatch

## Purpose
Bridge between the OpenClaw conversational interface and Claude Code's
scientific execution environment (K-Dense Scientific Skills).

## When to use
- Any bioinformatics task: RNA-seq, scRNA-seq, variant calling, sequence analysis
- Drug discovery: molecular docking, virtual screening, ADMET prediction
- Clinical data: survival analysis, variant interpretation, clinical trials search
- Multi-omics: proteomics, metabolomics, pathway enrichment
- Medical imaging: DICOM processing, digital pathology
- Scientific communication: literature review, scientific writing, figure generation
- Any request mentioning specific tools: DESeq2, Seurat, Scanpy, RDKit, BioPython, etc.

## Workflow

1. **Identify task type** from the user's request
2. **Locate data files** — check if user mentioned a file path; if not, list `/workspace/data/` and confirm with user
3. **Set up Dashboard** — every analysis task must have a live dashboard:
   ```bash
   TASK_DIR=data/<task_name>
   mkdir -p "$TASK_DIR/dashboard" "$TASK_DIR/output"
   cp skills/dashboard/dashboard.html "$TASK_DIR/dashboard/"
   cp skills/dashboard/dashboard_serve.py "$TASK_DIR/dashboard/"
   # Write initial state.json with: progress(0%), 研究概要, 分析计划(list), empty steps
   # Start server
   python "$TASK_DIR/dashboard/dashboard_serve.py" --port <free_port> &
   # Tell user the URL immediately: http://localhost:<port>/dashboard/dashboard.html
   ```
4. **拆分长任务** — 如果任务包含多个阶段（如：文献搜索 + 写大纲 + 写正文 + 做图 + 编译），**必须拆成多个 Claude Code session**，每个 session 只做一件事：
   - Phase 1: 文献搜索 + 大纲
   - Phase 2: 写正文（或分章节）
   - Phase 3: 生成图表
   - Phase 4: 编译 PDF
   - **原因：** 单次 CC session 超过 10 分钟大概率卡住（上下文窗口满、API 超时、生成超长文本）
5. **Construct the Claude Code prompt** — 短而聚焦，包含 dashboard 更新指令：
   - Which scientific skill(s) to use（**明确指定 skill 路径**，如 `先读 ~/next-medgeai/MedgeClaw/scientific-skills/scientific-skills/scientific-writing/SKILL.md`）
   - Input file path(s)
   - Output directory: always `$TASK_DIR/output/`
   - **Dashboard state.json path** and update expectations:
     - Update progress after each step
     - Use `step` panels with `desc`, `code`, `code_file`, `outputs`
     - Use `{"src": "/output/file.csv"}` for table references (NOT inline data)
     - Image paths absolute: `/output/fig1.png`
   - Expected output format (table, figure, report)
6. **Execute** via Claude Code CLI（推荐 stream-json + hooks）:
   ```bash
   # 推荐：stream-json 模式（可观测）
   cd "$TASK_DIR" && claude -p "短任务描述。先读 skill 文件。完成后: openclaw system event --text 'Done: 摘要' --mode now" \
     --output-format stream-json \
     --verbose \
     --dangerously-skip-permissions \
     2>/dev/null | tail -1
   
   # 旧方式（不推荐，无可观测性）
   claude --dangerously-skip-permissions -p "Use available scientific skills. [TASK]. Input: [PATH]. Outputs: $TASK_DIR/output/. Update dashboard at $TASK_DIR/dashboard/state.json after each step (step panels with code + outputs). Completion: openclaw system event --text 'Done: summary' --mode now"
   ```
7. **Monitor** — 用 hooks 的 `progress.json` 判断进度：
   - 如果 `last_update` 超过 5 分钟没变 → 大概率卡了，kill 掉重来
   - 如果任务 >30s，告知用户后台运行中
8. **Report back** — 总结结果，指向 dashboard URL

## 科学写作任务的特殊处理

**文献综述 / 论文写作必须拆分：**

```bash
# Phase 1: 文献搜索 + 大纲（5-10 分钟）
cd writing_outputs/<task_name> && claude -p "读 ~/next-medgeai/MedgeClaw/scientific-skills/scientific-skills/literature-review/SKILL.md 和 scientific-writing/SKILL.md。按 literature-review 流程搜索文献，创建 outline.md（Stage 1）。" \
  --output-format stream-json --verbose --dangerously-skip-permissions 2>/dev/null | tail -1

# Phase 2: 写正文（分章节，每章 5-10 分钟）
cd writing_outputs/<task_name> && claude -p "读 outline.md 的第 1-3 节。用 Edit 工具在 manuscript.tex 中补充这些章节的正文。写完整的学术散文。" \
  --output-format stream-json --verbose --dangerously-skip-permissions 2>/dev/null | tail -1

# Phase 3: 创建 BibTeX + 添加引用（5 分钟）
cd writing_outputs/<task_name> && claude -p "读 manuscript.tex 和 outline.md。创建 references/references.bib（至少 30 篇），在 tex 中添加 \cite{}（每节至少 5 处），在 \end{document} 前加 \bibliographystyle{unsrt} 和 \bibliography{references}。" \
  --output-format stream-json --verbose --dangerously-skip-permissions 2>/dev/null | tail -1

# Phase 4: 生成图表（5-10 分钟）
cd writing_outputs/<task_name> && claude -p "在 figures/ 下创建 5 个 Python 脚本生成图表 PDF。中文标签用 Noto Sans CJK SC 字体。" \
  --output-format stream-json --verbose --dangerously-skip-permissions 2>/dev/null | tail -1

# Phase 5: 编译 PDF（手动或简单 CC）
cd writing_outputs/<task_name>/drafts && xelatex -output-directory=../final manuscript.tex
cd ../final && bibtex manuscript && cd ../drafts && xelatex -output-directory=../final manuscript.tex && xelatex -output-directory=../final manuscript.tex
```

**为什么必须拆分：**
- 单次让 CC 做完所有步骤（搜文献 + 写大纲 + 写正文 + 做图 + 编译）会导致：
  - 上下文窗口满（74 篇摘要 + task.md + skill 文件 + LaTeX 模板 = 超大上下文）
  - Opus 生成超长 LaTeX 文本（数千 token）需要 10+ 分钟，容易超时
  - 中途卡住后无法恢复，只能重来
- 拆分后每个 phase 独立，失败了只需重跑该 phase

## Output handling
- Tables → summarize top rows, mention full file path
- Figures → send the image file to the user directly
- Reports → send the PDF/HTML file to the user directly
- Errors → show the error message and suggest a fix

## Example dispatches

**Clinical data analysis (complete flow with dashboard):**
```bash
# 1. Setup
TASK_DIR=data/charls_ace
mkdir -p "$TASK_DIR/dashboard" "$TASK_DIR/output"
cp skills/dashboard/dashboard.html "$TASK_DIR/dashboard/"
cp skills/dashboard/dashboard_serve.py "$TASK_DIR/dashboard/"
# 2. Write initial state.json
# 3. Start dashboard server
python "$TASK_DIR/dashboard/dashboard_serve.py" --port 7790 &
# 4. Dispatch to Claude Code
claude --dangerously-skip-permissions -p "分析 CHARLS 队列中 ACE 与 CVD 的关联。Input: data/charls_ace/charls.dta. Output: data/charls_ace/output/. 每步更新 dashboard state.json（step panels with code + outputs）。完成后: openclaw system event --text 'Done: ACE-CVD分析完成' --mode now"
```

**RNA-seq differential expression:**
```bash
claude --dangerously-skip-permissions -p "Use DESeq2 scientific skill. Run differential expression. Counts: /workspace/data/counts.csv, metadata: /workspace/data/meta.csv, contrast: treatment vs control. Save to /workspace/data/rnaseq/output/. Update dashboard at /workspace/data/rnaseq/dashboard/state.json."
```

**Single-cell RNA-seq:**
```bash
claude --dangerously-skip-permissions -p "Use Scanpy scientific skill. Analyze 10X data at /workspace/data/10x/. QC, clustering, markers. Save to /workspace/data/10x/output/. Update dashboard state.json with step panels."
```

## 输出路径约束（重要）

**所有任务输出必须写入指定目录：**

| 任务类型 | 输出路径 | 说明 |
|---------|---------|------|
| 数据分析 | `data/<task_name>/output/` | CSV、图表、报告 |
| Dashboard | `data/<task_name>/dashboard/` | state.json, dashboard.html, serve.py |
| 科学写作 | `writing_outputs/<date>_<topic>/` | LaTeX、PDF、BibTeX、figures/ |
| 临时文件 | `data/<task_name>/temp/` | 中间产物 |

**禁止写入：**
- ❌ 项目根目录（`~/next-medgeai/MedgeClaw/`）
- ❌ `/workspace/outputs/`（已废弃）
- ❌ `/workspace/data/`（只读，用户输入数据）

## ClawBio 精准医学技能

以下技能通过 Docker 执行，脚本位于 `/workspace/skills/clawbio/`。
容器已设置 `PYTHONPATH=/workspace/skills/clawbio`，可直接运行。

### 路由表

| 用户意图 | 技能 | Docker 命令 |
|---------|------|-------------|
| 药物基因组/用药指导/CYP2D6/华法林/CPIC | pharmgx-reporter | `docker exec medgeclaw python3 /workspace/skills/clawbio/pharmgx-reporter/pharmgx_reporter.py --input <file> --output /workspace/data/<task>/output/` |
| GWAS 变异查询/rsID/PheWAS/eQTL | gwas-lookup | `docker exec medgeclaw python3 /workspace/skills/clawbio/gwas-lookup/gwas_lookup.py --rsid <rsid> --output /workspace/data/<task>/output/` |
| 多基因风险评分/PRS/遗传风险 | gwas-prs | `docker exec medgeclaw python3 /workspace/skills/clawbio/gwas-prs/gwas_prs.py --input <file> --output /workspace/data/<task>/output/` |
| ClinPGx/基因-药物数据库/PharmGKB | clinpgx | `docker exec medgeclaw python3 /workspace/skills/clawbio/clinpgx/clinpgx.py --gene <symbol> --output /workspace/data/<task>/output/` |
| 营养基因组/MTHFR/叶酸/维生素D/咖啡因 | nutrigx-advisor | `docker exec medgeclaw python3 /workspace/skills/clawbio/nutrigx-advisor/nutrigx_advisor.py --input <file> --output /workspace/data/<task>/output/` |
| 基因组比较/IBS/祖源估计 | genome-compare | `docker exec medgeclaw python3 /workspace/skills/clawbio/genome-compare/genome_compare.py --input <file> --output /workspace/data/<task>/output/` |
| 祖源PCA/群体结构/SGDP | claw-ancestry-pca | `docker exec medgeclaw python3 /workspace/skills/clawbio/claw-ancestry-pca/ancestry_pca.py --demo --output /workspace/data/<task>/output/` |
| 群体公平性/HEIM评分/FST | equity-scorer | `docker exec medgeclaw python3 /workspace/skills/clawbio/equity-scorer/equity_scorer.py --input <file> --output /workspace/data/<task>/output/` |
| Galaxy工具/NGS流水线/usegalaxy | galaxy-bridge | `docker exec medgeclaw python3 /workspace/skills/clawbio/galaxy-bridge/galaxy_bridge.py --search <query>` |
| 科学图表数据提取 | data-extractor | `docker exec medgeclaw python3 /workspace/skills/clawbio/data-extractor/data_extractor.py --input <img> --output /workspace/data/<task>/output/` |
| 个人基因组报告/统一档案 | profile-report | `docker exec medgeclaw python3 /workspace/skills/clawbio/profile-report/profile_report.py --demo --output /workspace/data/<task>/output/` |
| RNA-seq差异表达/DESeq2/火山图 | rnaseq-de | `docker exec medgeclaw python3 /workspace/skills/clawbio/rnaseq-de/rnaseq_de.py --counts <file> --metadata <file> --output /workspace/data/<task>/output/` |

### ClawBio Runner（批量运行）

也可通过统一 runner 运行：
```bash
docker exec medgeclaw python3 /workspace/skills/clawbio/runner.py list
docker exec medgeclaw python3 /workspace/skills/clawbio/runner.py run pharmgx --demo --output /workspace/data/<task>/output/
```

### Demo 模式

所有 ClawBio 技能支持 `--demo` 模式，使用合成数据即时演示。
**当用户没有输入文件时，直接使用 `--demo` 运行并说明为合成数据，不要拒绝。**

### 基因档案（PatientProfile）

用户上传基因数据（23andMe/AncestryDNA/VCF）后，可创建持久化档案：
```bash
docker exec medgeclaw python3 -c "
from clawbio.common.profile import PatientProfile
p = PatientProfile.from_genetic_file('/workspace/data/<file>', patient_id='<id>')
p.save('/workspace/data/profiles/<id>.json')
"
```
后续技能可通过 `--profile /workspace/data/profiles/<id>.json` 复用，无需重复上传。

## Important rules
- Never modify raw data files in `/workspace/data/`
- If the user's request is ambiguous, ask one clarifying question before dispatching
- If Claude Code returns an error about a missing package, retry with `uv pip install [package]` prepended to the command
- **涉及中文可视化时**，在 prompt 中加入：绘图前先导入 `skills/cjk-viz/scripts/setup_cjk_font.py` 执行字体检测，不要硬编码字体名
