"""
utils_odds.py — odds and probability conversions (moneyline + Kalshi YES).
"""

def american_to_prob(odds: int) -> float:
    """
    Convert American odds to implied probability.
    +A -> 100 / (A + 100)
    -A -> A / (A + 100)
    """
    if odds == 0:
        return 0.0
    if odds > 0:
        return 100.0 / (odds + 100.0)
    return (-odds) / ((-odds) + 100.0)

def prob_to_american(p: float) -> int:
    """
    Convert probability to American odds (rounded).
    """
    if p <= 0 or p >= 1:
        return 0
    if p < 0.5:
        # positive odds
        return int(round(100.0 * (1.0 - p) / p))
    else:
        # negative odds
        return int(round(-1.0 * (p / (1.0 - p)) * 100.0))

def kalshi_yes_to_prob(price_cents: float, fee_rate: float = 0.0) -> float:
    """
    Convert Kalshi YES price (0–100) to implied probability. Optional fee adjustment.
    If fee_rate>0, reduce expected value slightly by multiplying (1 - fee_rate).
    """
    p = max(0.0, min(1.0, price_cents / 100.0))
    adj = max(0.0, min(1.0, (1.0 - fee_rate)))
    return p * adj
