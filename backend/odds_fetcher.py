"""
Odds Fetcher — retrieves live NCAAB moneyline odds and extracts:
  - p_market_consensus : consensus implied probability across all available books
  - p_fanduel_entry    : FanDuel implied probability (if FanDuel listed)

Writes JSON list to: data/odds_snapshot.json
Each item: { "team": str, "p_market_consensus": float, "p_fanduel_entry": float }

Notes:
- Uses The Odds API (v4). Set ODDS_API_KEY in env.
- Regions: US, Markets: h2h (moneyline), Odds: american
"""

import os
import json
from pathlib import Path
from collections import defaultdict

import requests

API_KEY = os.getenv("ODDS_API_KEY", "")
BASE_URL = "https://api.the-odds-api.com/v4/sports/basketball_ncaab/odds"
OUTFILE = Path(__file__).resolve().parents[2] / "data" / "odds_snapshot.json"

def american_to_prob(odds: int | float) -> float:
    """Convert American odds to implied probability in [0,1]."""
    try:
        odds = float(odds)
    except Exception:
        return 0.0
    if odds == 0:
        return 0.0
    if odds > 0:
        return 100.0 / (odds + 100.0)
    return (-odds) / ((-odds) + 100.0)

def run() -> list[dict]:
    print("[AGENT] Starting Odds Fetcher (NCAAB h2h)...")
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american",
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        games = r.json()
    except Exception as e:
        print(f"[AGENT] ⚠️ Failed to fetch odds: {e}")
        return []

    # Aggregate implied probabilities per team across all books (consensus)
    # Also capture FanDuel specifically when present
    # games[*].bookmakers[*].markets (key='h2h').outcomes[*] -> name, price
    team_probs_all_books = defaultdict(list)   # team -> [prob_from_book, ...]
    team_prob_fanduel   = {}                   # team -> prob_from_fanduel

    for g in games or []:
        for bm in (g.get("bookmakers") or []):
            bm_key = (bm.get("key") or "").lower()
            # find the h2h market
            for mk in (bm.get("markets") or []):
                if (mk.get("key") or "").lower() != "h2h":
                    continue
                for outcome in (mk.get("outcomes") or []):
                    team = outcome.get("name")
                    price = outcome.get("price")
                    if not team or not isinstance(price, (int, float)):
                        continue
                    p = american_to_prob(price)
                    if p <= 0 or p >= 1:
                        continue
                    team_probs_all_books[team].append(p)
                    if bm_key == "fanduel":
                        team_prob_fanduel[team] = p

    # Build simplified list (consensus + FanDuel-only)
    simplified: list[dict] = []
    for team, plist in team_probs_all_books.items():
        if not plist:
            continue
        p_consensus = sum(plist) / len(plist)
        p_fd = team_prob_fanduel.get(team, 0.0)
        simplified.append({
            "team": team,
            "p_market_consensus": round(p_consensus, 4),
            "p_fanduel_entry": round(p_fd, 4),
            # Legacy fields kept for backward compatibility with older linkers:
            "market_prob": round(p_consensus, 4),
            "model_prob": 0.0,
        })

    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    OUTFILE.write_text(json.dumps(simplified, indent=2), encoding="utf-8")
    print(f"[AGENT] ✅ Saved odds snapshot: {len(simplified)} entries -> {OUTFILE}")
    return simplified

if __name__ == "__main__":
    run()
