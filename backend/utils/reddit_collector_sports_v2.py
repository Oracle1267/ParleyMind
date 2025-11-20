"""
Reddit Sports Collector (NHL + NCAAB)
-------------------------------------
- Uses Reddit's live API via PRAW (no Pushshift).
- Scans selected subreddits for the last N hours.
- Filters posts by simple team-keyword matching.
- Produces a compact cache JSON ParleyMind can read.

USAGE:
  $ python -m backend.utils.reddit_collector_sports

INTEGRATION:
  - The JSON cache is written to: data/social/reddit_sports.json
  - Your /api/context/ai route can merge this into responses.

REQUIREMENTS:
  pip install praw
  (optional) pip install textblob
"""

from __future__ import annotations

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

# -----------------------------
# Minimal optional sentiment
# -----------------------------
def _sentiment(text: str) -> float:
    try:
        from textblob import TextBlob
        return float(TextBlob(text).sentiment.polarity)  # -1..1
    except Exception:
        return 0.0

# -----------------------------
# Logging
# -----------------------------
logger = logging.getLogger("reddit_sports")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
logger.addHandler(ch)

# -----------------------------
# Config (read from env if set)
# -----------------------------
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "hQ84S6INUXshFg4Q0zy6sw")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "h3WB4J6K5IwyRVYE1yb-xSHR4DjrFA")
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ParleyMindSports/1.0 (by u/Annakha)")

# How far back to look
LOOKBACK_HOURS = int(os.getenv("REDDIT_LOOKBACK_HOURS", "24"))
MAX_PER_SUB = int(os.getenv("REDDIT_MAX_PER_SUB", "400"))

# Where to write results
CACHE_PATH = Path("data/social/reddit_sports.json")

# Subreddits to scan
SUBS_NHL = [
    "nhl", "hockey", "FantasyHockey", "hockeyplayers", "hockeygoalies",
    "nhlstreams", "sportsbook", "sportsgambling"
]
SUBS_NCAAB = [
    "CollegeBasketball", "ncaab", "CBB", "MarchMadness",
    "sportsbook", "sportsgambling"
]

# Default scan lists if not supplied by caller
DEFAULT_TEAMS_NHL = [
    "Avalanche", "Red Wings", "Golden Knights", "Rangers", "Bruins",
    "Maple Leafs", "Oilers", "Canucks", "Penguins", "Lightning"
]
DEFAULT_TEAMS_NCAAB = [
    "Duke", "Kansas", "Kentucky", "Gonzaga", "UConn", "North Carolina",
    "Arizona", "Michigan State", "Purdue", "Baylor", "USC", "Colorado",
    "Ohio State", "Michigan", "Wake Forest", "Appalachian State", "Iona",
    "UMKC", "LIU", "Air Force", "UMBC", "Morgan State", "Lipscomb", "UNC Asheville"
]

# -----------------------------
# Core scrape
# -----------------------------
def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

def _within_window(created_utc: float, cutoff: datetime) -> bool:
    dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
    return dt >= cutoff

def _keyword_hit(text: str, keywords: List[str]) -> Tuple[bool, str]:
    t = text.lower()
    for k in keywords:
        k_norm = k.lower()
        if k_norm in t or f"#{k_norm}" in t:
            return True, k
    return False, ""

def _connect_praw():
    import praw
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        check_for_async=False,
    )

def _scan_subreddit(
    reddit,
    subreddit: str,
    keywords: List[str],
    cutoff: datetime,
    max_items: int
) -> List[dict]:
    """Pull latest posts from a subreddit and filter by keywords + time window."""
    out: List[dict] = []
    try:
        sr = reddit.subreddit(subreddit)
        # .new is the most reliable chronological feed.
        for i, post in enumerate(sr.new(limit=max_items)):
            if not hasattr(post, "created_utc"):
                continue
            if not _within_window(float(post.created_utc), cutoff):
                # Since we're iterating from newest to older, once we fall out of window
                # we can break early to speed things up.
                continue

            title = getattr(post, "title", "") or ""
            selftext = getattr(post, "selftext", "") or ""
            body = f"{title}\n{selftext}".strip()

            hit, kw = _keyword_hit(body, keywords)
            if not hit:
                continue

            out.append({
                "id": post.id,
                "subreddit": subreddit,
                "title": title,
                "url": getattr(post, "url", ""),
                "permalink": f"https://reddit.com{getattr(post, 'permalink', '')}",
                "score": int(getattr(post, "score", 0)),
                "num_comments": int(getattr(post, "num_comments", 0)),
                "created_utc": float(post.created_utc),
                "team_hit": kw,
                "sentiment": _sentiment(title),
            })
    except Exception as e:
        logger.warning(f"[WARN] Error scanning r/{subreddit}: {e}")
    return out

def collect_reddit_sports(
    teams_nhl: List[str] | None = None,
    teams_ncaab: List[str] | None = None,
    subs_nhl: List[str] | None = None,
    subs_ncaab: List[str] | None = None,
    lookback_hours: int = LOOKBACK_HOURS,
    max_per_sub: int = MAX_PER_SUB
) -> dict:
    teams_nhl = teams_nhl or DEFAULT_TEAMS_NHL
    teams_ncaab = teams_ncaab or DEFAULT_TEAMS_NCAAB
    subs_nhl = subs_nhl or SUBS_NHL
    subs_ncaab = subs_ncaab or SUBS_NCAAB

    reddit = _connect_praw()
    cutoff = _utc_now() - timedelta(hours=lookback_hours)

    logger.info("=== Reddit Sports Collector Started ===")
    logger.info(f"Window: last {lookback_hours}h | Max/Sub: {max_per_sub}")

    results: Dict[str, dict] = {
        "meta": {
            "generated_at_utc": _utc_now().isoformat(),
            "lookback_hours": lookback_hours,
        },
        "nhl": {"posts": [], "by_team": {}},
        "ncaab": {"posts": [], "by_team": {}},
    }

    # Initialize counters
    for t in teams_nhl:
        results["nhl"]["by_team"][t] = {"count": 0, "avg_sentiment": 0.0}
    for t in teams_ncaab:
        results["ncaab"]["by_team"][t] = {"count": 0, "avg_sentiment": 0.0}

    # NHL pass
    for sub in subs_nhl:
        posts = _scan_subreddit(reddit, sub, teams_nhl, cutoff, max_per_sub)
        logger.info(f"[NHL] r/{sub}: {len(posts)} hits")
        results["nhl"]["posts"].extend(posts)

    # NCAAB pass
    for sub in subs_ncaab:
        posts = _scan_subreddit(reddit, sub, teams_ncaab, cutoff, max_per_sub)
        logger.info(f"[NCAAB] r/{sub}: {len(posts)} hits")
        results["ncaab"]["posts"].extend(posts)

    # Aggregate team stats
    def _aggregate(section_key: str, teams: List[str]):
        by_team = results[section_key]["by_team"]
        for p in results[section_key]["posts"]:
            team = p.get("team_hit", "")
            if team in by_team:
                entry = by_team[team]
                entry["count"] += 1
                # rolling avg
                n = entry["count"]
                entry["avg_sentiment"] = ((entry["avg_sentiment"] * (n - 1)) + p.get("sentiment", 0.0)) / n

    _aggregate("nhl", teams_nhl)
    _aggregate("ncaab", teams_ncaab)

    # Sort posts by recency/score for convenience
    for sec in ("nhl", "ncaab"):
        results[sec]["posts"].sort(key=lambda x: (x.get("created_utc", 0), x.get("score", 0)), reverse=True)

    # Ensure folder exists & write cache
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ Wrote cache: {CACHE_PATH} | NHL posts: {len(results['nhl']['posts'])} | NCAAB posts: {len(results['ncaab']['posts'])}")
        logger.info("=== Reddit Sports Collector Finished ===")
        return results


def run_reddit_collector_sports():
    """Public entry point used by ParleyMind to trigger Reddit scan from context_engine."""
    try:
        return collect_reddit_sports()
    except Exception as e:
        logger.warning(f"[Reddit Context Error] {e}")
        return {}

def run():
    """Entry point for ParleyMind agent orchestrator."""
    from pathlib import Path
    print("[AGENT] Starting Reddit Collector (Sports v2)...")
    collect_reddit_sports()
    print("[AGENT] Reddit Collector finished.")


if __name__ == "__main__":
    try:
        collect_reddit_sports()
    except KeyboardInterrupt:
        logger.info("Cancelled.")
