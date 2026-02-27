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
4. **Construct the Claude Code prompt** — include dashboard update instructions:
   - Which scientific skill(s) to use
   - Input file path(s)
   - Output directory: always `$TASK_DIR/output/`
   - **Dashboard state.json path** and update expectations:
     - Update progress after each step
     - Use `step` panels with `desc`, `code`, `code_file`, `outputs`
     - Use `{"src": "/output/file.csv"}` for table references (NOT inline data)
     - Image paths absolute: `/output/fig1.png`
   - Expected output format (table, figure, report)
5. **Execute** via Claude Code CLI:
   ```bash
   claude --dangerously-skip-permissions -p "Use available scientific skills. [TASK]. Input: [PATH]. Outputs: $TASK_DIR/output/. Update dashboard at $TASK_DIR/dashboard/state.json after each step (step panels with code + outputs). Completion: openclaw system event --text 'Done: summary' --mode now"
   ```
6. **Monitor** — if the task takes >30s, inform the user it is running in background
7. **Report back** — summarize results, point user to dashboard URL for details

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

## Important rules
- Always save outputs to `/workspace/outputs/` — never to `/workspace/data/`
- Never modify raw data files in `/workspace/data/`
- If the user's request is ambiguous, ask one clarifying question before dispatching
- If Claude Code returns an error about a missing package, retry with `uv pip install [package]` prepended to the command
- **涉及中文可视化时**，在 prompt 中加入：绘图前先导入 `skills/cjk-viz/scripts/setup_cjk_font.py` 执行字体检测，不要硬编码字体名
