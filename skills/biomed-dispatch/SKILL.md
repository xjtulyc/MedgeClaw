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
3. **Construct the Claude Code prompt** — be specific about:
   - Which scientific skill(s) to use
   - Input file path(s)
   - Output directory: always `/workspace/outputs/`
   - Expected output format (table, figure, report)
4. **Execute** via Claude Code CLI:
   ```bash
   claude --print "Use available scientific skills. [TASK DESCRIPTION]. Input: [PATH]. Save all outputs to /workspace/outputs/. [SPECIFIC INSTRUCTIONS]."
   ```
5. **Monitor** — if the task takes >30s, inform the user it is running in background
6. **Report back** — summarize results, list output files, and suggest logical next steps

## Output handling
- Tables → summarize top rows, mention full file path
- Figures → send the image file to the user directly
- Reports → send the PDF/HTML file to the user directly
- Errors → show the error message and suggest a fix

## Example dispatches

**RNA-seq differential expression:**
```bash
claude --print "Use DESeq2 scientific skill. Run differential expression analysis. Counts matrix: /workspace/data/counts.csv, metadata: /workspace/data/meta.csv, contrast: treatment vs control. Save volcano plot and results table to /workspace/outputs/."
```

**Single-cell RNA-seq:**
```bash
claude --print "Use Scanpy scientific skill. Analyze 10X Genomics data at /workspace/data/10x/. Run QC, clustering, and marker gene identification. Save UMAP plot and cluster annotations to /workspace/outputs/."
```

**Literature search:**
```bash
claude --print "Use PubMed scientific skill. Search for recent papers (last 2 years) on [TOPIC]. Summarize top 10 results with abstracts. Save to /workspace/outputs/literature_review.md"
```

**Survival analysis:**
```bash
claude --print "Use survival analysis scientific skill with lifelines. Input: /workspace/data/clinical.csv. Columns: time=OS_months, event=OS_status, group=treatment. Generate Kaplan-Meier plot and log-rank test results. Save to /workspace/outputs/."
```

## Important rules
- Always save outputs to `/workspace/outputs/` — never to `/workspace/data/`
- Never modify raw data files in `/workspace/data/`
- If the user's request is ambiguous, ask one clarifying question before dispatching
- If Claude Code returns an error about a missing package, retry with `uv pip install [package]` prepended to the command
