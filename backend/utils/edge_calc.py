def compute_edge(model_prob, market_prob):
    """Return edge in percentage points."""
    return round((model_prob - market_prob) * 100, 2)

def compute_value_index(edge, momentum, sentiment):
    """Weighted blend to identify true value spots."""
    # downweight edge when momentum negative or sentiment euphoric
    sentiment_adj = 1 - abs(sentiment)
    return round(edge * (0.6 + 0.4 * momentum/10) * sentiment_adj, 2)
