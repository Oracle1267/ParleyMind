"""
tradecore_bridge.py
Temporary bridge between ParleyMind and AI_TRADE_CORE.
Currently stubbed — returns neutral risk data.
"""

def get_team_signal(team_name):
    """Return a neutral placeholder signal until AI_TRADE_CORE integration is active."""
    return {
        "team": team_name,
        "sport": "cfb",
        "injuries": [],
        "key_injuries": 0,
        "notes": "team not found",
        "risk_adj": 0.0
    }
