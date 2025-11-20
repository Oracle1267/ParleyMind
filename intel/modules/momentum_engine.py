"""
momentum_engine.py — compute short-term form & z-scores for each team.

Public function:
    compute(db_path="backend/instance/parlaymind.db")
Writes: form_last5_net, beat_market_last5, rolling_z
"""
import sqlite3
import math

def _z(x: float, mu: float, sigma: float) -> float:
    if sigma <= 1e-9:
        return 0.0
    return (x - mu) / sigma

def compute(db_path: str = "backend/instance/parlaymind.db") -> int:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    # Placeholder: derive form from (ppg - opp_ppg); real version should read last-5 games
    cur.execute("SELECT id, ppg, opp_ppg FROM team_dossier")
    rows = cur.fetchall()
    diffs = [ppg - opp for _, ppg, opp in rows]
    if diffs:
        mu = sum(diffs) / len(diffs)
        var = sum((d - mu)**2 for d in diffs) / max(1, (len(diffs)-1))
        sigma = math.sqrt(var)
    else:
        mu = 0.0; sigma = 1.0
    updated = 0
    for (tid, ppg, opp) in rows:
        form = (ppg - opp)  # stand-in for last-5 net margin
        beat_market = 0.0   # TODO: compute from odds snapshots vs actuals
        rz = _z(form, mu, sigma)
        cur.execute("""UPDATE team_dossier
                       SET form_last5_net=?, beat_market_last5=?, rolling_z=?
                       WHERE id=?""", (form, beat_market, rz, tid))
        updated += 1
    con.commit()
    con.close()
    return updated

if __name__ == "__main__":
    print("Updated rows:", compute())
