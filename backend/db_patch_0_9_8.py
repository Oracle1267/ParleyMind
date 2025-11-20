# backend/db_patch_0_9_8.py
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "instance" / "parlaymind.db"

ADDS = [
    ("ALTER TABLE team_dossier ADD COLUMN momentum_score REAL;", "momentum_score"),
    ("ALTER TABLE team_dossier ADD COLUMN efficiency_margin REAL;", "efficiency_margin"),
    ("ALTER TABLE team_dossier ADD COLUMN reddit_sentiment REAL;", "reddit_sentiment"),
    ("ALTER TABLE team_dossier ADD COLUMN team_url TEXT;", "team_url"),
]

def column_exists(cur, table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    for sql, col in ADDS:
        try:
            if not column_exists(cur, "team_dossier", col):
                cur.execute(sql)
                print(f"✅ Added {col}")
            else:
                print(f"↪️  {col} already exists")
        except sqlite3.OperationalError as e:
            print(f"⚠️  {col}: {e}")
    con.commit()
    con.close()
    print("Done.")

if __name__ == "__main__":
    main()
