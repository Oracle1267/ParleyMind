from pathlib import Path

state_md_content = """# 🧠 ParleyMind System State — v0.9.7 (11 Nov 2025)

## 📍 Project Summary
**ParleyMind** is an integrated OSINT-powered sports analytics platform designed to identify probabilistic betting advantages across college and professional sports.  
It merges real-time odds, social sentiment, injury reports, and advanced statistical metrics into an adaptive team dossier system capable of generating context-aware betting insights.

---

## ⚙️ Current Architecture

### 🧩 Backend (Python / Flask)
**Directory:** `C:\\Projects\\parleymind\\backend`

| Module | Purpose | Status |
|--------|----------|--------|
| `main.py` | Core Flask app; serves UI, manages endpoints (`/api/odds_ui`, `/api/context/ai/<team>`). | ✅ Stable |
| `context_engine.py` | Aggregates data (injuries, Reddit sentiment, team stats, Bluesky, etc.) into unified team context. | ✅ Operational |
| `reddit_collector_sports.py` | Legacy Reddit ingestion for NHL/NCAAB subs (Pushshift + PRAW). | ⚠️ Obsolete |
| `reddit_collector_sports_v2.py` | Updated Reddit collector using official Reddit API credentials; writes to `/data/social/reddit_sports.json`. | ✅ Active |
| `reddit_scheduler.py` | Background thread to auto-refresh Reddit data every few hours. | ✅ Running |
| `ncaab_reddit_aggregator.py` | Consolidates Reddit mentions and sentiment for each team from JSON cache. | ✅ Active |
| `ncaab_dossier_builder.py` | Builds team dossiers from database + integrated OSINT (stats, injuries, Reddit). | ⚠️ Schema upgrade in progress |
| `ncaab_dossier_scheduler.py` | Periodic regeneration of team dossiers. | ⚙️ Paused (pending schema update) |
| `teamrankings_scraper.py` | Pulls team-level efficiency and matchup stats from TeamRankings.com. | ✅ Online |
| `social_signal.py` | Collects Bluesky sentiment data (via `atproto`). | ✅ Integrated |
| `discover_team_stats_urls_v3.py` *(planned)* | Confirms working `/stats` URLs for verified NCAAB athletic sites. | 🛠️ Pending upload |

---

## 🗄️ Database

**Path:** `backend/instance/parlaymind.db`  
**Type:** SQLite (auto-expanding schema)

| Table | Description | Status |
|-------|--------------|--------|
| `bet` | Stores bet legs and outcomes for model validation. | ✅ |
| `ncaab_team` | Master list of all Division I basketball teams. | ✅ |
| `leg` | Links bets → teams. | ✅ |
| `team_dossier` | Central intelligence object per team (aggregated context). | ⚠️ Needs new columns (`momentum`, `injury_count`, etc.) |
| `injury` | Tracks player injury data. | ✅ + added `team_name` column |
| `game_performance` | Game-level history (date, opponent, score). | ✅ Basic |
| `game_schedule` | Upcoming games and travel data. | ⚙️ Optional for fatigue modeling |

📌 **Next schema update planned:**  
- Add `momentum_score`, `efficiency_margin`, `reddit_sentiment`, and `team_url` to `team_dossier`.  
- Normalize injuries and team relationships for automated joins.

---

## 📈 Data Sources

| Source | Integration | Notes |
|--------|--------------|-------|
| **ESPN** | ✅ | Team IDs, injury data, schedule parsing. |
| **Reddit** | ✅ | Sentiment from r/CollegeBasketball, r/NCAAB, r/Sportsbook, etc. |
| **Bluesky** | ✅ | Public posts mentioning teams/hashtags. |
| **TeamRankings.com** | ✅ | Key stats (off/def efficiency, pace, win prob, etc.) |
| **Official Team Sites** | 🛠️ | Manual base URLs being verified for `/stats` scraping. |
| **KenPom / BartTorvik** | ⚙️ Planned (paid API access). |
| **Rotowire** | ⚙️ Planned for detailed player injury tracking. |
| **OddsJam / Covers.com** | ⚙️ Future — line movement + public bet % integration. |

---

## 🧮 Current Analytical Framework

1. **Reddit Context Layer**  
   - Collects daily mentions and sentiment.
   - Scores team momentum via frequency and tone.

2. **Bluesky Context Layer**  
   - Lightweight check for posts per team.
   - Adds to public awareness/momentum weight.

3. **Team Performance Layer**  
   - Pulls win/loss, scoring margin, pace, and efficiency stats.
   - Auto-ingests from TeamRankings and official `/stats` pages.

4. **Dossier Builder**  
   - Combines injury, performance, and sentiment into a normalized table.
   - Outputs a JSON or SQL view usable by the Parley UI.

---

## 🖥️ Frontend (index.html)
- Displays live odds for **NFL, CFB, NCAAB, NHL**.  
- Upcoming update: integrate team dossier data in the same panel (`injuries`, `momentum`, `social_sentiment`, etc.).  
- Will soon include a **“Context Pulse” widget** showing inferred market bias.

---

## 🚧 Immediate Goals (Next Sprint)

| Priority | Task | Owner | Status |
|-----------|------|--------|--------|
| 🔥 | Update DB schema for `team_dossier` (add key analytics fields). | Nick / ChatGPT | ⏳ |
| 🔥 | Confirm official athletics URLs for 44 tracked NCAAB teams. | Nick | 🧩 In progress |
| 🔥 | Build and test `discover_team_stats_urls_v3.py`. | ChatGPT | 🧱 Next step |
| ⚙️ | Run full `ncaab_dossier_builder` after schema patch. | Nick | ⏳ |
| 🧠 | Add TeamRankings metrics into context_engine | ChatGPT | Planned |
| 🧩 | Display team-level dossiers in UI. | ChatGPT | Planned |

---

## 🧾 Data Output Summary
| File | Location | Description |
|------|-----------|-------------|
| `reddit_sports.json` | `/data/social/` | Cached Reddit results for all active sports subs. |
| `team_stats_links.csv` | `/data/` | Confirmed working stat URLs per school. |
| `team_stats_failures.csv` | `/data/` | Missing or redirected URLs. |
| `team_dossiers.json` *(planned)* | `/data/ncaab/` | Unified team-level intelligence objects. |

---

## 🧩 Future Modules (Design Stage)
- `momentum_engine.py` → calculates rolling momentum scores.
- `line_movement_tracker.py` → tracks odds movement across books.
- `parlay_optimizer.py` → evaluates parlay value based on live implied probabilities.
- `kalshi_feed_adapter.py` → planned integration for market prediction feeds.
- `injury_monitor_rotowire.py` → advanced per-player injury tracking.

---

## 🧭 Current Focus
**Sprint Theme:**  
> “From OSINT to Edge — turning chatter and stats into actionable probability.”

We are currently building the *data fidelity backbone* that will power ParleyMind’s betting intelligence layer.  
Once the 44-team test batch is fully working, the system will scale to all 300+ D1 schools with stable ingestion, caching, and inference.
"""

# Save file to project root
path = Path("state.md")
path.write_text(state_md_content, encoding="utf-8")
path.absolute()
