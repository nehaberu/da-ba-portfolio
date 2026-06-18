"""
Run every .sql file in queries/ against retail.db and pretty-print the results.

Usage:
    python data/generate_data.py   # once, to build retail.db
    python run_queries.py          # run all analysis queries
    python run_queries.py 04       # run only the query whose filename starts with 04
"""
import os
import sys
import sqlite3
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "retail.db")
QUERY_DIR = os.path.join(HERE, "queries")

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)


def split_statements(sql_text: str):
    """Split a file into individual statements, ignoring comment-only chunks."""
    statements = []
    for chunk in sql_text.split(";"):
        # keep a statement only if it has at least one non-comment, non-blank line
        has_code = any(
            line.strip() and not line.strip().startswith("--")
            for line in chunk.splitlines()
        )
        if has_code:
            statements.append(chunk.strip())
    return statements


def main() -> None:
    if not os.path.exists(DB_PATH):
        sys.exit("retail.db not found. Run `python data/generate_data.py` first.")

    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    files = sorted(f for f in os.listdir(QUERY_DIR)
                   if f.endswith(".sql") and f.startswith(prefix))

    conn = sqlite3.connect(DB_PATH)
    for fname in files:
        with open(os.path.join(QUERY_DIR, fname)) as fh:
            sql_text = fh.read()
        print("\n" + "=" * 70)
        print(f"FILE: {fname}")
        print("=" * 70)
        for stmt in split_statements(sql_text):
            df = pd.read_sql_query(stmt, conn)
            print(df.to_string(index=False))
            print("-" * 70)
    conn.close()


if __name__ == "__main__":
    main()
