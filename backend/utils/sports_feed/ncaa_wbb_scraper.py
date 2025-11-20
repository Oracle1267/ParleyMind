import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.ncaa.com/scoreboard/basketball-women/d1"

def fetch_wbb_games():
    """Scrape the NCAA women's basketball scoreboard."""
    res = requests.get(BASE_URL, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    games = []
    for matchup in soup.select(".gamePod"):
        home = matchup.select_one(".gamePod-game-team-home .gamePod-game-team-name").get_text(strip=True)
        away = matchup.select_one(".gamePod-game-team-away .gamePod-game-team-name").get_text(strip=True)
        status = matchup.select_one(".gamePod-status").get_text(strip=True)
        games.append({
            "home_team": home,
            "away_team": away,
            "status": status,
            "commence_time": datetime.utcnow().isoformat(),
            "markets": [],  # no odds yet
            "source": "NCAA_WBB"
        })
    return games
