"""
stats_enricher.py — populate baseline team stats into team_dossier.

This stub expects you already have team base URLs or a CSV mapping.
Pluggable fetchers live here; for v1.1 you can hardwire TeamRankings or
official site snapshots.

Public function:
    enrich(db_path="backend/instance/parlaymind.db")

Outputs: updates team_dossier columns: wins, losses, ppg, opp_ppg, coach, pace.
"""
import sqlite3
from typing import Dict, Tuple

def _fake_stats_source(team_name: str) -> Tuple[int,int,float,float,str,float]:
    """
    Temporary placeholder: returns (wins, losses, ppg, opp_ppg, coach, pace).
    Replace with real scraper or API call.
    """
    # simple deterministic toy values for smoke tests
    wins = len(team_name) % 25
    losses = (len(team_name) * 2) % 25
    ppg = 65.0 + (len(team_name) % 10)
    opp_ppg = 62.0 + (len(team_name) % 8)
    coach = "TBD"
    pace = 68.5
    return wins, losses, ppg, opp_ppg, coach, pace

def enrich(db_path: str = "backend/instance/parlaymind.db") -> int:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT id, team_name FROM team_dossier")
    rows = cur.fetchall()
    updated = 0
    for tid, name in rows:
        wins, losses, ppg, opp_ppg, coach, pace = _fake_stats_source(name)
        cur.execute("""UPDATE team_dossier
                       SET wins=?, losses=?, ppg=?, opp_ppg=?, coach=?, pace=?
                       WHERE id=?""", (wins, losses, ppg, opp_ppg, coach, pace, tid))
        updated += 1
    con.commit()
    con.close()
    return updated

if __name__ == "__main__":
    print("Updated rows:", enrich())
