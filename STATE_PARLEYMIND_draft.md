# ParleyMind • Project State (Draft)
**Generated:** 2025-11-15 10:16

## Snapshot
- Files detected: 1009 (by extension: py×963, txt×27, md×8, json×5, csv×3, log×1, cfg×1, yaml×1)
- Directories (approx): 1758
- Python packages/modules (dirs with `__init__.py`): —

## Top-Level Hints (heuristic)
- Folder PATH listing for volume Windows
- Volume serial number is 96C6-8FFB
- C:.
- |   .env
- |   .env.bak
- |   debug_dossier.py
- |   parleymind_tree.txt
- |   state - Copy.md
- |   state - Copy.md.bak
- |   state v1_0.md
- |   state.md
- |   statev_0_9_7.md
- |   state_v1_0.md
- |   structure.txt
- |
- +---backend
- |   |   config.json
- |   |   config.py
- |   |   db_patch_0_9_8.py
- |   |   discover_team_stats_urls_v3.py

## Notable Components (name-based heuristic)
- |   debug_dossier.py
- |   |   config.json
- |   |   config.py
- |   |   models.py
- |   |   ncaab_dossier_builder.py
- |   |   ncaab_teams_all.csv
- |   |   odds_snapshot.json
- |   |   |       |   |   _internal_utils.py
- |   |   |       |   |   _utils.py
- |   |   |       |   |   api.py
- |   |   |       |   |   async_utils.py
- |   |   |       |   |   cli.py
- |   |   |       |   |   config.py
- |   |   |       |   |   core.py
- |   |   |       |   |   model.py
- |   |   |       |   |   models.py
- |   |   |       |   |   utils.py
- |   |   |       |   |   |   api.py
- |   |   |       |   |   |   config.py
- |   |   |       |   |   |   configuration.py
- |   |   |       |   |   |   decl_api.py
- |   |   |       |   |   |   type_api.py
- |   |   |       |   |   |   type_migration_guidelines.txt
- |   |   |       |   |   |   utils.py
- |   |   |       |   |   |   |   _api.py
- |   |   |       |   |   |   |   _distutils.py
- |   |   |       |   |   |   |   _internal_utils.py
- |   |   |       |   |   |   |   _sysconfig.py
- |   |   |       |   |   |   |   api.py
- |   |   |       |   |   |   |   configuration.py
- |   |   |       |   |   |   |   core.py
- |   |   |       |   |   |   |   modeline.py
- |   |   |       |   |   |   |   models.py
- |   |   |       |   |   |   |   reserved_words.py
- |   |   |       |   |   |   |   utils.py
- |   |   |   ncaab_dossier_builder.py
- |   |   |   ncaab_dossier_scheduler.py
- |   |   |   ncaab_reddit_aggregator.py
- |   |   |   odds_fetcher.py
- |   |   |   reddit_scheduler.py
- |   |   |   teamrankings_scraper.py
- |   |   |   tradecore_bridge.py
- |   |   |   |   ncaa_wbb_scraper.py
- |   |   |   |   ncaa_wvb_scraper.py

## Immediate Next Actions (suggested)
1. **Fix date handling** in any `ncaab_*` dossiers/builders (tz-naive vs aware; standardize season keys).
2. **Lock pipelines by league/season** with consistent IDs across ingest → transform → model.
3. **DB schema**: add idempotent upserts & unique indexes on `(league, season, game_id, book, fetched_at)`.
4. **Unit tests** for dossier builders, odds parsers, and feature generation.
5. **Re-run dossier sync** and capture a clean log for the `STATE.md` appendix.
6. **Create `env.sample`** documenting required secrets and API URLs.
7. **CLI ergonomics**: `python -m backend.cli build-dossiers --league NCAAB --season 2025`.

## Risks & Unknowns
- Inconsistent team naming across sources (alias map needed).
- Timezone & DST drift affecting game datetime joins.
- Book odds normalization (American ↔ decimal) & juice removal not yet validated.
- Potential gaps in historical lines (backfill strategy TBD).

---
*(Auto-generated from the uploaded tree; refine as we iterate.)*
