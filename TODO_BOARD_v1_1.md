# ParleyMind • TODO Board (v1.1 Bootstrap)
Generated: 2025-11-15 10:17

## Legend
- [ ] TODO  |  [~] In-Progress  |  [x] Done

## High-Impact Next (Start Here)
- [ ] **Implement `stats_enricher.py`** to populate W–L, PPG, OppPPG, coach, pace into `team_dossier`.
- [ ] **Add `momentum_engine.py`** for last-5 net rating, market beat rate, rolling z-scores.
- [ ] **Wire `edge_fuser_v2` + `kelly_sizer`** into `intel_cycle.py` to output `edge_report_v2.json`.
- [ ] **Odds snapshots**: extend odds fetcher to persist open/hourly/pre/close implied probabilities for CLV.
- [ ] **Dashboard table v2**: sortable (Edge, Conf, Model%, Market%, Kelly%, Units, W–L, PPG, OppPPG).

## INGEST / SCRAPERS  
_Found 25 files_
- odds_fetcher.py
- reddit_collector_sports_v2.py
- reddit_sports_2025-11-09.log
- context_fetcher.py
- ncaab_dossier_scheduler.py
- ncaab_reddit_aggregator.py
- odds_fetcher.py
- reddit_collector_sports.py
- reddit_collector_sports_v2.py
- reddit_scheduler.py
- teamrankings_scraper.py
- ncaa_wbb_scraper.py
- ncaa_wvb_scraper.py
- api.py
- collector.py
- [ ] Normalize team names across sources (alias map).
- [ ] Add retry/backoff and response schema validation.
- [ ] Log fetch timestamps for open/hourly/pre/close snapshots.

## DB / SCHEMA / MIGRATIONS  
_Found 36 files_
- db_patch_0_9_8.py
- models.py
- schema_linker.py
- models.py
- sessions.py
- session.py
- sandbox.py
- installation_report.py
- session.py
- reporter.py
- models.py
- sessions.py
- reporters.py
- models.py
- sessions.py
- [ ] Create idempotent migration for `team_dossier` new columns (form, pace, kelly, signals_json).
- [ ] Add unique index `(league, season, game_id, book, fetched_at)` on odds snapshots.

## CORE ANALYTICS / EDGE  
_Found 6 files_
- edge_calc.py
- social_signal.py
- signals.py
- model.py
- modeline.py
- probe.py
- [ ] Implement calibration (Platt/Isotonic) hook (optional for v1.1).
- [ ] Define `DEFAULT_THRESHOLDS` in `decision_policy.py` (edge, conf).

## BACKEND / SERVER  
_Found 10 files_
- main.py
- app.py
- blueprints.py
- views.py
- app.py
- blueprints.py
- main.py
- main.py
- controller.py
- testapp.py
- [ ] `/api/value-table` returns table rows for dashboard v2.
- [ ] Add `/api/edge-report` to stream latest `edge_report_v2.json`.

## UTILS / HELPERS  
_Found 47 files_
- config.json
- config.py
- env_loader.py
- pyvenv.cfg
- _utilities.py
- utils.py
- utils.py
- _utils.py
- utils.py
- config.py
- debughelpers.py
- helpers.py
- async_utils.py
- constants.py
- environment.py
- [ ] `env.sample` for keys and base URLs.
- [ ] Centralize odds conversion (American ↔ prob) util and test it.

## TESTS  
_Found 34 files_
- ansitowin32_test.py
- ansi_test.py
- initialise_test.py
- isatty_test.py
- winterm_test.py
- test_contextvars.py
- test_cpp.py
- test_extension_interface.py
- test_gc.py
- test_generator.py
- test_generator_nested.py
- test_greenlet.py
- test_greenlet_trash.py
- test_leaks.py
- test_stack_saved.py
- [ ] Unit: odds conversion; CLV tracker; decision policy thresholds; DB migration idempotence.

## DOCS  
_Found 8 files_
- state - Copy.md
- state v1_0.md
- state.md
- statev_0_9_7.md
- state_v1_0.md
- README.md
- LICENSE.md
- ICON_LICENSE.md
- [ ] Update `STATE.md` to v1.1 once edge report runs end-to-end.

## DATA / CSV / JSON  
_Found 4 files_
- ncaab_teams_all.csv
- team_stats_failures.csv
- team_stats_links.csv
- collection_plan.yaml

## OTHER  
_Found 839 files_
- debug_dossier.py
- parleymind_tree.txt
- structure.txt
- discover_team_stats_urls_v3.py
- logger.py
- ncaab_dossier_builder.py
- run_agents.py
- __init__.py
- __init__.py
- context_engine.py
- discover_team_stats_urls.py
- ncaab_dossier_builder.py
- tradecore_bridge.py
- __init__.py
- feed_manager.py