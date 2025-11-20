"""
ParleyMind Scout v1.1
=====================
Automatically discovers NCAAB team stats URLs for each Division I school
and logs both successes and failures.

Usage:
    python -m backend.utils.discover_team_stats_urls
"""

import os
import csv
import sqlite3
import requests
from datetime import datetime

# === CONFIGURATION ===
DB_PATH = r"C:\Projects\parleymind\backend\instance\parlaymind.db"
OUTPUT_CSV = r"C:\Projects\parleymind\data\team_stats_links.csv"
FAILURE_LOG = r"C:\Projects\parleymind\data\team_stats_failures.csv"

CANDIDATE_PATHS = [
    "/sports/mens-basketball/stats",
    "/sports/m-baskbl/stats",
    "/sports/mbball/stats",
    "/sport/m-baskbl/stats",
    "/sports/men/basketball/stats",
    "/sports/m-basketball/stats",
]

TEAM_DOMAINS = [
    ("American University Eagles", "aueagles.com"),
    ("Arizona State Sun Devils", "thesundevils.com"),
    ("Arizona Wildcats", "arizonawildcats.com"),
    ("Arkansas Razorbacks", "arkansasrazorbacks.com"),
    ("Auburn Tigers", "auburntigers.com"),
    ("Bellarmine Knights", "athletics.bellarmine.edu"),
]


def init_db():
    """Ensure database and table exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team_stats_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT,
            domain TEXT,
            stats_url TEXT,
            last_checked DATETIME
        );
    """)
    conn.commit()
    conn.close()


def find_valid_url(domain: str) -> str:
    """Try common paths until one returns valid HTML."""
    for path in CANDIDATE_PATHS:
        url = f"https://{domain}{path}"
        try:
            r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and "stats" in r.text.lower():
                print(f"✅ Found valid stats page for {domain}: {url}")
                return url
        except Exception as e:
            print(f"⚠️ {domain}{path} -> {e}")
    print(f"❌ No valid stats page for {domain}")
    return None


def main():
    print("=== 🏀 ParleyMind Scout v1.1: NCAA Stats URL Discovery ===")
    init_db()

    results, failures = [], []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for team_name, domain in TEAM_DOMAINS:
        url = find_valid_url(domain)
        timestamp = datetime.utcnow()
        if url:
            results.append((team_name, domain, url, timestamp))
            cur.execute("""
                INSERT INTO team_stats_sources (team_name, domain, stats_url, last_checked)
                VALUES (?, ?, ?, ?)
            """, (team_name, domain, url, timestamp))
        else:
            failures.append((team_name, domain, timestamp))
        conn.commit()

    conn.close()

    # --- Write success CSV ---
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Team Name", "Domain", "Stats URL", "Last Checked"])
        writer.writerows(results)

    # --- Write failure CSV ---
    os.makedirs(os.path.dirname(FAILURE_LOG), exist_ok=True)
    with open(FAILURE_LOG, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Team Name", "Domain", "Last Checked"])
        writer.writerows(failures)

    print(f"\n📄 Saved {len(results)} successes to: {OUTPUT_CSV}")
    print(f"⚠️ Logged {len(failures)} failures to: {FAILURE_LOG}")
    print(f"💾 Database updated: {DB_PATH}")
    print("✅ Done.\n")


if __name__ == "__main__":
    main()
