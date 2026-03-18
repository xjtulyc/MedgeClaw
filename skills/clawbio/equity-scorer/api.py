"""Importable API for the equity-scorer skill.

Unlike other ClawBio skills that accept a genotype dict, the equity-scorer
operates on multi-sample VCF files or ancestry CSV files.  This thin
wrapper exposes a ``run()`` function with a consistent interface so
that the bio-orchestrator can invoke it programmatically.

Usage::

    from skills.equity_scorer.api import run

    result = run("/path/to/populations.vcf", options={"pop_map": "map.csv"})
    print(result["summary"]["heim_score"])
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

# Ensure project root is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Also ensure the skill directory is importable (for equity_scorer module)
_SKILL_DIR = Path(__file__).resolve().parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from equity_scorer import run_vcf_pipeline, run_csv_pipeline, DEFAULT_WEIGHTS


def run(input_path: str, options: dict | None = None) -> dict[str, Any]:
    """Run equity scoring on a VCF or ancestry CSV.

    Args:
        input_path: Path to VCF (.vcf) or ancestry CSV (.csv/.tsv) file.
        options: Optional configuration dict with keys:
            - ``pop_map``: Path to population map CSV (only for VCF inputs).
            - ``output``: Output directory path (default: temp directory).
            - ``weights``: Tuple or comma-separated string of 4 HEIM weights
              (RI, HB, FC, GS).  Default: ``(0.35, 0.25, 0.20, 0.20)``.

    Returns:
        dict with keys:
            - ``heim_result``: Full HEIM score result dict.
            - ``summary``: Abbreviated summary with heim_score, rating,
              n_samples, n_populations.
            - ``output_dir``: Path to the output directory (str).
    """
    options = options or {}
    input_path = Path(input_path)

    # Parse output directory
    output_dir = Path(options.get("output", tempfile.mkdtemp(prefix="equity_")))

    # Parse weights
    weights = options.get("weights", DEFAULT_WEIGHTS)
    if isinstance(weights, str):
        weights = tuple(float(w) for w in weights.split(","))
    weights = tuple(weights)

    # Detect file type and run appropriate pipeline
    suffix = input_path.suffix.lower()
    if suffix in (".vcf",):
        pop_map_path = Path(options["pop_map"]) if options.get("pop_map") else None
        heim_result = run_vcf_pipeline(input_path, pop_map_path, output_dir, weights)
    elif suffix in (".csv", ".tsv"):
        heim_result = run_csv_pipeline(input_path, output_dir, weights)
    else:
        raise ValueError(
            "Unsupported file type '%s'. Provide a .vcf or .csv file." % suffix
        )

    return {
        "heim_result": heim_result,
        "summary": {
            "heim_score": heim_result["heim_score"],
            "rating": heim_result["rating"],
            "n_samples": heim_result["n_samples"],
            "n_populations": heim_result["n_populations"],
        },
        "output_dir": str(output_dir),
    }
