# ParleyMind

ParleyMind is a local sports betting intelligence system focused on finding value, especially in moneyline-first parlay construction. It began as a pre-Codex Flask betting assistant and has since grown toward an intelligence collection plan model: gather source signals, normalize them, fuse them into edge estimates, and turn those estimates into disciplined staking decisions.

## Current Shape

The repository has three major layers:

- `backend/` - Flask app, odds endpoints, bet logging, team dossier APIs, Reddit/background schedulers, and source-specific utilities.
- `intel/` - Intelligence collection plan and the v2 moneyline edge cycle: migration, enrichment, momentum, model/market fusion, decision policy, and report generation.
- `data/` - Local CSVs, odds snapshots, social/scraper outputs, and generated edge reports.

The app currently uses SQLite at `backend/instance/parlaymind.db` and The Odds API for sportsbook data. Some modules still contain transitional or placeholder logic from earlier versions, so treat the project as an alpha system with valuable working pieces rather than a polished production service.

## What Works

- Flask server with parlay/bet CRUD endpoints.
- Live odds fetch path for CFB, NFL, NCAAB, and NHL through The Odds API.
- NCAAB team/dossier database models.
- Background Reddit and NCAAB dossier schedulers.
- Intelligence collection plan in `intel/collection_plan.yaml`.
- v2 edge report cycle in `intel/intel_cycle.py`.
- Bounded Kelly staking policy in `intel/modules/kelly_sizer.py`.
- Model-vs-market decision policy in `intel/modules/decision_policy.py`.

## Known Gaps

- `backend/templates/index.html` has malformed JavaScript around `loadOdds()` and references `/api/edge/latest`, which is not currently implemented.
- `backend/utils/schema_linker.py` does not compile in its current state and needs repair before it can merge Reddit and odds signals.
- `intel/modules/stats_enricher.py` and `intel/modules/momentum_engine.py` still use placeholder stats/form logic.
- `backend/main.py` has branches for `wncaab` and `volleyball` odds without importing the matching helper functions.
- There are duplicate legacy modules and backups that should be pruned once the active path is confirmed.
- No dependency manifest or automated test suite is present yet.

## Setup

Create a local `.env` file with:

```env
ODDS_API_KEY=your_the_odds_api_key
REDDIT_CLIENT_ID=optional
REDDIT_CLIENT_SECRET=optional
REDDIT_USER_AGENT=parleymind-scraper
PARLEY_DB=backend/instance/parlaymind.db
```

Install the Python dependencies used by the current code:

```powershell
pip install flask flask-cors flask-sqlalchemy python-dotenv requests beautifulsoup4 textblob pytz
```

Run the Flask app:

```powershell
python -m backend.main
```

Run the intelligence cycle:

```powershell
python -m intel.intel_cycle
```

## Modernization Priority

The next engineering pass should focus on making the intelligence cycle reliable end to end:

1. Repair `backend/utils/schema_linker.py` and define a repeatable source-ingestion order.
2. Add `/api/edge/latest` so the UI can consume the newest generated report.
3. Replace placeholder enrichment with real TeamRankings/official stats data and a team alias map.
4. Persist open/hourly/pre-close/close odds snapshots for CLV tracking.
5. Add focused tests for odds conversion, decision thresholds, migration idempotence, and report generation.

## Intended Mindset

ParleyMind should operate less like a generic parlay picker and more like an intelligence workflow:

- Start from priority intelligence requirements.
- Collect source signals with timestamps and provenance.
- Normalize team identities across sources.
- Fuse market, performance, sentiment, and schedule indicators.
- Validate whether identified edge survives closing-line and outcome review.
- Bet only when edge, confidence, and staking rules agree.
