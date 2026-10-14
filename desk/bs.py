"""Black-Scholes-Merton pricing, Greeks and implied volatility (European, continuous dividend yield).

Units, per share (multiply by 100 for one contract):
  delta, gamma   per $1 move in the stock
  theta          $ per calendar day
  vega           $ per 1 volatility point (0.01)
  rho            $ per 1 rate point (0.01)
American early exercise is ignored; fine for the short-dated, mostly OTM contracts we trade.
"""
import math

def _cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def _pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

def _d1d2(S, K, T, sigma, r, q):
    v = sigma * math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / v
    return d1, d1 - v

def price(kind, S, K, T, sigma, r=0.0, q=0.0):
    """kind: 'call' or 'put'. T in years."""
    if T <= 0 or sigma <= 0:
        return max(0.0, S - K) if kind == "call" else max(0.0, K - S)
    d1, d2 = _d1d2(S, K, T, sigma, r, q)
    if kind == "call":
        return S * math.exp(-q * T) * _cdf(d1) - K * math.exp(-r * T) * _cdf(d2)
    return K * math.exp(-r * T) * _cdf(-d2) - S * math.exp(-q * T) * _cdf(-d1)

def greeks(kind, S, K, T, sigma, r=0.0, q=0.0):
    if T <= 0 or sigma <= 0:
        itm = (S > K) if kind == "call" else (S < K)
        d = (1.0 if kind == "call" else -1.0) if itm else 0.0
        return {"delta": d, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}
    d1, d2 = _d1d2(S, K, T, sigma, r, q)
    dq, dr, sq = math.exp(-q * T), math.exp(-r * T), math.sqrt(T)
    gamma = dq * _pdf(d1) / (S * sigma * sq)
    vega = S * dq * _pdf(d1) * sq
    common = -S * dq * _pdf(d1) * sigma / (2 * sq)
    if kind == "call":
        delta = dq * _cdf(d1)
        theta = common - r * K * dr * _cdf(d2) + q * S * dq * _cdf(d1)
        rho = K * T * dr * _cdf(d2)
    else:
        delta = -dq * _cdf(-d1)
        theta = common + r * K * dr * _cdf(-d2) - q * S * dq * _cdf(-d1)
        rho = -K * T * dr * _cdf(-d2)
    return {"delta": delta, "gamma": gamma, "theta": theta / 365.0,
            "vega": vega / 100.0, "rho": rho / 100.0}

def implied_vol(kind, premium, S, K, T, r=0.0, q=0.0, lo=1e-4, hi=5.0, tol=1e-7):
    """Bisection on sigma. Returns None if the premium is outside no-arbitrage bounds."""
    if T <= 0 or premium <= 0:
        return None
    if premium < price(kind, S, K, T, lo, r, q) - tol or premium > price(kind, S, K, T, hi, r, q):
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if price(kind, S, K, T, mid, r, q) > premium:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)
