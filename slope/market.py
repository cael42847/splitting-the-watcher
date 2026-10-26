#!/usr/bin/env python3
"""market.py — the logit Bertrand market of Calvano et al. (AER 2020), the workhorse of the
LLM-collusion papers (Fish et al. 2024; Lee 2026). Computes, BEFORE any agent plays, the terrain:
the competitive (Nash) price, the monopoly (joint-profit) price, and the SLOPE = the prize for
sliding, i.e. how much more each seller earns at the monopoly price than in competition.

Demand for firm i:  q_i = exp((a - p_i)/mu) / ( sum_j exp((a - p_j)/mu) + exp(a0/mu) )
Profit:             pi_i = (p_i - c) * q_i
mu = horizontal differentiation: small mu = buyers very price-sensitive (near-perfect substitutes,
Bertrand-like); large mu = buyers barely look at price. (Corrected 2026-10-13 after the cold read:
the first comment said small mu meant a flat terrain with little to gain; the table shows the
opposite for the prize — competition crushes profit, so the relative prize for sliding is largest.)  Marion's definition, 2026-10-13: the slope is the environment, set
before anything happens; the market's behaviour is the consequence, measured after.
"""
import math, argparse

def demand(prices, i, a=2.0, a0=0.0, mu=0.25):
    num = math.exp((a - prices[i]) / mu)
    den = sum(math.exp((a - p) / mu) for p in prices) + math.exp(a0 / mu)
    return num / den

def consumer_surplus(prices, a=2.0, a0=0.0, mu=0.25):
    """Logit consumer surplus (up to a constant): mu * ln( sum_j exp((a - p_j)/mu) + exp(a0/mu) )."""
    return mu * math.log(sum(math.exp((a - p) / mu) for p in prices) + math.exp(a0 / mu))

def profit(prices, i, c=1.0, **kw):
    return (prices[i] - c) * demand(prices, i, **kw)

def best_response(p_others, n, c=1.0, **kw):
    lo, hi = c, c + 10.0
    best, bp = -1, c
    for k in range(4001):
        p = lo + (hi - lo) * k / 4000
        pr = profit([p] + p_others, 0, c=c, **kw)
        if pr > best: best, bp = pr, p
    return bp

def nash_price(n, c=1.0, **kw):
    p = c + 0.5
    for _ in range(200):
        newp = best_response([p] * (n - 1), n, c=c, **kw)
        if abs(newp - p) < 1e-6: break
        p = 0.5 * p + 0.5 * newp
    return p

def monopoly_price(n, c=1.0, **kw):
    best, bp = -1, c
    for k in range(4001):
        p = c + 10.0 * k / 4000
        tot = sum(profit([p] * n, i, c=c, **kw) for i in range(n))
        if tot > best: best, bp = tot, p
    return bp

def terrain(n, mu, c=1.0, a=2.0, a0=0.0):
    kw = dict(a=a, a0=a0, mu=mu)
    pn, pm = nash_price(n, c=c, **kw), monopoly_price(n, c=c, **kw)
    prn = profit([pn] * n, 0, c=c, **kw); prm = profit([pm] * n, 0, c=c, **kw)
    # the gain for breaking ranks: cut while the others stay at the monopoly price
    pd = best_response([pm] * (n - 1), n, c=c, **kw); prd = profit([pd] + [pm] * (n - 1), 0, c=c, **kw)
    return dict(n=n, mu=mu, p_nash=round(pn, 4), p_mono=round(pm, 4),
                profit_nash=round(prn, 4), profit_mono=round(prm, 4),
                slope=round((prm - prn) / prn, 3),          # prize for sliding, relative to competing
                breakaway=round((prd - prm) / prm, 3),      # extra gain for the one who cuts
                # THE ANGLE (grim-trigger folk theorem): how much the future must weigh for sliding to hold.
                # delta* = (pi_breakaway - pi_mono) / (pi_breakaway - pi_nash). Low = a steep slope:
                # even a short future keeps the snow sliding. High = the slope holds only with a long future.
                delta_star=round((prd - prm) / (prd - prn), 3))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, nargs="+", default=[2, 3, 5])
    ap.add_argument("--mu", type=float, nargs="+", default=[0.05, 0.1, 0.25, 0.5, 1.0])
    a = ap.parse_args()
    print("n   mu     p_nash  p_mono  prize   breakaway  delta*")
    for n in a.n:
        for mu in a.mu:
            t = terrain(n, mu)
            print(f"{n:<3} {mu:<6} {t['p_nash']:<7} {t['p_mono']:<7} {t['slope']:<7} {t['breakaway']:<10} {t['delta_star']}")
