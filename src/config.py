"""Paths and layer ordering for the Netflix ELT.

The SQL layers execute in the order listed in `LAYERS`. Within a layer, files
run alphabetically. That is the simplest dependency model that works: the layer
boundaries carry the ordering, so no model in `marts/` can accidentally depend
on another model in `marts/`.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
WAREHOUSE = PROCESSED_DIR / "netflix.duckdb"

SQL_DIR = ROOT / "sql"
ANALYSIS_SQL_DIR = SQL_DIR / "analysis"
TESTS_DIR = SQL_DIR / "tests"

OUT_DIR = ROOT / "outputs"
RESULTS_DIR = OUT_DIR / "results"
CHARTS_DIR = OUT_DIR / "charts"

RAW_CSV = RAW_DIR / "netflix_titles.csv"

# Executed in this order. Each entry is (folder, materialisation).
LAYERS: list[tuple[str, str]] = [
    ("staging", "view"),        # cheap, always fresh, no storage cost
    ("intermediate", "table"),  # the unnests are expensive; materialise once
    ("marts", "table"),         # what analysts and BI tools read
]

for _d in (PROCESSED_DIR, RESULTS_DIR, CHARTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)
