import sqlite3

from intel.modules.db_patch_team_dossier_v2 import run as run_migration
from intel.modules.decision_policy import decide
from intel.modules.utils_odds import american_to_prob, prob_to_american


def test_american_odds_round_trip_examples():
    assert round(american_to_prob(100), 4) == 0.5
    assert round(american_to_prob(-150), 4) == 0.6
    assert prob_to_american(0.5) == -100
    assert prob_to_american(0.4) == 150


def test_decision_policy_accepts_clear_value():
    decision = decide(
        p_model=0.62,
        p_fanduel=0.54,
        p_kalshi=0.54,
        p_consensus=0.55,
        conf=0.75,
    )

    assert decision.bet is True
    assert decision.venue == "FanDuel"
    assert decision.stake_fraction > 0


def test_team_dossier_migration_is_idempotent(tmp_path):
    db_path = tmp_path / "parleymind.db"
    con = sqlite3.connect(db_path)
    con.execute("CREATE TABLE team_dossier (id INTEGER PRIMARY KEY, team_name TEXT)")
    con.commit()
    con.close()

    run_migration(str(db_path))
    run_migration(str(db_path))

    con = sqlite3.connect(db_path)
    cols = {row[1] for row in con.execute("PRAGMA table_info(team_dossier)").fetchall()}
    con.close()

    assert "p_market_consensus" in cols
    assert "stake_units" in cols
