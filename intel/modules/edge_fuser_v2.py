"""
edge_fuser_v2.py — combine market anchor + stats to produce p_model, edge, confidence.

Public function:
    fuse(row: dict) -> dict  # pure function usable in pandas or per-row loops
"""
import math

def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def _clamp(x, lo, hi):
    return max(lo, min(hi, x))

DEFAULT_WEIGHTS = {
    "w_form": 0.20,
    "w_strength": 0.02,
    "w_bias": 0.0
}

def fuse(row: dict, weights: dict = None) -> dict:
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    p_market = _clamp(float(row.get("p_market_consensus", 0.5)), 1e-6, 1-1e-6)
    form = _clamp(float(row.get("form_last5_net", 0.0)), -30.0, 30.0)
    strength = _clamp(float(row.get("ppg", 0.0)) - float(row.get("opp_ppg", 0.0)), -30.0, 30.0)

    market_logit = math.log(p_market / (1.0 - p_market))
    model_logit = market_logit + w["w_bias"] + w["w_form"] * (form/10.0) + w["w_strength"] * (strength/10.0)
    p_model = _sigmoid(model_logit)

    # crude confidence proxy (replace later): magnitude + data presence
    mag = min(1.0, (abs(form) + abs(strength)) / 40.0)  # 0..1
    conf = 0.5 + 0.5 * mag  # 0.5..1.0

    p_fanduel = float(row.get("p_fanduel_entry", 0.0)) or p_market
    p_kalshi  = float(row.get("p_kalshi_entry", 0.0)) or p_market
    p_book = min(p_fanduel, p_kalshi)  # better price (lower implied) for a pick-to-win
    edge = p_model - p_book

    return {
        "p_model": p_model,
        "edge": edge,
        "conf": conf
    }
