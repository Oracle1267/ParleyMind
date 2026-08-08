import importlib
import json
import sys


def _load_app(monkeypatch, tmp_path):
    monkeypatch.setenv("ODDS_API_KEY", "test-key")
    monkeypatch.setenv("PARLEYMIND_DISABLE_SCHEDULERS", "1")
    monkeypatch.setenv("PARLEY_DB", str(tmp_path / "api.db"))
    monkeypatch.setenv(
        "PARLEY_SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{(tmp_path / 'sqlalchemy.db').as_posix()}",
    )
    sys.modules.pop("backend.main", None)
    return importlib.import_module("backend.main").app


def test_latest_edge_report_endpoint_returns_newest_report(tmp_path, monkeypatch):
    reports_dir = tmp_path / "edge_reports"
    reports_dir.mkdir()
    monkeypatch.setenv("PARLEY_EDGE_REPORTS_DIR", str(reports_dir))
    app = _load_app(monkeypatch, tmp_path)

    report = reports_dir / "edge_report_v2_2026-08-08.json"
    report.write_text(
        json.dumps({
            "meta": {"report_version": "v2"},
            "findings": [{"team": "Colorado State Rams", "edge": 0.05}],
        }),
        encoding="utf-8",
    )

    response = app.test_client().get("/api/edge/latest")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["source_file"] == report.name
    assert payload["findings"][0]["team"] == "Colorado State Rams"


def test_latest_edge_report_endpoint_handles_missing_report(tmp_path, monkeypatch):
    reports_dir = tmp_path / "edge_reports"
    reports_dir.mkdir()
    monkeypatch.setenv("PARLEY_EDGE_REPORTS_DIR", str(reports_dir))
    app = _load_app(monkeypatch, tmp_path)

    response = app.test_client().get("/api/edge/latest")

    assert response.status_code == 404
    assert response.get_json()["findings"] == []
