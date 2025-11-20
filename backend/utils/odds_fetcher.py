"""
ParleyMind Odds Fetcher
-----------------------
Retrieves and simplifies live odds data from The Odds API.

Outputs:
  data/odds_snapshot.json  (used by schema_linker + intel_cycle)
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# --- Load .env file ---
load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ ODDS_API_KEY not found in .env file")

BASE_URL = "https://api.the-odds-api.com/v4/sports"
OUTFILE = Path(__file__).resolve().parents[2] / "data" / "odds_snapshot.json"


# ----------------------------------------------------------------------
# Utility
# ----------------------------------------------------------------------
def _fetch_odds(sport_key: str):
    """Generic odds fetcher for any supported sport."""
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american",
    }
    url = f"{BASE_URL}/{sport_key}/odds"
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[⚠️ OddsAPI] Fetch failed for {sport_key}: {e}")
        return []


def _simplify_odds(raw_games):
    """
    Simplify raw API odds into per-team implied probabilities.
    """
    simplified = []
    for game in raw_games:
        bookmakers = game.get("bookmakers", [])
        if not bookmakers:
            continue

        # pick one book, e.g., Fanduel preferred
        bookmaker = next((b for b in bookmakers if b.get("key") == "fanduel"), bookmakers[0])

        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue

            for o in market.get("outcomes", []):
                name = o.get("name")
                price = o.get("price")

                if not name or price is None:
                    continue

                # Convert American odds to implied probability
                try:
                    if price > 0:
                        prob = 100 / (price + 100)
                    else:
                        prob = abs(price) / (abs(price) + 100)
                except Exception:
                    prob = 0.5

                simplified.append({
                    "team": name,
                    "market_prob": round(prob, 4),
                    "model_prob": 0.0,  # Placeholder; filled by your ML model later
                })
    return simplified


# ----------------------------------------------------------------------
# Sport-Specific Functions
# ----------------------------------------------------------------------
def get_ncaab_odds():
    """Men’s College Basketball odds"""
    raw = _fetch_odds("basketball_ncaab")
    simplified = _simplify_odds(raw)
    _save_snapshot(simplified)
    return simplified


def get_wncaab_odds():
    """Women’s College Basketball odds"""
    raw = _fetch_odds("basketball_ncaaw")
    simplified = _simplify_odds(raw)
    _save_snapshot(simplified)
    return simplified


def get_nfl_odds():
    """NFL odds"""
    raw = _fetch_odds("americanfootball_nfl")
    simplified = _simplify_odds(raw)
    _save_snapshot(simplified)
    return simplified


def get_cfb_odds():
    """College Football odds"""
    raw = _fetch_odds("americanfootball_ncaaf")
    simplified = _simplify_odds(raw)
    _save_snapshot(simplified)
    return simplified


def get_nhl_odds():
    """NHL odds"""
    raw = _fetch_odds("icehockey_nhl")
    simplified = _simplify_odds(raw)
    _save_snapshot(simplified)
    return simplified


def get_volleyball_odds():
    """Placeholder — Odds API doesn’t offer NCAA volleyball"""
    print("[INFO] Volleyball odds unavailable; returning empty set.")
    return []


# ----------------------------------------------------------------------
# Persistence
# ----------------------------------------------------------------------
def _save_snapshot(simplified):
    """Write simplified snapshot to disk."""
    try:
        OUTFILE.parent.mkdir(parents=True, exist_ok=True)
        OUTFILE.write_text(json.dumps(simplified, indent=2), encoding="utf-8")
        print(f"[AGENT] ✅ Saved {len(simplified)} entries to {OUTFILE}")
    except Exception as e:
        print(f"[⚠️ OddsAPI] Failed to save snapshot: {e}")


# ----------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------
def run():
    """Default entrypoint (NCAAB)"""
    print("[AGENT] Starting Odds Fetcher (NCAAB default)...")
    data = get_ncaab_odds()
    print(f"[AGENT] Retrieved {len(data)} odds entries.")
    return data


if __name__ == "__main__":
    run()
