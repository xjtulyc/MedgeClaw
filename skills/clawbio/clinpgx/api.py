"""Importable API for the clinpgx skill."""
from __future__ import annotations
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from clawbio.common.report import write_result_json


def run(genotypes: dict[str, str] | None = None, options: dict | None = None) -> dict:
    """Run ClinPGx queries.

    Args:
        genotypes: Not used directly (ClinPGx queries by gene/drug name).
                   Could be used in future to auto-detect relevant genes.
        options: Dict with keys:
            - genes: list[str] — gene symbols to query
            - drugs: list[str] — drug names to query
            - cache_dir: str — cache directory path
            - use_cache: bool — whether to use cache (default True)
            - output_dir: str — if provided, write report files

    Returns:
        Result dict with gene_results, drug_results, summary.
    """
    options = options or {}

    # Import the skill's internal modules
    from clinpgx import ClinPGxClient, query_gene, query_drug

    gene_symbols = options.get("genes", [])
    drug_names = options.get("drugs", [])
    cache_dir = Path(options.get("cache_dir", Path.home() / ".clawbio" / "clinpgx_cache"))
    use_cache = options.get("use_cache", True)

    client = ClinPGxClient(cache_dir=cache_dir, use_cache=use_cache)

    gene_results = []
    for symbol in gene_symbols:
        try:
            result = query_gene(client, symbol)
            gene_results.append(result)
        except Exception as e:
            gene_results.append({"symbol": symbol, "found": False, "error": str(e)})

    drug_results = []
    for name in drug_names:
        try:
            result = query_drug(client, name)
            drug_results.append(result)
        except Exception as e:
            drug_results.append({"name": name, "found": False, "error": str(e)})

    # Build summary
    all_annotations = []
    all_guidelines = []
    all_labels = []
    for gr in gene_results:
        if gr.get("found"):
            all_annotations.extend(gr.get("clinical_annotations", []))
            all_guidelines.extend(gr.get("guidelines", []))
            all_labels.extend(gr.get("drug_labels", []))
    for dr in drug_results:
        if dr.get("found"):
            all_annotations.extend(dr.get("clinical_annotations", []))
            all_labels.extend(dr.get("drug_labels", []))

    result = {
        "gene_results": gene_results,
        "drug_results": drug_results,
        "summary": {
            "genes_queried": len(gene_results),
            "drugs_queried": len(drug_results),
            "annotations_found": len(all_annotations),
            "guidelines_found": len(all_guidelines),
            "labels_found": len(all_labels),
        },
    }

    # Write result.json if output_dir provided
    output_dir = options.get("output_dir")
    if output_dir:
        write_result_json(
            output_dir=output_dir,
            skill="clinpgx",
            version="0.2.0",
            summary=result["summary"],
            data={"gene_results": gene_results, "drug_results": drug_results},
        )

    return result
