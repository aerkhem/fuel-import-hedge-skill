"""Independent check of Stage 2 (diesel hedged with Brent).

Written by Claude (Anthropic), a separate AI assistant, NOT by the WorkSwarm
agent, to verify scripts/stage2_design.py and scripts/stage2_test.py by a
different method:
  - prices read with the csv module, not pandas;
  - Brent roll days from calendar-month boundaries (assumptions.md, A7);
  - CVaR computed by sorting, and the LP solved with scipy's HiGHS, not cvxpy.

Run from the repo root:
  python scripts/verify_stage2.py                      # diesel (HO=F), defaults
  python scripts/verify_stage2.py --product RB=F       # gasoline, same periods
Options: --product, --product-unit gal|bbl, --hedge, --raw-dir, --fx,
--design START END, --test START END.
Prints design-period hedge ratios, then the out-of-sample test with those
ratios held fixed. Compare by hand with the results file of the run checked.
"""
import argparse
import csv

import numpy as np
import pandas as pd
from scipy.optimize import linprog

ap = argparse.ArgumentParser()
ap.add_argument("--product", default="HO=F")
ap.add_argument("--product-unit", default="gal", choices=["gal", "bbl"])
ap.add_argument("--hedge", default="BZ=F")
ap.add_argument("--raw-dir", default="data/raw")
ap.add_argument("--fx", default="data/raw/bom_currency-rate-USD.xlsx")
ap.add_argument("--design", nargs=2, default=["2021-09-01", "2024-08-31"])
ap.add_argument("--test", nargs=2, default=["2024-09-01", "2026-08-31"])
args = ap.parse_args()

RAW = args.raw_dir
L_PER_GAL = 3.785411784
L_PER_BBL = 42 * L_PER_GAL
L_PER_UNIT = L_PER_GAL if args.product_unit == "gal" else L_PER_BBL
HORIZON, STEP = 21, 5
DESIGN = tuple(args.design)
TEST = tuple(args.test)
ALPHAS = [0, 0.25, 0.5, 0.75, 1]


def load(ticker):
    rows = list(csv.DictReader(open(f"{RAW}/{ticker}.csv")))
    return ([r["Date"][:10] for r in rows],
            np.array([float(r["Open"]) for r in rows]),
            np.array([float(r["Close"]) for r in rows]))


dates, oB, cB = load(args.hedge)
dH, _, cH = load(args.product)
assert dates == dH, f"{args.hedge} and {args.product} dates differ"

bom = pd.read_excel(args.fx)
fx = dict(zip(pd.to_datetime(bom["Date"]).dt.strftime("%Y-%m-%d"),
              bom["USD - US dollar"].astype(float)))

# Brent roll days: first trading row of each month except January, plus the
# last trading row of December (A7).
roll = set()
for i in range(1, len(dates)):
    if dates[i][:7] != dates[i - 1][:7] and dates[i][5:7] != "01":
        roll.add(i)
    if dates[i][5:7] == "12" and (i + 1 == len(dates) or dates[i + 1][:7] != dates[i][:7]):
        roll.add(i)


def brent_returns(adjust):
    r = np.zeros(len(cB))
    for i in range(1, len(cB)):
        r[i] = cB[i] / oB[i] - 1 if (adjust and i in roll) else cB[i] / cB[i - 1] - 1
    return r


def scenarios(period, adjust=True):
    lo, hi = period
    rows = [i for i, d in enumerate(dates) if lo <= d <= hi]
    starts = range(rows[0], rows[-1] - HORIZON + 1, STEP)
    rB = brent_returns(adjust)
    dC, H, first, last = [], [], None, None
    for i in starts:
        j = i + HORIZON
        S0, S1 = fx[dates[i]], fx[dates[j]]
        b1 = cB[i] * np.prod(1 + rB[i + 1:j + 1])
        dC.append(cH[j] / L_PER_UNIT * S1 - cH[i] / L_PER_UNIT * S0)
        H.append((b1 - cB[i]) / L_PER_BBL * S1)
        first = first or (dates[i], dates[j]); last = (dates[i], dates[j])
    return np.array(dC), np.array(H), first, last


def cvar(loss, beta):
    m = len(loss); tail = (1 - beta) * m; k = int(np.floor(tail))
    s = np.sort(loss)[::-1]
    return (s[:k].sum() + (tail - k) * (s[k] if k < m else 0.0)) / tail


def lp_hedge(X, H, beta):
    """min eta + sum(u)/((1-beta)M) s.t. u >= X - h*H - eta, u >= 0, 0 <= h <= 2."""
    m = len(X)
    c = np.r_[0.0, 1.0, np.full(m, 1 / ((1 - beta) * m))]
    A = np.zeros((m, m + 2)); A[:, 0] = -H; A[:, 1] = -1; A[np.arange(m), 2 + np.arange(m)] = -1
    res = linprog(c, A_ub=A, b_ub=-X, bounds=[(0, 2), (None, None)] + [(0, None)] * m, method="highs")
    return float(res.x[0])


def describe(margin):
    return (f"mean {margin.mean():8.2f}  sd {margin.std():8.2f}  "
            f"CVaR90 {cvar(-margin, 0.90):8.2f}  CVaR95 {cvar(-margin, 0.95):8.2f}")


dC_d, H_d, f_d, l_d = scenarios(DESIGN)
dC_t, H_t, f_t, l_t = scenarios(TEST)
print(f"Product {args.product} ({args.product_unit}), hedge {args.hedge}")
print(f"Design: {len(dC_d)} windows, {f_d[0]}..{f_d[1]} to {l_d[0]}..{l_d[1]}")
print(f"Test:   {len(dC_t)} windows, {f_t[0]}..{f_t[1]} to {l_t[0]}..{l_t[1]}")

for a in ALPHAS:
    X_d = (1 - a) * dC_d                       # design loss without hedge
    if a == 1:
        hedges = {"none": 0.0, "100%": 1.0, "min-var": 0.0, "CVaR90": 0.0, "CVaR95": 0.0}
    else:
        hedges = {"none": 0.0, "100%": 1.0,
                  "min-var": np.cov(X_d, H_d)[0, 1] / np.var(H_d, ddof=1),
                  "CVaR90": lp_hedge(X_d, H_d, 0.90),
                  "CVaR95": lp_hedge(X_d, H_d, 0.95)}
    print(f"\nalpha = {a}")
    for name, h in hedges.items():
        m_d = -X_d + h * H_d
        m_t = -(1 - a) * dC_t + h * H_t
        print(f"  {name:8s} h={h:6.4f} | design {describe(m_d)}")
        print(f"  {'':8s} {'':8s} | TEST   {describe(m_t)}")
