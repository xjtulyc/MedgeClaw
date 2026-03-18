"""ClawBio common utilities — shared parsers, profiles, reports, checksums."""

from clawbio.common.parsers import (
    detect_format,
    parse_genetic_file,
    GenotypeRecord,
)
from clawbio.common.checksums import sha256_file, sha256_hex
from clawbio.common.report import (
    generate_report_header,
    generate_report_footer,
    DISCLAIMER,
)
from clawbio.common.profile import PatientProfile
from clawbio.common.html_report import HtmlReportBuilder, write_html_report

# scrna_io has heavy dependencies (numpy, scipy, anndata) — lazy import
def __getattr__(name):
    _scrna_names = {
        "compute_input_checksum",
        "detect_processed_input_reason",
        "load_count_adata",
        "load_10x_mtx_data",
        "resolve_input_source",
    }
    if name in _scrna_names:
        from clawbio.common import scrna_io
        return getattr(scrna_io, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "detect_format",
    "parse_genetic_file",
    "GenotypeRecord",
    "sha256_file",
    "sha256_hex",
    "generate_report_header",
    "generate_report_footer",
    "DISCLAIMER",
    "PatientProfile",
    "HtmlReportBuilder",
    "write_html_report",
    "compute_input_checksum",
    "detect_processed_input_reason",
    "load_count_adata",
    "load_10x_mtx_data",
    "resolve_input_source",
]
