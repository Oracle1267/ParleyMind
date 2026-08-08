"""
Schema Linker - merges Reddit + Odds data into team_dossier and computes derived metrics.

Reads:
  - data/social/reddit_sports.json
  - data/odds_snapshot.json
Writes:
  - backend/instance/parlaymind.db (table: team_dossier)
"""

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(
    os.getenv("PARLEY_DB")
    or (Path(__file__).resolve().parents[1] / "instance" / "parlaymind.db")
)
REDDIT_PATH = Path(__file__).resolve().parents[2] / "data" / "social" / "reddit_sports.json"
ODDS_PATH = Path(__file__).resolve().parents[2] / "data" / "odds_snapshot.json"

REQUIRED_COLUMNS = {
    "reddit_sentiment": "REAL DEFAULT 0",
    "p_market_consensus": "REAL DEFAULT 0",
    "p_fanduel_entry": "REAL DEFAULT 0",
    "market_prob": "REAL DEFAULT 0",
    "model_prob": "REAL DEFAULT 0",
    "edge": "REAL DEFAULT 0",
    "value_index": "REAL DEFAULT 0",
}


def normalize(value: str) -> str:
    """Normalize source names for loose cross-source team matching."""
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def _ensure_columns(cur: sqlite3.Cursor) -> None:
    cur.execute("PRAGMA table_info(team_dossier)")
    existing = {row[1] for row in cur.fetchall()}
    for name, declaration in REQUIRED_COLUMNS.items():
        if name not in existing:
            cur.execute(f"ALTER TABLE team_dossier ADD COLUMN {name} {declaration}")


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[LINKER] Invalid JSON in {path}: {exc}")
        return default


def _reddit_team_map(payload: Any) -> dict[str, float]:
    if isinstance(payload, dict):
        by_team = payload.get("ncaab", {}).get("by_team", {})
        if isinstance(by_team, dict):
            return {
                team: float((value or {}).get("avg_sentiment", 0.0))
                for team, value in by_team.items()
                if isinstance(value, dict)
            }
    return {}


def run() -> dict[str, int]:
    print(f"[LINKER] Using DB: {DB_PATH} (exists={DB_PATH.exists()})")
    updated_reddit = 0
    updated_odds = 0

    con = sqlite3.connect(str(DB_PATH), timeout=30)
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA busy_timeout=5000;")
        cur = con.cursor()
        _ensure_columns(cur)

        reddit_data = _load_json(REDDIT_PATH, {})
        reddit_by_team = _reddit_team_map(reddit_data)
        if reddit_by_team:
            for team, sentiment in reddit_by_team.items():
                cur.execute(
                    """
                    UPDATE team_dossier
                    SET reddit_sentiment = ?
                    WHERE LOWER(REPLACE(team_name, ' ', '')) LIKE ?
                    """,
                    (sentiment, f"%{normalize(team)}%"),
                )
                updated_reddit += cur.rowcount
            print(f"[LINKER] Updated {updated_reddit} teams from Reddit sentiment.")
        else:
            print(f"[LINKER] No Reddit team sentiment found at {REDDIT_PATH}.")

        odds = _load_json(ODDS_PATH, [])
        if isinstance(odds, list) and odds:
            for entry in odds:
                if not isinstance(entry, dict):
                    continue
                team = entry.get("team") or entry.get("name")
                if not team:
                    continue

                p_cons = float(entry.get("p_market_consensus", entry.get("market_prob", 0.0)) or 0.0)
                p_fd = float(entry.get("p_fanduel_entry", 0.0) or 0.0)
                market_p = float(entry.get("market_prob", p_cons) or 0.0)
                model_p = float(entry.get("model_prob", 0.0) or 0.0)

                cur.execute(
                    """
                    UPDATE team_dossier
                    SET p_market_consensus = ?,
                        p_fanduel_entry = ?,
                        market_prob = ?,
                        model_prob = ?
                    WHERE LOWER(REPLACE(team_name, ' ', '')) LIKE ?
                    """,
                    (p_cons, p_fd, market_p, model_p, f"%{normalize(team)}%"),
                )
                updated_odds += cur.rowcount
            print(f"[LINKER] Updated {updated_odds} teams from Odds data.")
        else:
            print(f"[LINKER] No odds snapshot entries found at {ODDS_PATH}.")

        cur.execute(
            """
            UPDATE team_dossier
            SET edge = ROUND(model_prob - market_prob, 4),
                value_index = ROUND(ABS(model_prob - market_prob) * (1 + ABS(reddit_sentiment)), 4)
            WHERE model_prob IS NOT NULL AND market_prob IS NOT NULL
            """
        )

        con.commit()
    finally:
        con.close()

    total = updated_reddit + updated_odds
    print(f"[LINKER] Schema linking complete: {total} team updates.")
    return {"reddit": updated_reddit, "odds": updated_odds, "total": total}


if __name__ == "__main__":
    run()
