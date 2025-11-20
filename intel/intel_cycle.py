"""
PARLEYMIND INTELLIGENCE CYCLE v2.2 (Moneyline Edge – FanDuel-only)
------------------------------------------------------------------
Runs the v1.1 moneyline edge pipeline WITHOUT Kalshi:
  1) DB migration for new dossier fields
  2) Stats enrichment (wins/losses/ppg/opp_ppg/coach/pace)
  3) Momentum calc (form_last5_net / rolling_z)
  4) Fuse model (p_model, edge, conf) anchored to market consensus
  5) Decision policy (FanDuel venue + bounded Kelly stake)
  6) Write edge_report_v2_YYYY-MM-DD.json

Author: ParleyMind / Nick G.
Date: 2025-11-15
"""

import json
import sqlite3
import traceback
from pathlib import Path
from datetime import datetime, date, UTC

# === v1.1 EDGE imports (intel package layout) ===
from intel.modules.db_patch_team_dossier_v2 import run as migrate_team_dossier_v2
from intel.modules.stats_enricher import enrich as stats_enrich
from intel.modules.momentum_engine import compute as momentum_compute
from intel.modules.edge_fuser_v2 import fuse as edge_fuse
from intel.modules.decision_policy import decide as edge_decide

# --- CONFIG --------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]          # C:\Projects\parleymind
DB_PATH = ROOT / "backend" / "instance" / "parlaymind.db"
REPORTS_PATH = ROOT / "data" / "edge_reports"
REPORTS_PATH.mkdir(parents=True, exist_ok=True)

# add right after the stdlib imports
import os, sys
from pathlib import Path as _P
sys.path.append(str(_P(__file__).resolve().parents[1]))  # ensures project root on sys.path

# keep using the existing ROOT/DB_PATH logic,
# but allow PARLEY_DB override:
DB_OVERRIDE = os.getenv("PARLEY_DB")
if DB_OVERRIDE:
    DB_PATH = _P(DB_OVERRIDE)




# --- HELPERS -------------------------------------------------------------
def _to_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def _fetch_rows(con: sqlite3.Connection):
    """
    Pull the dossier fields needed for v1.1 (FanDuel-only).
    """
    cur = con.cursor()
    cur.execute("""
        SELECT
            id,
            team_name,

            -- odds fields (FanDuel + market consensus)
            COALESCE(p_market_consensus, market_prob, 0) AS p_market_consensus,
            COALESCE(p_fanduel_entry, 0)                 AS p_fanduel_entry,

            -- stats (from enricher)
            COALESCE(ppg, 0)                             AS ppg,
            COALESCE(opp_ppg, 0)                         AS opp_ppg,
            COALESCE(form_last5_net, 0)                  AS form_last5_net,

            -- legacy (not used, kept for continuity)
            COALESCE(model_prob, 0)                      AS legacy_model_prob,
            COALESCE(market_prob, 0)                     AS legacy_market_prob,
            COALESCE(edge, 0)                            AS legacy_edge,
            COALESCE(value_index, 0)                     AS legacy_value_index,
            COALESCE(reddit_sentiment, 0)                AS legacy_sentiment
        FROM team_dossier
    """)
    return cur.fetchall()

# --- MAIN INTELLIGENCE CYCLE --------------------------------------------
def run_intel_cycle():
    start_ts = datetime.now(UTC)
    print(f"\n[INTEL] === ParleyMind Intelligence Cycle started @ {start_ts} ===")

    # 0) Ensure DB has all required columns
    migrate_team_dossier_v2(str(DB_PATH))

    # 1) Refresh baseline stats (placeholder until real scraper is wired)
    _ = stats_enrich(str(DB_PATH))

    # 2) Compute simple momentum proxies (placeholder until last-5 games logic is wired)
    _ = momentum_compute(str(DB_PATH))

    # 3) Read dossiers and compute fused model + decision
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = _fetch_rows(con)
    if not rows:
        print("[INTEL] ⚠️ No rows in team_dossier. Populate dossiers and odds first.")
        con.close()
        return

    findings = []
    num_bet_candidates = 0

    for r in rows:
        team = str(r["team_name"] or "Unknown")

        # Normalized probabilities
        p_market = _to_float(r["p_market_consensus"])
        p_fd     = _to_float(r["p_fanduel_entry"])

        # Skip if no usable price/market
        if p_market <= 0 or p_fd <= 0:
            continue

        # Stats context
        ppg        = _to_float(r["ppg"])
        opp_ppg    = _to_float(r["opp_ppg"])
        form_last5 = _to_float(r["form_last5_net"])

        # Fuse → p_model, edge (vs best venue), conf
        # NOTE: We DO NOT have Kalshi; force p_kalshi_entry to p_fanduel_entry so helpers work unchanged.
        fused = edge_fuse({
            "p_market_consensus": p_market,
            "form_last5_net":     form_last5,
            "ppg":                ppg,
            "opp_ppg":            opp_ppg,
            "p_fanduel_entry":    p_fd,
            "p_kalshi_entry":     p_fd,  # <-- mirror FanDuel (no Kalshi data)
        })

        # Decide venue + stake (will pick FanDuel since both equal)
        decision = edge_decide(
            p_model=fused["p_model"],
            p_fanduel=p_fd,
            p_kalshi=p_fd,           # <-- mirror FanDuel (no Kalshi data)
            p_consensus=p_market,
            conf=fused["conf"]
        )

        value_index_v2 = fused["edge"] * fused["conf"]
        venue = decision.venue if decision.venue else "FanDuel"

        entry_prob = p_fd

        finding = {
            "team": team,
            # Market + venue
            "p_market_consensus": p_market,
            "p_fanduel_entry": p_fd,
            "entry_prob": entry_prob,
            # Model result
            "p_model": fused["p_model"],
            "edge": fused["edge"],
            "confidence_v2": fused["conf"],
            "value_index_v2": value_index_v2,
            # Decision
            "bet": bool(decision.bet),
            "venue": venue,
            "stake_fraction": round(decision.stake_fraction, 6),
            "stake_units": round(decision.stake_fraction * 100.0, 3),
            "decision_reason": getattr(decision, "reason", "ok"),
            # Legacy for continuity (not required by v1.1)
            "legacy": {
                "legacy_model_prob": _to_float(r["legacy_model_prob"]),
                "legacy_market_prob": _to_float(r["legacy_market_prob"]),
                "legacy_edge": _to_float(r["legacy_edge"]),
                "legacy_value_index": _to_float(r["legacy_value_index"]),
                "legacy_sentiment": _to_float(r["legacy_sentiment"]),
            }
        }

        if finding["bet"]:
            num_bet_candidates += 1

        findings.append(finding)

    con.close()

    if not findings:
        print("[INTEL] ⚠️ No findings produced (missing odds or dossier fields).")
        return

    # Sort by new value index (v2)
    findings.sort(key=lambda x: x["value_index_v2"], reverse=True)

    # Build summary
    total = len(findings)
    avg_edge = round(sum(f["edge"] for f in findings) / max(1, total), 4)
    avg_val2 = round(sum(f["value_index_v2"] for f in findings) / max(1, total), 4)
    top10 = findings[:10]
    top_bets = [f for f in findings if f["bet"]]

    summary = {
        "report_version": "v2",
        "report_date": date.today().isoformat(),
        "started_at_utc": start_ts.isoformat(),
        "teams_analyzed": total,
        "bet_candidates": num_bet_candidates,
        "avg_edge": avg_edge,
        "avg_value_index_v2": avg_val2,
        "top_10_teams": [f["team"] for f in top10],
    }

    # Save JSON report
    report_obj = {
        "meta": summary,
        "findings": findings
    }
    outfile = REPORTS_PATH / f"edge_report_v2_{date.today()}.json"
    outfile.write_text(json.dumps(report_obj, indent=2), encoding="utf-8")
    print(f"[INTEL] ✅ Edge Assessment Report saved: {outfile}")

    # Print Top Bets (those that passed policy)
    if top_bets:
        print("\n[INTEL] Bet Candidates (sorted by ValueIndex v2):")
        for f in top_bets[:10]:
            team = f["team"]
            edge = f["edge"]
            conf = f["confidence_v2"]
            units = f["stake_units"]
            venue = f["venue"] or "-"
            print(f"   {team:<28} | Edge:{edge:+.3f} | Conf:{conf:.2f} | Units:{units:.2f} | Venue:{venue}")
    else:
        print("\n[INTEL] No bets passed thresholds this cycle.")

    # Footer
    print("\n[INTEL] === Cycle Summary ===")
    print(f"Teams Analyzed: {total}")
    print(f"Bet Candidates: {num_bet_candidates}")
    print(f"Average Edge: {avg_edge:+.4f}")
    print(f"Average Value Index v2: {avg_val2:+.4f}")
    print(f"[INTEL] === Intelligence Cycle complete ===\n")


# --- ENTRYPOINT ----------------------------------------------------------
if __name__ == "__main__":
    try:
        run_intel_cycle()
    except Exception:
        traceback.print_exc()
