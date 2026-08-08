import json
import sqlite3

from backend.utils import schema_linker


def test_schema_linker_merges_reddit_and_odds(tmp_path, monkeypatch):
    db_path = tmp_path / "parleymind.db"
    reddit_path = tmp_path / "reddit_sports.json"
    odds_path = tmp_path / "odds_snapshot.json"

    con = sqlite3.connect(db_path)
    con.execute("CREATE TABLE team_dossier (id INTEGER PRIMARY KEY, team_name TEXT)")
    con.execute("INSERT INTO team_dossier (team_name) VALUES ('Colorado State Rams')")
    con.commit()
    con.close()

    reddit_path.write_text(
        json.dumps({
            "ncaab": {
                "by_team": {
                    "Colorado State": {"avg_sentiment": 0.25}
                }
            }
        }),
        encoding="utf-8",
    )
    odds_path.write_text(
        json.dumps([
            {
                "team": "Colorado State",
                "p_market_consensus": 0.52,
                "p_fanduel_entry": 0.51,
                "market_prob": 0.52,
                "model_prob": 0.57,
            }
        ]),
        encoding="utf-8",
    )

    monkeypatch.setattr(schema_linker, "DB_PATH", db_path)
    monkeypatch.setattr(schema_linker, "REDDIT_PATH", reddit_path)
    monkeypatch.setattr(schema_linker, "ODDS_PATH", odds_path)

    summary = schema_linker.run()

    con = sqlite3.connect(db_path)
    row = con.execute(
        """
        SELECT reddit_sentiment, p_market_consensus, p_fanduel_entry, edge, value_index
        FROM team_dossier
        WHERE team_name = 'Colorado State Rams'
        """
    ).fetchone()
    con.close()

    assert summary["total"] == 2
    assert row == (0.25, 0.52, 0.51, 0.05, 0.0625)
