"""
Schema Linker — merges Reddit + Odds data into team_dossier and computes derived metrics.

Reads:
  - data/social/reddit_sports.json
  - data/odds_snapshot.json
Writes:
  - backend/instance/parlaymind.db (table: team_dossier)

What it updates:
  - reddit_sentiment                         (from reddit cache)
  - p_market_consensus, p_fanduel_entry      (from odds snapshot)
  - legacy market_prob/model_prob            (kept for backward compatibility)
  - legacy edge/value_index (based on legacy fields, unchanged)
"""

# --- top of file (replace DB_PATH line) ---
import os, sqlite3, json, re
from pathlib import Path

DB_PATH = Path(os.getenv("PARLEY_DB") or (Path(__file__).resolve().parents[1] / "instance" / "parlaymind.db"))
REDDIT_PATH = Path(__file__).resolve().parents[2] / "data" / "social" / "reddit_sports.json"
ODDS_PATH   = Path(__file__).resolve().parents[2] / "data" / "odds_snapshot.json"

def run():
    print(f"[LINKER] Using DB: {DB_PATH} (exists={DB_PATH.exists()})")
    con = sqlite3.connect(str(DB_PATH), timeout=30, isolation_level=None)  # autocommit
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA busy_timeout=5000;")
        cur = con.cursor()
        # (the rest of your function stays the same)


    # --- Merge Reddit sentiment ------------------------------------------------
    if REDDIT_PATH.exists():
        reddit = json.loads(REDDIT_PATH.read_text(encoding="utf-8"))
        ncaab = reddit.get("ncaab", {}).get("by_team", {})
        for team, val in ncaab.items():
            sentiment = float(val.get("avg_sentiment", 0.0))
            cur.execute("""
                UPDATE team_dossier
                SET reddit_sentiment = ?
                WHERE LOWER(REPLACE(team_name, ' ', '')) LIKE ?
            """, (sentiment, f"%{normalize(team)}%"))
            if cur.rowcount:
                updated_reddit += 1
        print(f"[LINKER] ✅ Updated {updated_reddit} teams from Reddit sentiment.")
    else:
        print(f"[LINKER] ⚠️ Reddit file not found: {REDDIT_PATH}")

    # --- Merge Odds (consensus + FanDuel) -------------------------------------
    if ODDS_PATH.exists():
        odds = json.loads(ODDS_PATH.read_text(encoding="utf-8"))
        for entry in odds:
            team = entry.get("team") or entry.get("name")
            if not team:
                continue
            # New fields (preferred)
            p_cons = float(entry.get("p_market_consensus", 0.0))
            p_fd   = float(entry.get("p_fanduel_entry", 0.0))
            # Legacy (kept for backward support)
            market_p = float(entry.get("market_prob", p_cons))
            model_p  = float(entry.get("model_prob", 0.0))

            cur.execute("""
                UPDATE team_dossier
                SET 
                    p_market_consensus = ?,
                    p_fanduel_entry    = ?,
                    -- legacy continuity:
                    market_prob        = ?,
                    model_prob         = ?
                WHERE LOWER(REPLACE(team_name, ' ', '')) LIKE ?
            """, (p_cons, p_fd, market_p, model_p, f"%{normalize(team)}%"))
            if cur.rowcount:
                updated_odds += 1
        print(f"[LINKER] ✅ Updated {updated_odds} teams from Odds data.")
    else:
        print(f"[LINKER] ⚠️ Odds file not found: {ODDS_PATH}")

    # --- Legacy edge/value_index (unchanged for backward compatibility) -------
    print("[LINKER] 🧮 Computing legacy edges and value indices...")
    cur.execute("""
        UPDATE team_dossier
        SET edge = ROUND(model_prob - market_prob, 4),
            value_index = ROUND(ABS(model_prob - market_prob) * (1 + ABS(reddit_sentiment)), 4)
        WHERE model_prob IS NOT NULL AND market_prob IS NOT NULL;
    """)

    con.commit()
    con.close()
    print(f"[LINKER] === Schema linking complete: {updated_reddit + updated_odds} teams updated ===")

if __name__ == "__main__":
    run()
