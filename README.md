# ParleyMind

ParleyMind is a local OSINT-style sports betting intelligence system. It is not built on the assumption that the operator already knows sports well. It is built around a different thesis: disciplined scraping, source collection, timestamping, normalization, and validation can surface information asymmetries before the betting market fully prices them in.

The project was inspired by observing a coworker who is skilled at finding profitable sports bets and assembling parlays. ParleyMind exists to make that kind of intuition more inspectable: what changed, who knew it, when the line moved, whether the price still had value, and whether the bet beat the closing market.

## Mission

ParleyMind should answer a focused intelligence question:

> Did we find a real information asymmetry before the current line absorbed it?

The system should prioritize evidence over gut feel. It should collect and compare signals from public sources, sportsbook movement, team context, sentiment, injuries, schedules, and historical outcomes. The goal is not to magically pick winners. The goal is to build a feedback loop that shows which signals create repeatable edge and which signals are noise.

## Current Shape

The repository has three major layers:

- `backend/` - Flask app, odds endpoints, bet logging, team dossier APIs, Reddit/background schedulers, and source-specific utilities.
- `intel/` - Intelligence collection plan and the v2 moneyline edge cycle: migration, enrichment, momentum, model/market fusion, decision policy, and report generation.
- `data/` - Local CSVs, odds snapshots, social/scraper outputs, and generated edge reports.

The app currently uses SQLite at `backend/instance/parlaymind.db` and The Odds API for sportsbook data. Some modules still contain transitional or placeholder logic from earlier versions, so treat the project as an alpha system with valuable working pieces rather than a polished production service.

## Operating Concept

The intended workflow is closer to an intelligence desk than a picks app:

1. Collect public signals from odds, injuries, beat reporting, Reddit/social chatter, schedules, team stats, and local source material.
2. Normalize teams, players, timestamps, books, odds formats, source names, and confidence levels.
3. Detect meaningful changes: injury updates, sentiment spikes, line movement, book disagreement, rest/travel stress, or market overreaction.
4. Fuse signals into a documented edge estimate with model probability, market probability, confidence, and stake recommendation.
5. Validate every signal against closing line value, result, and postmortem notes.

Parleys should be treated as a downstream construction problem, not the first problem. The first problem is proving that any individual leg has positive expected value.

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
5. Add a bet journal/audit trail that records why a bet was considered, when the line was captured, and what source triggered the idea.
6. Add focused tests for odds conversion, decision thresholds, migration idempotence, and report generation.

## Intended Mindset

ParleyMind should operate less like a generic parlay picker and more like an intelligence workflow:

- Start from priority intelligence requirements.
- Collect source signals with timestamps and provenance.
- Normalize team identities across sources.
- Distinguish "this team will win" from "this price is wrong."
- Fuse market, performance, sentiment, and schedule indicators.
- Validate whether identified edge survives closing-line and outcome review.
- Bet only when edge, confidence, and staking rules agree.

## North Star

The strongest version of ParleyMind is not a sports expert in a box. It is an edge-detection instrument for a builder who may not know sports deeply but can build a disciplined OSINT pipeline. If the system can consistently identify better-than-close prices, explain why they appeared, and show which source signals were predictive, then it is doing its job.
