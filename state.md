# ParleyMind Project State

Date: 2026-08-08
Version: Alpha-1.1 review snapshot
Maintainer: Nick Glanzer
Repository: Oracle1267/ParleyMind

## Executive Summary

ParleyMind is an older, locally run Flask sports betting system that predates modern coding-agent workflows. The core idea is still strong: use a disciplined intelligence collection plan to gather market, team, public-sentiment, and schedule signals, then fuse those signals into value estimates and bounded staking decisions.

The project is currently in a transitional alpha state. There are working pieces for odds ingestion, bet logging, NCAAB team dossiers, Reddit collection, and a v2 moneyline edge cycle. There are also clear seams from several generations of development: duplicate modules, backup files, placeholder analytics, and at least two confirmed breakpoints that block a clean end-to-end run.

The next best step is not to add another model layer. It is to stabilize the source-to-edge pipeline so every report can be traced back to collected evidence and later evaluated for CLV and outcome accuracy.

## Current Architecture

### Backend Flask App

Primary entrypoint:

- `backend/main.py`

Main responsibilities:

- Serve the parlay builder UI.
- Expose bet logging endpoints.
- Expose odds endpoints through `/api/odds_ui/<sport>`.
- Expose team context and NCAAB dossier endpoints.
- Start Reddit and NCAAB dossier background schedulers.

Key models:

- `Bet`
- `Leg`
- `NCAABTeam`
- `TeamDossier`
- `Injury`
- `GamePerformance`
- `GameSchedule`

### Intelligence Layer

Primary files:

- `intel/collection_plan.yaml`
- `intel/intel_cycle.py`
- `intel/modules/db_patch_team_dossier_v2.py`
- `intel/modules/stats_enricher.py`
- `intel/modules/momentum_engine.py`
- `intel/modules/edge_fuser_v2.py`
- `intel/modules/decision_policy.py`
- `intel/modules/kelly_sizer.py`

Current intended flow:

1. Patch `team_dossier` with v2 analytics/staking columns.
2. Refresh baseline team stats.
3. Compute form/momentum proxies.
4. Fuse model probability against market consensus and FanDuel entry probability.
5. Apply decision thresholds and bounded Kelly sizing.
6. Write `data/edge_reports/edge_report_v2_<date>.json`.

### Data Sources

Active or planned source surfaces:

- The Odds API for sportsbook prices.
- Reddit sports collector for sentiment and attention signals.
- TeamRankings scraper for NCAAB scoring stats.
- ESPN/team metadata paths for team context and schedules.
- Local CSV team mapping in `data/ncaab_teams_all.csv`.

## Confirmed Working Pieces

- Repository is connected to `https://github.com/Oracle1267/parleymind.git`.
- Flask app and SQLAlchemy models are present.
- Odds fetchers exist for CFB, NFL, NCAAB, and NHL.
- `intel/collection_plan.yaml` defines priority intelligence requirements.
- `intel/intel_cycle.py` defines a coherent v2 moneyline edge report workflow.
- `intel/modules/decision_policy.py` defines minimum edge and confidence thresholds.
- `intel/modules/kelly_sizer.py` caps staking by confidence band.
- NCAAB dossier builder/scheduler code exists.
- Reddit collection and social signal utilities exist.

## Open Risks

### `intel/modules/stats_enricher.py`

Status: placeholder.

The current enrichment function uses deterministic fake stats based on team-name length.

Impact:

The v2 edge report can run structurally, but its performance inputs are not yet evidence-grade.

### `intel/modules/momentum_engine.py`

Status: placeholder.

The current momentum calculation derives form from `ppg - opp_ppg` instead of real last-5 game performance and market result history.

Impact:

Momentum and confidence should be considered scaffolding, not production-grade betting signals.

## Release Notes

### 2026-08-08 Stabilization Pass

- Repaired `backend/utils/schema_linker.py` so every project Python file compiles.
- Fixed malformed frontend JavaScript around odds and edge loading.
- Added `/api/edge/latest` to serve the newest `edge_report_v2_*.json`.
- Imported the missing WNCAAB and volleyball odds helpers in `backend/main.py`.
- Added `requirements.txt` and `pytest.ini`.
- Added automated coverage for Python compilation, frontend script parsing, odds conversion, decision policy, migration idempotence, schema linking, and the latest-edge endpoint.
- Added environment controls so tests can import the Flask app without starting background schedulers or touching the real app database.

## Existing Dirty Worktree Note

At review time, the worktree already had an uncommitted change in:

- `backend/ncaab_dossier_builder.py`

That change imports `backend.utils.teamrankings_scraper` and computes efficiency margin from TeamRankings points for/allowed. It appears aligned with the modernization direction, but this documentation update does not claim ownership of that source change.

## Recommended Next Step

Make the "source-to-edge spine" work end to end before adding new predictive complexity.

### Step 1: Harden the Source Merge Contract

- Define one canonical source merge contract:
  - `data/social/reddit_sports.json`
  - `data/odds_snapshot.json`
  - `backend/instance/parlaymind.db`
- Add timestamps and source provenance for every linked signal.
- Add alias-aware team matching before relying on partial string matching.

### Step 2: Replace Placeholder Intelligence Inputs

- Replace fake stats in `intel/modules/stats_enricher.py` with real TeamRankings or official stat ingestion.
- Add a team alias map so odds, Reddit, TeamRankings, ESPN, and local CSV names resolve to the same team entity.
- Store source timestamps and provenance in either `signals_json` or normalized source tables.

### Step 3: Add CLV Tracking

- Persist odds snapshots at open, hourly, pregame, and close.
- Compare entry probability to closing probability.
- Report CLV by team, sport, book, and model decision reason.

### Step 4: Validate Betting Logic

- Add tests for:
  - American odds to implied probability.
  - Migration idempotence.
  - Edge decision thresholds.
  - Kelly cap behavior.
  - Latest-report loading.
- Backtest v2 reports against closing lines before increasing automation.

## Intelligence Collection Plan Direction

The system should be refocused around this cycle:

1. Requirements: define the exact edge question.
2. Collection: gather sportsbook, team, social, schedule, injury, and public-bias signals.
3. Processing: normalize team names, timestamps, odds formats, and source confidence.
4. Fusion: compute market probability, model probability, edge, confidence, and stake size.
5. Dissemination: publish an edge report and UI table with reasons and provenance.
6. Feedback: score picks for CLV, result, calibration, and false-positive pattern.

Priority intelligence requirements remain:

- Where is the market mispricing moneyline probability?
- When is public sentiment distorting price?
- Which momentum signals are sustainable versus regression-prone?
- Which schedule/rest/travel factors are underpriced?
- Which line moves precede public information releases?

## Suggested Version Goal

Alpha-1.2 should mean:

- The repo has one documented way to run collection, linking, edge generation, and UI review.
- The UI can show the latest v2 report without JavaScript errors.
- Every edge row includes enough source context to explain why it exists.
- Placeholder stats are replaced or clearly flagged at runtime.
- A minimal test suite protects the moneyline edge path.
