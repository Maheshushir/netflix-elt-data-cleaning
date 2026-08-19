"""T of ELT: execute the SQL layers in order, then run the test suite.

A small reimplementation of what dbt does: models are plain .sql
files that each SELECT, and the runner wraps them in CREATE OR REPLACE. Tests
are .sql files that return the *offending* rows, so an empty result is a pass.

    python src/run_elt.py            # build + test
    python src/run_elt.py --no-test  # build only
    python src/run_elt.py --test     # test only, against the existing build
"""
from __future__ import annotations

import argparse
import time

import duckdb

from config import LAYERS, SQL_DIR, TESTS_DIR, WAREHOUSE


def build(con: duckdb.DuckDBPyConnection) -> list[tuple[str, str, int, float]]:
    built: list[tuple[str, str, int, float]] = []

    for folder, materialisation in LAYERS:
        layer_dir = SQL_DIR / folder
        files = sorted(layer_dir.glob("*.sql"))
        if not files:
            continue

        print(f"\n[{folder}]  ({materialisation})")
        for path in files:
            model = path.stem
            sql = path.read_text(encoding="utf-8").rstrip().rstrip(";")
            started = time.time()
            con.execute(
                f"CREATE OR REPLACE {materialisation.upper()} {model} AS\n{sql}"
            )
            rows = con.execute(f"SELECT COUNT(*) FROM {model}").fetchone()[0]
            elapsed = time.time() - started
            print(f"  {model:<26} {rows:>8,} rows   {elapsed:5.2f}s")
            built.append((folder, model, rows, elapsed))

    return built


def test(con: duckdb.DuckDBPyConnection) -> tuple[int, int]:
    files = sorted(TESTS_DIR.glob("*.sql"))
    if not files:
        print("\nNo tests found.")
        return 0, 0

    print(f"\n[tests]  {len(files)} assertions")
    passed = failed = 0

    for path in files:
        name = path.stem
        sql = path.read_text(encoding="utf-8").rstrip().rstrip(";")
        try:
            offending = con.execute(sql).fetchdf()
        except Exception as exc:                       # a broken test is a failure
            print(f"  FAIL  {name:<28} query error: {exc}")
            failed += 1
            continue

        if len(offending) == 0:
            print(f"  pass  {name}")
            passed += 1
        else:
            print(f"  FAIL  {name:<28} {len(offending)} offending row(s)")
            print(offending.head(5).to_string(index=False, max_colwidth=40))
            failed += 1

    return passed, failed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-test", action="store_true")
    ap.add_argument("--test", action="store_true", help="run tests only")
    args = ap.parse_args()

    if not WAREHOUSE.exists():
        raise SystemExit("No warehouse. Run: python src/load_raw.py")

    con = duckdb.connect(str(WAREHOUSE))
    started = time.time()

    try:
        if not args.test:
            built = build(con)
            total_rows = sum(b[2] for b in built)
            print(f"\nBuilt {len(built)} models, {total_rows:,} rows total, "
                  f"in {time.time()-started:.2f}s")

        if not args.no_test:
            passed, failed = test(con)
            print(f"\n{passed} passed, {failed} failed")
            if failed:
                raise SystemExit(
                    f"\n{failed} test(s) failed, so the build is not trustworthy."
                )
            print("\nAll assertions hold. Next: python src/analyze.py")
    finally:
        con.close()


if __name__ == "__main__":
    main()
