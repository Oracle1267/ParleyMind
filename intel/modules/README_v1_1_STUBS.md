# ParleyMind v1.1 Stubs (Moneyline Edge Starter)
**Date:** 2025-11-15 10:20  

Drop these files into your project (recommended layout below). They are conservative,
readable, and ready to wire into your existing `intel_cycle.py`.

## Files
- `backend/modules/utils_odds.py`
- `backend/modules/db_patch_team_dossier_v2.py`
- `backend/modules/stats_enricher.py`
- `backend/modules/momentum_engine.py`
- `backend/modules/edge_fuser_v2.py`
- `backend/modules/decision_policy.py`
- `backend/modules/kelly_sizer.py`
- `backend/edge_cycle_example.py`

## Wiring Order
1. **Migration** – ensure dossier columns exist (`db_patch_team_dossier_v2.run()`).
2. **Enrichment** – populate baseline stats (`stats_enricher.enrich()`).
3. **Momentum** – compute simple form metrics (`momentum_engine.compute()`).
4. **Fuse** – compute `p_model`, `edge`, `conf` (`edge_fuser_v2.fuse(row)`).
5. **Decide** – choose venue + stake with guardrails (`decision_policy.decide(...)`).

## Notes
- `stats_enricher` and `momentum_engine` use placeholders so you can run a dry cycle now.
  Swap in your real scrapers and snapshots as you go.
- Keep your **edge threshold** at **3.5%** and **conf ≥ 0.60** while the model is young.
- Add CLV tracking as soon as you log entry and close prices from TheOdds.

