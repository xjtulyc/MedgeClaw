#!/usr/bin/env python3
"""
runner.py -- Stripped-down ClawBio skill runner for MedgeClaw.

Usage:
    python runner.py list
    python runner.py run pharmgx --demo
    python runner.py run equity --input data.vcf --output ./results

Designed to run with PYTHONPATH=/workspace/skills/clawbio.
Auto-detects Docker vs host environment.
"""
import argparse, hashlib, os, subprocess, sys, time
from pathlib import Path

# Auto-detect: use /workspace path in Docker, or script's own directory on host
_SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_BASE = Path("/workspace/skills/clawbio") if Path("/workspace").is_dir() else _SCRIPT_DIR
DEFAULT_OUTPUT = Path("/workspace/output") if Path("/workspace").is_dir() else _SCRIPT_DIR / "output"


def _s(script, desc, flags=(), geno=False, no_input=False, demo_args=None):
    """Shorthand skill entry builder."""
    return {"script": script, "description": desc,
            "allowed_extra_flags": set(flags), "accepts_genotypes": geno,
            "no_input_required": no_input,
            "demo_args": demo_args or ["--demo"]}


def _demo_input(path):
    """Build demo_args that use --input with a file relative to SKILLS_BASE."""
    return ["--input", path]


SKILLS = {
    "pharmgx":     _s("pharmgx-reporter/pharmgx_reporter.py",
                       "Pharmacogenomics reporter (12 genes, 31 SNPs, 51 drugs)",
                       ["--weights"], geno=True,
                       demo_args=_demo_input("pharmgx-reporter/demo_patient.txt")),
    "equity":      _s("equity-scorer/equity_scorer.py",
                       "HEIM equity scorer (FST, heterozygosity, pop representation)",
                       ["--weights", "--pop-map"],
                       demo_args=["--input", "examples/demo_populations.vcf",
                                  "--pop-map", "examples/demo_population_map.csv"]),
    "nutrigx":     _s("nutrigx_advisor/nutrigx_advisor.py",
                       "Nutrigenomics advisor (diet, vitamins, caffeine, lactose)",
                       geno=True,
                       demo_args=_demo_input("nutrigx_advisor/tests/synthetic_patient.csv")),
    "scrna":       _s("scrna-orchestrator/scrna_orchestrator.py",
                       "scRNA Orchestrator (Scanpy QC, doublet detection, clustering)",
                       ["--min-genes","--min-cells","--max-mt-pct","--n-top-hvg",
                        "--n-pcs","--n-neighbors","--use-rep","--leiden-resolution",
                        "--random-state","--top-markers","--contrast-groupby",
                        "--contrast-group1","--contrast-group2","--contrast-top-genes",
                        "--contrast-volcano","--de-groupby","--de-group1","--de-group2",
                        "--de-top-genes","--de-volcano","--doublet-method","--annotate",
                        "--annotation-model"]),
    "scrna-embedding": _s("scrna-embedding/scrna_embedding.py",
                       "scRNA Embedding (scVI latent, optional batch integration)",
                       ["--method","--layer","--batch-key","--min-genes","--min-cells",
                        "--max-mt-pct","--n-top-hvg","--latent-dim","--max-epochs",
                        "--n-neighbors","--random-state","--accelerator"]),
    "compare":     _s("genome-compare/genome_compare.py",
                       "Genome comparator (IBS vs George Church + ancestry)",
                       ["--no-figures","--aims-panel","--reference"], geno=True),
    "drugphoto":   _s("pharmgx-reporter/pharmgx_reporter.py",
                       "Drug photo analysis (single-drug PGx lookup)",
                       ["--drug","--dose"], geno=True,
                       demo_args=_demo_input("genome-compare/data/manuel_corpas_23andme.txt.gz")),
    "prs":         _s("gwas-prs/gwas_prs.py",
                       "GWAS Polygenic Risk Score calculator (PGS Catalog, 3000+)",
                       ["--trait","--pgs-id","--min-overlap","--max-variants","--build"],
                       geno=True),
    "clinpgx":     _s("clinpgx/clinpgx.py",
                       "ClinPGx API query (gene-drug interactions, CPIC guidelines)",
                       ["--gene","--genes","--drug","--drugs","--no-cache"],
                       no_input=True),
    "gwas":        _s("gwas-lookup/gwas_lookup.py",
                       "GWAS Lookup -- federated variant query (9 databases)",
                       ["--rsid","--skip","--no-figures","--no-cache","--max-hits"],
                       no_input=True),
    "profile":     _s("profile-report/profile_report.py",
                       "Unified personal genomic profile report",
                       ["--profile"], no_input=True),
    "galaxy":      _s("galaxy-bridge/galaxy_bridge.py",
                       "Galaxy tool discovery and execution (8,000+ tools)",
                       ["--search","--list-categories","--tool-details","--run",
                        "--max-results"], no_input=True),
    "data-extract":_s("data-extractor/data_extractor.py",
                       "Extract numerical data from scientific figure images",
                       ["--web","--port","--plot-type"]),
    "rnaseq":      _s("rnaseq-de/rnaseq_de.py",
                       "Bulk/pseudo-bulk RNA-seq DE (QC + PCA + DE)",
                       ["--counts","--metadata","--formula","--contrast",
                        "--backend","--min-count","--min-samples"]),
}

# ------------------------------------------------------------------ list --- #

def list_skills():
    """Print a simple table of available skills."""
    print(f"{'Skill':<20} {'Geno?':<7} {'Description'}")
    print(f"{'─'*20} {'─'*7} {'─'*50}")
    for name, info in SKILLS.items():
        g = "yes" if info.get("accepts_genotypes") else ""
        print(f"{name:<20} {g:<7} {info['description']}")
    print(f"\n  {len(SKILLS)} skills | run: python runner.py run <skill> --demo")

# ------------------------------------------------------------------- run --- #

def run_skill(skill_name, input_path=None, output_dir=None,
              demo=False, extra_args=None, profile_path=None):
    """Run a ClawBio skill as a subprocess. Returns a result dict."""
    skill_info = SKILLS.get(skill_name)
    if not skill_info:
        return {"skill": skill_name, "success": False, "exit_code": -1,
                "output_dir": None, "stdout": "",
                "stderr": f"Unknown skill '{skill_name}'. Available: {list(SKILLS.keys())}"}
    script_path = str(SKILLS_BASE / skill_info["script"])
    out_dir = output_dir or str(DEFAULT_OUTPUT / skill_name)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    # Build command
    cmd = ["python3", script_path]
    if demo:
        # Use per-skill demo_args (may be --demo or --input <demo_file>)
        demo_args = skill_info.get("demo_args", ["--demo"])
        resolved = []
        for arg in demo_args:
            # Resolve relative paths to SKILLS_BASE
            if arg.startswith("--"):
                resolved.append(arg)
            else:
                candidate = SKILLS_BASE / arg
                resolved.append(str(candidate) if candidate.exists() else arg)
        cmd.extend(resolved)
    elif input_path:
        cmd.extend(["--input", input_path])
    elif not skill_info.get("no_input_required"):
        return {"skill": skill_name, "success": False, "exit_code": -1,
                "output_dir": out_dir, "stdout": "",
                "stderr": "No input provided. Use --demo or --input <file>."}
    cmd.extend(["--output", out_dir])
    if profile_path:
        cmd.extend(["--profile", profile_path])
    # Filter extra_args against per-skill allowlist
    if extra_args:
        allowed = skill_info.get("allowed_extra_flags", set())
        blocked = {"--input", "--output", "--demo"}
        filtered, i = [], 0
        while i < len(extra_args):
            flag = extra_args[i].split("=")[0]
            if flag in blocked:
                i += 2 if "=" not in extra_args[i] and i+1 < len(extra_args) else i+1
                continue
            if flag in allowed:
                filtered.append(extra_args[i])
                if ("=" not in extra_args[i] and i+1 < len(extra_args)
                        and not extra_args[i+1].startswith("-")):
                    filtered.append(extra_args[i+1]); i += 1
            i += 1
        cmd.extend(filtered)
    # Execute (cwd=script's parent dir so relative imports like `from core.X` work)
    script_dir = str((SKILLS_BASE / skill_info["script"]).parent)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                              cwd=script_dir)
        return {"skill": skill_name, "success": proc.returncode == 0,
                "exit_code": proc.returncode, "output_dir": out_dir,
                "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired:
        return {"skill": skill_name, "success": False, "exit_code": -1,
                "output_dir": out_dir, "stdout": "",
                "stderr": "Skill timed out after 600 seconds."}

# ----------------------------------------------------------------- repro --- #

def repro_bundle(output_dir, command_str, input_files=None):
    """Create a reproducibility bundle in output_dir/repro/."""
    repro = Path(output_dir) / "repro"
    repro.mkdir(parents=True, exist_ok=True)
    cmd_file = repro / "commands.sh"
    cmd_file.write_text(f"#!/usr/bin/env bash\n{command_str}\n", encoding="utf-8")
    os.chmod(cmd_file, 0o755)
    if input_files:
        lines = []
        for fp in input_files:
            p = Path(fp)
            if p.is_file():
                sha = hashlib.sha256(p.read_bytes()).hexdigest()
                lines.append(f"{sha}  {p.name}")
        if lines:
            (repro / "checksums.sha256").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return str(repro)

# ------------------------------------------------------------------ cli --- #

def main():
    pa = argparse.ArgumentParser(prog="runner.py",
                                 description="ClawBio skill runner (MedgeClaw)")
    sub = pa.add_subparsers(dest="command")
    sub.add_parser("list", help="List available skills")
    rp = sub.add_parser("run", help="Run a skill")
    rp.add_argument("skill", help="Skill alias")
    rp.add_argument("--input", dest="input_path")
    rp.add_argument("--output", dest="output_dir")
    rp.add_argument("--demo", action="store_true")
    rp.add_argument("--profile", dest="profile_path")
    args, extra = pa.parse_known_args()

    if args.command == "list":
        list_skills(); return
    if args.command == "run":
        result = run_skill(args.skill, args.input_path, args.output_dir,
                           args.demo, extra or None, args.profile_path)
        # Repro bundle
        cs = f"python3 {SKILLS.get(args.skill,{}).get('script','?')}"
        if args.demo: cs += " --demo"
        elif args.input_path: cs += f" --input {args.input_path}"
        if result["output_dir"]:
            cs += f" --output {result['output_dir']}"
            repro_bundle(result["output_dir"], cs,
                         [args.input_path] if args.input_path else None)
        st = "OK" if result["success"] else "FAILED"
        print(f"\n[{st}] {result['skill']}  (exit {result['exit_code']})")
        if result["output_dir"]: print(f"  output: {result['output_dir']}")
        if result["stdout"]:     print(f"\n--- stdout ---\n{result['stdout'][:2000]}")
        if result["stderr"]:     print(f"\n--- stderr ---\n{result['stderr'][:2000]}")
        sys.exit(0 if result["success"] else 1)
    pa.print_help()

if __name__ == "__main__":
    main()
