import requests
import time
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("teamrankings_scraper")
logger.setLevel(logging.INFO)

BASE_URL = "https://www.teamrankings.com/ncaa-basketball"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

STAT_ENDPOINTS = {
    "ppg": "/stat/points-per-game",
    "ppg_allowed": "/stat/points-allowed-per-game",
    "home_ppg": "/stat/home-points-per-game",
    "away_ppg": "/stat/away-points-per-game",
}


def _fetch_page(url):
    """Fetch and parse a TeamRankings page."""
    try:
        time.sleep(2)
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")
        return None


def _parse_stat_table(soup, stat_type):
    """Extract team stats from a TeamRankings table."""
    stats = {}
    try:
        table = soup.find("table", {"class": "tr-table scrollable"})
        if not table:
            return stats
        
        rows = table.find_all("tr")[1:]
        for row in rows[:100]:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            
            team_cell = cols[0].find("a")
            if not team_cell:
                continue
            
            team_name = team_cell.get_text(strip=True)
            try:
                value = float(cols[1].get_text(strip=True))
                stats[team_name] = value
            except ValueError:
                pass
    except Exception as e:
        logger.warning(f"Error parsing {stat_type}: {e}")
    
    return stats


def fetch_team_stats():
    """Fetch all rolling stats for all teams."""
    all_stats = {}
    
    for stat_type, endpoint in STAT_ENDPOINTS.items():
        logger.info(f"Fetching {stat_type}...")
        url = BASE_URL + endpoint
        soup = _fetch_page(url)
        
        if not soup:
            logger.warning(f"Could not fetch {stat_type}, skipping")
            continue
        
        stats = _parse_stat_table(soup, stat_type)
        all_stats[stat_type] = stats
        logger.info(f"  → {len(stats)} teams found for {stat_type}")
    
    return all_stats


def get_team_stat(team_name, stat_type, all_stats):
    """Get a specific stat for a team from the fetched data."""
    if stat_type not in all_stats:
        return None
    
    stats_dict = all_stats[stat_type]
    if team_name in stats_dict:
        return stats_dict[team_name]
    
    for key in stats_dict:
        if team_name.lower() in key.lower() or key.lower() in team_name.lower():
            return stats_dict[key]
    
    return None
