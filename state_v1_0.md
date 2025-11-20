from pathlib import Path

state_v1_0_0 = """# 🧠 ParleyMind System State — v1.0.0 (15 Nov 2025)

## 📍 Project Summary
**ParleyMind** is now a fully operational OSINT-driven sports intelligence platform capable of fusing live sentiment, odds, and performance data into actionable probability edge assessments.  
This milestone marks the completion of the **data synchronization layer** — Reddit, odds, and team dossiers now operate in unified schema alignment.

---

## ⚙️ Current Architecture

### 🧩 Backend (Python / Flask)
**Directory:** C:\\Projects\\parleymind\\backend

| Module | Purpose | Status |
|--------|----------|--------|
| `main.py` | Core Flask app serving dashboard and `/api` endpoints. | ✅ Stable |
| `reddit_collector_sports_v2.py` | Collects multi-subreddit NCAAB & NHL sentiment; saves to `data/social/reddit_sports.json`. | ✅ Active |
| `odds_fetcher.py` | Gathers real-time lines and implied probabilities; outputs to `data/odds_snapshot.json`. | ✅ Active |
| `schema_linker.py` | Links sentiment + odds into database, updating `team_dossier` fields. | ✅ Verified |
| `ncaab_dossier_builder.py` | Centralized intelligence constructor; builds and updates dossiers with metadata, sentiment, odds, and base URLs. | ✅ Stable |
| `intel_cycle.py` | Generates probabilistic edge reports and confidence scoring. | ✅ Operational |
| `reddit_scheduler` / `dossier_scheduler` | Background threads for auto-refreshing context. | ⚙️ Optional |
| `teamrankings_scraper.py` | Planned extension for live stat ingestion (W–L, PPG, Opp PPG). | 🧩 Next milestone |

---

## 🗄️ Database

**Path:** C:\\Projects\\parleymind\\backend\\instance\\parlaymind.db  
**Type:** SQLite (production-ready schema)

| Table | Description | Status |
|-------|--------------|--------|
| `ncaab_team` | Team registry synced from `ncaab_teams_all.csv`. | ✅ |
| `team_dossier` | Unified intelligence per team (odds + sentiment + URLs + edge). | ✅ New schema |
| `bet` / `leg` | Reserved for model validation and parlay tracking. | ⚙️ Planned |
| `injury`, `game_schedule`, `game_performance` | Placeholder structures for future integration. | ⚙️ Planned |

### `team_dossier` Columns
| Column | Description |
|--------|--------------|
| id | Primary key |
| team_id | FK → ncaab_team |
| team_name | Unique team name |
| base_url | Official team athletics site |
| summary | Scraped page summary/meta |
| snapshot_date | Date of last dossier update |
| reddit_sentiment | “positive” / “neutral” / “negative” |
| market_prob / model_prob | Market vs model probability differentials |
| edge | Calculated deviation (value signal) |
| value_index | Weighted opportunity score |
| created_at | ISO 8601 UTC timestamp |

---

## 📈 Data Sources

| Source | Integration | Output |
|--------|--------------|----------|
| **Reddit API** | ✅ | `data/social/reddit_sports.json` |
| **Odds API** | ✅ | `data/odds_snapshot.json` |
| **Official Athletics Sites** | ✅ | Base URLs from `data/ncaab_teams_all.csv` |
| **TeamRankings.com** | ⚙️ Planned (off/def metrics) |
| **Rotowire / ESPN Injuries** | ⚙️ Planned |
| **Bluesky** | ⚙️ Optional sentiment layer (future) |

---

## 🧠 Analytical Stack
1. **Sentiment Layer** – Normalized via Reddit mentions and tone analysis.  
2. **Market Layer** – Real-time implied probability comparison from odds feeds.  
3. **Fusion Layer (Schema Linker)** – Writes cross-source context to SQLite.  
4. **Dossier Layer** – Creates comprehensive team-level intelligence profiles.  
5. **Intel Cycle** – Computes edge, confidence, and value index for dashboard.  

---

## 🖥️ Frontend Status (index.html / dashboard.html)
- **Working routes:** `/`, `/api/ncaab/dossier/<team>`  
- **Dashboard data:** Reads from `team_dossier` table.  
- **Next feature:** Interactive Value Index heatmap + sortable team metrics.  

---

## 🚧 Current Goals (Next Sprint)
| Priority | Task | Owner | Status |
|-----------|------|--------|--------|
| 🔥 | Integrate `team_dossier` metrics into the Flask dashboard UI. | Nick | 🧩 In progress |
| 🔥 | Add W–L and PPG scraping from each `base_url`. | ChatGPT | Planned |
| ⚙️ | Automate full intelligence refresh (Reddit → Odds → Linker → Dossier → Intel). | Both | Planned |
| ⚙️ | Extend edge report to visualize trends over time. | ChatGPT | Pending |
| 🧩 | Begin UI optimization for actionable edge filtering. | Nick | Upcoming |

---

## 🧾 Data Output Summary
| File | Location | Purpose |
|------|-----------|----------|
| `reddit_sports.json` | `data/social/` | Reddit sentiment cache |
| `odds_snapshot.json` | `data/` | Real-time market odds |
| `ncaab_teams_all.csv` | `data/` | Verified base URLs for all tracked teams |
| `edge_report_*.json` | `data/edge_reports/` | Intel Cycle results |
| `state_v1_0_0.md` | `/data/` or `/docs/` | Current system state summary |

---

## 🧩 Next Module Targets
- `stats_enricher.py` → Pulls W–L, PPG, Opp PPG, and coach names.  
- `momentum_engine.py` → Computes form-based team momentum.  
- `edge_dashboard.py` → Web layer to visualize Value Index by confidence.  
- `db_patch_team_dossier_v2.py` → Handles automatic schema migrations.  

---

## 🧭 Sprint Theme
> “Alignment and Intelligence — fuse every signal into one coherent edge.”

This milestone establishes **schema coherence** and stable ingestion pipelines, setting the foundation for **predictive enrichment** and UI-level insight delivery in v1.1+.
"""

out_path = Path("statev_1_0_0.md")
out_path.write_text(state_v1_0_0, encoding="utf-8")
out_path.resolve()
