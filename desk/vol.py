"""Volatility context: realized vol, IV rank/percentile, expected move."""
import math

def realized_vol(closes, window=20):
    """Annualized close-to-close volatility over the last `window` returns."""
    if len(closes) < window + 1:
        raise ValueError(f"need {window + 1} closes, got {len(closes)}")
    c = closes[-(window + 1):]
    rets = [math.log(c[i] / c[i - 1]) for i in range(1, len(c))]
    mean = sum(rets) / len(rets)
    var = sum((x - mean) ** 2 for x in rets) / (len(rets) - 1)
    return math.sqrt(var * 252)

def iv_rank(history, current):
    """Where current IV sits between the period's low (0) and high (100)."""
    lo, hi = min(history), max(history)
    return 50.0 if hi == lo else 100.0 * (current - lo) / (hi - lo)

def iv_percentile(history, current):
    """Share of days in the period with IV below current (0-100)."""
    return 100.0 * sum(1 for x in history if x < current) / len(history)

def expected_move_from_straddle(call_mid, put_mid):
    """ATM straddle price; the market prices roughly a 1-sd move of ~1.25x this (straddle ~ 0.8 sd)."""
    straddle = call_mid + put_mid
    return {"straddle": straddle, "one_sd": straddle / 0.8}

def expected_move_from_iv(spot, iv, days):
    return spot * iv * math.sqrt(days / 365.0)
