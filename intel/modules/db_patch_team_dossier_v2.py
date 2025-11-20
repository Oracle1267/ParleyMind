"""
db_patch_team_dossier_v2.py — idempotent migration for new team_dossier fields.

Run once at startup (safe to re-run).
"""
import sqlite3
from typing import Iterable

ADDED_COLUMNS = [
    # basic stats
    ("wins", "INTEGER DEFAULT 0"),
    ("losses", "INTEGER DEFAULT 0"),
    ("ppg", "REAL DEFAULT 0"),
    ("opp_ppg", "REAL DEFAULT 0"),
    ("coach", "TEXT DEFAULT ''"),
    ("pace", "REAL DEFAULT 0"),
    # form & analytics
    ("form_last5_net", "REAL DEFAULT 0"),
    ("beat_market_last5", "REAL DEFAULT 0"),
    ("rolling_z", "REAL DEFAULT 0"),
    ("confidence_v2", "REAL DEFAULT 0"),
    ("value_index_v2", "REAL DEFAULT 0"),
    # staking
    ("kelly_fraction_bound", "REAL DEFAULT 0"),
    ("stake_units", "REAL DEFAULT 0"),
    # explainability
    ("signals_json", "TEXT DEFAULT ''"),
    # market tracking
    ("p_market_consensus", "REAL DEFAULT 0"),
    ("p_fanduel_entry", "REAL DEFAULT 0"),
    ("p_kalshi_entry", "REAL DEFAULT 0"),
    ("p_model_entry", "REAL DEFAULT 0"),
    ("edge_entry", "REAL DEFAULT 0"),
    ("clv_entry", "REAL DEFAULT 0")
]

def add_column_if_missing(cur: sqlite3.Cursor, table: str, col: str, decl: str) -> None:
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    if col not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")

def run(db_path: str = "backend/instance/parlaymind.db") -> None:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        for col, decl in ADDED_COLUMNS:
            add_column_if_missing(cur, "team_dossier", col, decl)
        con.commit()
    finally:
        con.close()

if __name__ == "__main__":
    run()
