"""Importable API for the gwas-prs skill.

Allows other skills and the orchestrator to call PRS calculation
programmatically without shelling out to the CLI.

Usage:
    import importlib, sys, pathlib
    _skill_dir = pathlib.Path("<project_root>/skills/gwas-prs")
    if str(_skill_dir) not in sys.path:
        sys.path.insert(0, str(_skill_dir))
    from api import run

    result = run(
        genotypes={"rs7903146": "CT", "rs1801282": "CG", ...},
        options={"pgs_id": "PGS000013", "build": "GRCh37"},
    )
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# The skill directory uses a hyphen ("gwas-prs") which is not a valid
# Python package name, so we load the engine module via importlib.
_SKILL_DIR = Path(__file__).resolve().parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

import gwas_prs as _engine  # noqa: E402  (sibling module in same dir)


def run(genotypes: dict[str, str], options: dict | None = None) -> dict:
    """Run PRS calculation on a genotype dict.

    Args:
        genotypes: Mapping of rsid -> genotype string (e.g. {"rs7903146": "CT"}).
        options: Optional settings dict. Recognised keys:
            - pgs_id (str): Specific PGS Catalog score ID (e.g. "PGS000013").
                            If omitted, all curated scores are used.
            - build (str): Genome build, "GRCh37" (default) or "GRCh38".
            - min_overlap (float): Minimum SNP overlap fraction (default 0.5).

    Returns:
        Dict with keys:
            - results: list of per-score dicts (pgs_id, trait, raw_score,
              percentile, risk_category, overlap_fraction, ...)
            - scores_calculated: int
            - disclaimer: str
    """
    options = options or {}
    build = options.get("build", "GRCh37")
    pgs_id = options.get("pgs_id")
    min_overlap = options.get("min_overlap", 0.5)

    skill_dir = Path(__file__).resolve().parent
    data_dir = skill_dir / "data"

    # Determine which scoring files to use
    scoring_entries: list[dict] = []

    if pgs_id:
        pgs_id = pgs_id.strip().upper()
        if not pgs_id.startswith("PGS"):
            pgs_id = "PGS" + pgs_id.lstrip("0")
        ids_to_score = [pgs_id]
    else:
        # Default: all curated scores
        ids_to_score = list(_engine.CURATED_SCORES.keys())

    for sid in ids_to_score:
        scoring_path = data_dir / f"{sid}_hmPOS_{build}.txt"
        scoring_path_gz = data_dir / f"{sid}_hmPOS_{build}.txt.gz"
        if scoring_path.exists():
            fpath = scoring_path
        elif scoring_path_gz.exists():
            fpath = scoring_path_gz
        else:
            continue

        meta = _engine.CURATED_SCORES.get(sid, {})
        scoring_entries.append({
            "pgs_id": sid,
            "trait": meta.get("trait", "Unknown"),
            "filepath": fpath,
            "metadata": {
                "publication": meta.get("publication", ""),
                "variants_count": meta.get("variants_count", 0),
            },
        })

    # Score each entry
    all_results: list[dict] = []
    for sf in scoring_entries:
        scoring_variants = _engine.parse_scoring_file(sf["filepath"])
        if not scoring_variants:
            continue

        prs = _engine.calculate_prs(genotypes, scoring_variants)

        if prs["overlap_fraction"] < min_overlap:
            continue

        pct_info = _engine.estimate_percentile(
            prs["raw_score"], sf["pgs_id"], scoring_variants
        )

        all_results.append({
            "pgs_id": sf["pgs_id"],
            "trait": sf["trait"],
            "raw_score": prs["raw_score"],
            "variants_used": prs["variants_used"],
            "variants_total": prs["variants_total"],
            "overlap_fraction": prs["overlap_fraction"],
            "percentile": pct_info["percentile"],
            "risk_category": pct_info["risk_category"],
            "z_score": pct_info["z_score"],
            "method": pct_info["method"],
            "reference_population": pct_info.get("reference_population"),
        })

    return {
        "results": all_results,
        "scores_calculated": len(all_results),
        "disclaimer": _engine.DISCLAIMER,
    }
