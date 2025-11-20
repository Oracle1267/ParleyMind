# backend/utils/context_fetcher.py
import requests

ESPN_SPORT_KEY = {
    "nfl": "football/nfl",
    "cfb": "football/college-football",
}

def _find_team_id_caseless(league_json, team_name: str):
    """Find a team id in ESPN teams payload by fuzzy name contains (case-insensitive)."""
    try:
        leagues = league_json.get("sports", [])[0].get("leagues", [])
        if not leagues:
            return None
        teams = leagues[0].get("teams", [])
        team_name_l = team_name.lower()
        for t in teams:
            name = t["team"]["displayName"]
            if team_name_l in name.lower():
                return t["team"]["id"]
    except Exception:
        return None
    return None

def get_team_injuries(team_name: str, sport: str = "cfb", timeout: float = 6.0):
    """
    Returns a compact injury summary for a team using ESPN public endpoints.
    sport: "cfb" or "nfl"
    """
    sport_key = ESPN_SPORT_KEY.get(sport.lower())
    if not sport_key:
        return {"team": team_name, "sport": sport, "injuries": [], "key_injuries": 0, "notes": "unsupported sport"}

    base = f"https://site.api.espn.com/apis/site/v2/sports/{sport_key}"
    # 1) get teams for league (to map display name -> team id)
    try:
        teams_resp = requests.get(f"{base}/teams", timeout=timeout)
        teams_resp.raise_for_status()
        tid = _find_team_id_caseless(teams_resp.json(), team_name)
        if not tid:
            return {"team": team_name, "sport": sport, "injuries": [], "key_injuries": 0, "notes": "team not found"}
    except Exception as e:
        return {"team": team_name, "sport": sport, "injuries": [], "key_injuries": 0, "notes": f"teams err: {e}"}

    # 2) get injuries for that team id
    try:
        inj_resp = requests.get(f"{base}/teams/{tid}/injuries", timeout=timeout)
        inj_resp.raise_for_status()
        data = inj_resp.json()
    except Exception as e:
        return {"team": team_name, "sport": sport, "injuries": [], "key_injuries": 0, "notes": f"inj err: {e}"}

    injuries = []
    # ESPN returns groupings; flatten to a simple list
    for group in data.get("injuries", []):
        for item in group.get("injuries", []):
            status = item.get("status")  # e.g., "Out", "Questionable", "Doubtful", "Available"
            athlete = (item.get("athlete") or {}).get("displayName")
            pos = (item.get("athlete") or {}).get("position", {}).get("abbreviation")
            desc = item.get("details")
            injuries.append({
                "name": athlete,
                "pos": pos,
                "status": status,
                "desc": desc
            })

    # "Key" = likely-to-impact statuses:
    key_statuses = {"Out", "Doubtful", "Questionable"}
    key_injuries = sum(1 for i in injuries if i.get("status") in key_statuses)

    # keep top 3 names for UI note
    headline = ", ".join([i["name"] for i in injuries if i.get("status") in key_statuses and i.get("name")][:3])

    return {
        "team": team_name,
        "sport": sport.lower(),
        "injuries": injuries,
        "key_injuries": key_injuries,
        "headline": headline,     # short comma-separated list
        "notes": ""               # reserved for additional context
    }
