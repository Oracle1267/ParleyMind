from .ncaa_wbb_scraper import fetch_wbb_games
from .ncaa_wvb_scraper import fetch_wvb_games

def get_feed_for_sport(sport_key: str):
    sport_key = sport_key.lower()
    if sport_key in ["wncaab", "wbb", "basketball_women"]:
        return fetch_wbb_games()
    elif sport_key in ["wvb", "volleyball", "volleyball_women"]:
        return fetch_wvb_games()
    else:
        raise ValueError(f"Unsupported direct-feed sport: {sport_key}")
