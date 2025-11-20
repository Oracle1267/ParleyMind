"""
kelly_sizer.py — bounded Kelly for binary outcomes.
"""
from typing import Dict

DEFAULT_CAPS = {
    "0.60-0.69": 0.005,
    "0.70-0.79": 0.01,
    "0.80-1.00": 0.02,
}

def _cap(conf: float, caps: Dict[str, float]) -> float:
    if conf < 0.60: return 0.0
    if conf < 0.70: return caps.get("0.60-0.69", 0.005)
    if conf < 0.80: return caps.get("0.70-0.79", 0.01)
    return caps.get("0.80-1.00", 0.02)

def kelly_fraction(p_model: float, p_book: float, conf: float, caps: Dict[str, float] = None) -> float:
    caps = caps or DEFAULT_CAPS
    if not (0 <= p_model <= 1 and 0 <= p_book <= 1 and 0 <= conf <= 1):
        return 0.0
    if p_book in (0.0, 1.0):
        return 0.0
    b = (1.0 / p_book) - 1.0
    q = 1.0 - p_model
    f_raw = ((b * p_model) - q) / b
    if f_raw <= 0:
        return 0.0
    return min(f_raw * conf, _cap(conf, caps))
