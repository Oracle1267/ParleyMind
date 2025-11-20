import json
from pathlib import Path


def load_ncaab_reddit_data():
    """Load NCAAB Reddit data from cache and aggregate by team."""
    cache_path = Path("data/social/reddit_sports.json")
    
    if not cache_path.exists():
        return {}
    
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        ncaab_section = data.get("ncaab", {})
        by_team = ncaab_section.get("by_team", {})
        
        return by_team
    except Exception as e:
        print(f"[Reddit Aggregator] Error loading NCAAB Reddit data: {e}")
        return {}
