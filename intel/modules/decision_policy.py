"""
decision_policy.py — minimal policy for bet/no-bet, venue, and stake.
"""
from dataclasses import dataclass
from typing import Optional, Dict
from .utils_odds import american_to_prob, kalshi_yes_to_prob
from .kelly_sizer import kelly_fraction

@dataclass
class Decision:
    bet: bool
    venue: Optional[str]
    stake_fraction: float
    reason: str
    details: Dict

DEFAULTS = {"min_edge": 0.035, "min_conf": 0.60}

def decide(p_model: float, p_fanduel: float, p_kalshi: float, p_consensus: float, conf: float, thresholds: Dict = None) -> Decision:
    t = {**DEFAULTS, **(thresholds or {})}
    # choose better price
    venue, p_book = ("FanDuel", p_fanduel) if p_fanduel <= p_kalshi else ("Kalshi", p_kalshi)
    edge = p_model - p_book
    if (p_model - p_consensus) < 0:
        return Decision(False, None, 0.0, "model_below_consensus", {"p_model":p_model, "p_consensus":p_consensus})
    if edge < t["min_edge"]:
        return Decision(False, None, 0.0, "edge_below_threshold", {"edge": edge})
    if conf < t["min_conf"]:
        return Decision(False, None, 0.0, "confidence_below_threshold", {"conf": conf})
    stake = kelly_fraction(p_model, p_book, conf)
    if stake <= 0:
        return Decision(False, None, 0.0, "non_positive_kelly", {"p_model": p_model, "p_book": p_book})
    return Decision(True, venue, stake, "ok", {"edge": edge, "p_book": p_book})
