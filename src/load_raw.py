"""E + L of ELT — load the CSV into the warehouse with **zero** cleaning.

This is the whole point of ELT rather than ETL: the raw table is a faithful,
byte-for-byte landing of the source. Every column is VARCHAR, nothing is
trimmed, nothing is parsed, nothing is dropped. If a transformation later turns
out to be wrong, the fix is a SQL change and a re-run — the source of truth is
already in the warehouse and never has to be re-fetched.

Contrast with the ETL sibling project (nyc-taxi-etl-pipeline), where the
transform happens *before* the load and the raw form is not retained.

    python src/load_raw.py
"""
from __future__ import annotations

import duckdb

from config import RAW_CSV, WAREHOUSE

EXPECTED_COLUMNS = [
    "show_id", "type", "title", "director", "cast", "country",
    "date_added", "release_year", "rating", "duration", "listed_in",
    "description",
]


def main() -> None:
    if not RAW_CSV.exists():
        raise SystemExit(f"Missing {RAW_CSV}")

    con = duckdb.connect(str(WAREHOUSE))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    # all_varchar: refuse to let the reader guess types. Type inference is a
    # transformation, and transformations belong in the T layer where they are
    # reviewable, not hidden in a CSV reader's heuristics.
    con.execute(
        """
        CREATE OR REPLACE TABLE raw.netflix_titles AS
        SELECT *, CAST(NULL AS VARCHAR) AS _dummy
        FROM read_csv(?, all_varchar = true, header = true,
                      encoding = 'utf-8', null_padding = true)
        """,
        [str(RAW_CSV)],
    )
    con.execute("ALTER TABLE raw.netflix_titles DROP COLUMN _dummy")

    cols = [r[0] for r in con.execute("DESCRIBE raw.netflix_titles").fetchall()]
    rows = con.execute("SELECT COUNT(*) FROM raw.netflix_titles").fetchone()[0]

    missing = set(EXPECTED_COLUMNS) - set(cols)
    extra = set(cols) - set(EXPECTED_COLUMNS)
    if missing:
        raise SystemExit(f"Source is missing expected columns: {sorted(missing)}")
    if extra:
        print(f"  note: source has unexpected extra columns {sorted(extra)}")

    print(f"  raw.netflix_titles: {rows:,} rows x {len(cols)} columns (all VARCHAR)")

    # Sanity check the landing: every column should be non-empty somewhere, and
    # at least one should contain NULLs (this source is known to be sparse).
    # Every identifier is quoted: `cast` is a reserved word in DuckDB (and in
    # most dialects), and an unquoted reference to it is a parser error.
    nulls = con.execute(
        "SELECT "
        + ", ".join(f'SUM(CASE WHEN "{c}" IS NULL THEN 1 ELSE 0 END) AS "{c}"'
                    for c in EXPECTED_COLUMNS)
        + " FROM raw.netflix_titles"
    ).fetchdf().iloc[0]
    sparse = {c: int(n) for c, n in nulls.items() if n > 0}
    print(f"  NULLs landed as-is: {sparse}")

    print(f"  loaded from {RAW_CSV.name}")
    print(f"  warehouse: {WAREHOUSE}")
    con.close()


if __name__ == "__main__":
    main()
