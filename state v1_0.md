from pathlib import Path

state_md_content = """## 🧩 ParleyMind — System State v0.9.3  
**Date:** 11 Nov 2025  
**Status:** ⚙️ Functional with Context AI Integration  

---

### 🏗️ Core Architecture

| Layer | File | Purpose | Status |
|-------|------|----------|--------|
| **Backend** | `backend/main.py` | Flask entry point, serves routes `/api/odds_ui/<sport>` and `/api/context/ai/<team>` | ✅ Stable |
|  | `backend/utils/context_engine.py` | Builds team context (injuries, momentum, bye week, social, Reddit) | ✅ Operational |
|  | `backend/utils/social_signal.py` | Gathers Bluesky signals (via `atproto` if installed) | ✅ Optional |
|  | `backend/utils/reddit_collector_sports.py` | Collects NHL + NCAAB posts via PRAW (Reddit API) | ✅ Running correctly |
|  | `backend/utils/reddit_scheduler.py` | Background scheduler; now imports `run_reddit_collector_sports()` dynamically | ✅ Fixed |
| **Frontend** | `frontend/index.html` | Web interface for parlay builder; loads odds via `/api/odds_ui`; fetches AI context per team | ✅ Displaying NFL, NCAAF, NHL, NCAAB |
| **Odds Source** | `backend/utils/odds_fetcher.py` | Pulls live data from the Odds API for multiple sports | ✅ Working for NFL, CFB, NHL, NCAAB |

---

### 🔍 Data Flows

#### 1. **Odds Pipeline**
odds_fetcher → Flask route /api/odds_ui/<sport> → frontend odds table
- Supports `nfl`, `cfb`, `nhl`, `ncaab`
- Data updates manually via browser refresh or backend reload

#### 2. **Context AI Pipeline**
context_engine → ESPN (injuries, schedule) + Reddit + Bluesky
- Uses ESPN team ID lookup to find injuries and bye-week status  
- Reddit data cached in `data/social/reddit_sports.json`  
- Bluesky queries are optional (only if credentials exist in config)  
- Returns JSON summary per team with:
  ```json
  {
    "bye_week": false,
    "injuries": [],
    "momentum": "neutral",
    "reddit_mentions": 4,
    "reddit_sentiment": "positive",
    "notes": "Found ESPN ID 38"
  }
#### 3. Scheduler
reddit_scheduler → calls run_reddit_collector_sports() every launch
- Background thread launches at Flask startup

- Now uses safe dynamic import (avoids stale cache)

- Planned: 6-hour refresh interval instead of per page load

🧠 Known Issues / Next Steps
Priority	Task	Status
🔴 High	Add setInterval/thread.Timer for 6-hour Reddit refresh	⏳ Pending
🟠 Medium	Move context AI inference results (momentum/social score) onto homepage UI	⏳ Pending
🟠 Medium	Remove Flask debug autoreloader duplication	⏳ Pending
🟢 Low	Create /scripts/flush_cache_and_restart.py utility for dev resets	⏳ Planned
🟢 Low	Tune PRAW subreddit filters and sentiment thresholds	⏳ Ongoing

📦 Current Directory Structure
parleymind/
├── backend/
│   ├── main.py
│   └── utils/
│       ├── context_engine.py
│       ├── odds_fetcher.py
│       ├── reddit_collector_sports.py
│       ├── reddit_scheduler.py
│       └── social_signal.py
├── frontend/
│   └── index.html
├── data/
│   └── social/
│       └── reddit_sports.json
└── state.md   ← this file

⚙️ Current Behavior Snapshot

Frontend: Loads live odds for 4 sports; builds parlays interactively.

Backend: Returns combined context + social data for each team.

Reddit Collector: Runs every startup; caches results.

BlueSky Collector: Returns empty array if no posts found or creds missing.

🔮 Next Version Targets (v1.0)

Add per-team “momentum card” showing Reddit sentiment and post frequency.

Integrate threading.Timer loop for background refreshes (6h cycle).

Move configuration to .env and add config_loader.py.

Add historical odds comparison and “smart parlay suggestion” logic.

Add local SQLite cache for team contexts.


