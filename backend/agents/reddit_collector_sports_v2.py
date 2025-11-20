"""
Reddit Sports Collector (NHL + NCAAB)
-------------------------------------
- Scans selected subreddits for the last N hours.
- Filters posts by simple team-keyword matching.
- Writes cache JSON ParleyMind can read: data/social/reddit_sports.json

USAGE:
  python -m backend.utils.reddit_collector_sports_v2

REQUIREMENTS:
  pip install praw
  (optional) pip install textblob
"""
from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

def _sentiment(text: str) -> float:
    try:
        from textblob import TextBlob
        return float(TextBlob(text).sentiment.polarity)  # -1..1
    except Exception:
        return 0.0

logger = logging.getLogger("reddit_sports")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
logger.addHandler(ch)

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ParleyMindSports/1.0 (by u/ParleyMind)")

LOOKBACK_HOURS = int(os.getenv("REDDIT_LOOKBACK_HOURS", "24"))
MAX_PER_SUB = int(os.getenv("REDDIT_MAX_PER_SUB", "400"))
CACHE_PATH = Path("data/social/reddit_sports.json")

SUBS_NHL = ["nhl", "hockey", "FantasyHockey", "sportsbook", "sportsgambling"]
SUBS_NCAAB = ["CollegeBasketball", "ncaab", "CBB", "MarchMadness", "sportsbook", "sportsgambling"]

DEFAULT_TEAMS_NHL = ["Avalanche", "Red Wings", "Golden Knights", "Rangers", "Bruins"]
DEFAULT_TEAMS_NCAAB = [
    "Duke","Kansas","Kentucky","Gonzaga","UConn","North Carolina","Arizona","Purdue","Baylor","Colorado"
]

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

def _scan_subreddit(reddit, subreddit: str, keywords: List[str], cutoff: datetime, max_items: int) -> List[dict]:
    out: List[dict] = []
    try:
        sr = reddit.subreddit(subreddit)
        for post in sr.new(limit=max_items):
            if not hasattr(post, "created_utc"):
                continue
            if not _within_window(float(post.created_utc), cutoff):
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
        logger.warning(f"[WARN] r/{subreddit}: {e}")
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
        "meta": {"generated_at_utc": _utc_now().isoformat(), "lookback_hours": lookback_hours},
        "nhl": {"posts": [], "by_team": {t: {"count": 0, "avg_sentiment": 0.0} for t in teams_nhl}},
        "ncaab": {"posts": [], "by_team": {t: {"count": 0, "avg_sentiment": 0.0} for t in teams_ncaab}},
    }

    for sub in subs_nhl:
        posts = _scan_subreddit(reddit, sub, teams_nhl, cutoff, max_per_sub)
        logger.info(f"[NHL] r/{sub}: {len(posts)} hits")
        results["nhl"]["posts"].extend(posts)

    for sub in subs_ncaab:
        posts = _scan_subreddit(reddit, sub, teams_ncaab, cutoff, max_per_sub)
        logger.info(f"[NCAAB] r/{sub}: {len(posts)} hits")
        results["ncaab"]["posts"].extend(posts)

    # Aggregate by-team stats
    def _aggregate(section_key: str):
        by_team = results[section_key]["by_team"]
        for p in results[section_key]["posts"]:
            team = p.get("team_hit", "")
            if team in by_team:
                entry = by_team[team]
                n = entry["count"] + 1
                entry["avg_sentiment"] = (entry["avg_sentiment"] * entry["count"] + p.get("sentiment", 0.0)) / n
                entry["count"] = n

    _aggregate("nhl")
    _aggregate("ncaab")

    # Sort posts by recency then score
    for sec in ("nhl", "ncaab"):
        results[sec]["posts"].sort(key=lambda x: (x.get("created_utc", 0), x.get("score", 0)), reverse=True)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"✅ Wrote cache: {CACHE_PATH}")
    logger.info("=== Reddit Sports Collector Finished ===")
    return results

def run():
    print("[AGENT] Starting Reddit Collector (Sports v2)...")
    try:
        collect_reddit_sports()
    finally:
        print("[AGENT] Reddit Collector finished.")

if __name__ == "__main__":
    collect_reddit_sports()
