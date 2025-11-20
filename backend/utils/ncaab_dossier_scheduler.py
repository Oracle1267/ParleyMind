import threading
import time
import datetime


def _init_teams(app):
    """One-time initialization: sync all NCAAB teams from ESPN."""
    with app.app_context():
        try:
            from backend.utils.ncaab_dossier_builder import get_ncaab_teams_from_espn, sync_teams_to_db
            print("[NCAAB Dossier Scheduler] Fetching teams from ESPN...")
            teams = get_ncaab_teams_from_espn()
            if teams:
                sync_teams_to_db(teams)
                print(f"[NCAAB Dossier Scheduler] Synced {len(teams)} teams")
        except Exception as e:
            print(f"[NCAAB Dossier Scheduler] Error initializing teams: {e}")


def _run_update_once(app):
    """Run a single dossier update cycle."""
    with app.app_context():
        try:
            from backend.utils.ncaab_dossier_builder import update_all_dossiers
            from backend.utils.ncaab_reddit_aggregator import load_ncaab_reddit_data
            print(f"[{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S}] [NCAAB Dossier Scheduler] Updating dossiers...")
            reddit_data = load_ncaab_reddit_data()
            update_all_dossiers(reddit_data)
            print(f"[{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S}] [NCAAB Dossier Scheduler] ✅ Dossiers updated")
        except Exception as e:
            print(f"[NCAAB Dossier Scheduler] ⚠️ Error: {e}")


def _loop(app):
    """Internal recurring timer loop (runs every 6 hours)."""
    while True:
        _run_update_once(app)
        for _ in range(6 * 60):
            time.sleep(60)


def start_ncaab_dossier_scheduler(app):
    """Launch background dossier update thread."""
    _init_teams(app)
    t = threading.Thread(target=_loop, args=(app,), name="NCAABDossierScheduler", daemon=True)
    t.start()
    print("[NCAAB Dossier Scheduler] Started background thread")
