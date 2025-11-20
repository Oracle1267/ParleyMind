# excerpt: backend/ncaab_dossier_builder.py
import sqlite3, json
from pathlib import Path

DB = Path(__file__).parent / "instance" / "parlaymind.db"
DATA = Path(__file__).parent.parent / "data"

def load_sentiment():
    fp = DATA / "social" / "reddit_sports.json"
    if not fp.exists(): return {}
    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return {}
    # Expect: { "Team Name": {"mentions": int, "sentiment": float}, ... }
    return {k: v.get("sentiment", 0.0) for k, v in obj.items()}

def load_team_urls():
    fp = DATA / "team_stats_links.csv"
    if not fp.exists(): return {}
    out = {}
    for line in fp.read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip(): continue
        team, url = line.split(",", 1)
        out[team.strip('" ')] = url.strip('" ')
    return out

def calc_momentum(eff_margin: float, sentiment: float) -> float:
    # Simple blend: weight efficiency more, sentiment as accelerator
    return round(0.7 * eff_margin + 0.3 * (sentiment * 10), 3)

def upsert_dossier(rows):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys=ON;")
    for r in rows:
        cur.execute("""
        INSERT INTO team_dossier(team_name, efficiency_margin, reddit_sentiment, momentum_score, team_url)
        VALUES (?,?,?,?,?)
        ON CONFLICT(team_name) DO UPDATE SET
          efficiency_margin=excluded.efficiency_margin,
          reddit_sentiment=excluded.reddit_sentiment,
          momentum_score=excluded.momentum_score,
          team_url=excluded.team_url;
        """, (r["team_name"], r["efficiency_margin"], r["reddit_sentiment"], r["momentum_score"], r["team_url"]))
    con.commit(); con.close()

def build():
    # TODO: pull real efficiency margin from TeamRankings scraper cache
    sentiment = load_sentiment()
    urls = load_team_urls()
    # Minimal join: rely on existing ncaab_team master
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("SELECT name, 0.0 FROM ncaab_team;")
    rows = []
    for team_value, eff in cur.fetchall():
        team_name = team_value.strip()
        eff_margin = float(eff or 0.0)
        sent = float(sentiment.get(team_name, 0.0))
        url = urls.get(team_name, "")
        momentum = calc_momentum(eff_margin, sent)
        rows.append({
            "team_name": team_name,
            "efficiency_margin": eff_margin,
            "reddit_sentiment": sent,
            "momentum_score": momentum,
            "team_url": url
        })

    con.close()
    upsert_dossier(rows)
    print(f"✅ Dossiers updated: {len(rows)}")

if __name__ == "__main__":
    build()
