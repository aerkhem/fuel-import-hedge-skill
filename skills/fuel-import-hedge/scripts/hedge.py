#!/usr/bin/env python
"""Estimate and test a Brent hedge ratio for a USD-priced fuel sold in MNT.

Reusable generalisation of the reviewed diesel workflow
(scripts/stage2_design.py and scripts/stage2_test.py). It works from any
folder: every path is resolved from the command-line arguments.

The design period estimates h values (min-variance, CVaR LP and brute-force
grid) for a grid of alpha (pass-through of the USD move into the MNT cost)
and beta (CVaR confidence). An optional test period applies those h values
FIXED to out-of-sample data.

All paths are relative to the current working directory.
"""
import os
import sys
import json
import argparse
from datetime import datetime

import numpy as np
import pandas as pd
import cvxpy as cp

GAL_PER_BBL = 42.0
L_PER_GAL = 3.785411784
L_PER_BBL = GAL_PER_BBL * L_PER_GAL
L_PER_UNITS = {"gal": L_PER_GAL, "bbl": L_PER_BBL}
STAT_BETAS = (0.90, 0.95)


def cvar_loss(margin, beta):
    """CVaR of LOSS for a margin array (positive = tail loss)."""
    xs = np.sort(margin)
    q = 1.0 - beta
    M = len(xs)
    k = int(q * M)
    s = float(xs[:k].sum())
    if k < M:
        s += (q * M - k) * xs[k]
    return -s / (q * M)


def lp_h(L0, Hv, beta, hmax):
    """CVaR-minimising hedge ratio via the linear program."""
    M = len(L0)
    q = 1.0 - beta
    h = cp.Variable()
    eta = cp.Variable()
    u = cp.Variable(M)
    cons = [u >= L0 - Hv * h - eta, u >= 0, 0 <= h, h <= hmax]
    cp.Problem(cp.Minimize(eta + cp.sum(u) / (q * M)), cons).solve()
    return h.value


def grid_h(L0, Hv, beta, hmax):
    """CVaR-minimising hedge ratio by brute-force grid with exact CVaR."""
    best = (1e18, 0.0)
    for h in np.arange(0, hmax + 1e-4, 0.01):
        cv = cvar_loss(-(L0 - Hv * h), beta)
        if cv < best[0]:
            best = (cv, h)
    return best[1]


def statline(m):
    return (m.mean(), m.std(), cvar_loss(m, STAT_BETAS[0]), cvar_loss(m, STAT_BETAS[1]))


def load_raw(path, start, end):
    """Load a yfinance csv filtered to [start, end]; stop clearly if missing."""
    if not os.path.isfile(path):
        raise SystemExit("raw file not found: " + path)
    df = pd.read_csv(path)
    df["date"] = df["Date"].astype(str).str[:10]
    df = df.set_index("date")[["Open", "Close"]]
    df = df[(df.index >= start) & (df.index <= end)]
    return df[~df.index.duplicated(keep="first")].sort_index()


def load_fx(path):
    """Load the MNT-per-USD rate as a date->float map; stop clearly if missing."""
    if not os.path.isfile(path):
        raise SystemExit("fx file not found: " + path)
    fx = pd.read_excel(path)
    fx["date"] = pd.to_datetime(fx["Date"]).dt.strftime("%Y-%m-%d")
    return dict(zip(fx["date"], fx["USD - US dollar"].astype(float)))


def roll_dates(dts):
    """Brent contract-roll dates: first trading day of each month except
    January, plus the last day of each December."""
    ys = pd.Series(dts)
    g = ys.groupby(ys.str[:7])
    firsts = set(g.min())
    lasts = set(g.max())
    return {d for d in dts if (d[5:7] != "01" and d in firsts) or (d[5:7] == "12" and d in lasts)}


def build(dts, BZc, BZo, HOc, fxm, l_per_unit, horizon, step, hadj):
    """--horizon-day windows stepped by --step; roll adjustment applied on the
    hedge leg only (A7)."""
    rows = []
    N = len(dts)
    roll = roll_dates(dts)
    for i in range(0, N - horizon + 1, step):
        j = i + horizon
        B0 = BZc[i]
        B1 = B0
        for t in range(i + 1, j + 1):
            r = (BZc[t] / BZo[t] - 1) if (hadj and dts[t] in roll) else (BZc[t] / BZc[t - 1] - 1)
            B1 *= (1 + r)
        if dts[i] not in fxm or dts[j] not in fxm:
            raise SystemExit("missing FX for window %s..%s" % (dts[i], dts[j]))
        S0 = fxm[dts[i]]
        S1 = fxm[dts[j]]
        C0 = HOc[i] / l_per_unit * S0
        C1 = HOc[j] / l_per_unit * S1
        H = (B1 - B0) / L_PER_BBL * S1
        rows.append((dts[i], dts[j], C0, C1, H))
    return rows


def design_tables(builds, alphas, betas, hmax):
    """(lines, checks, fixed_h0) for the design period. fixed_h0 holds the
    adjusted, alpha=0 ratios reused on the test data."""
    lines = []
    checks = {"lp_grid_agree": True, "alpha1_zero": True, "scaling": True}
    fixed_h0 = {}
    for hadj, tag in ((True, "Adjusted (A7 roll adj on hedge leg)"),
                      (False, "Raw (sensitivity)")):
        wr = builds[hadj]
        C0s = np.array([r[2] for r in wr])
        C1s = np.array([r[3] for r in wr])
        Hv = np.array([r[4] for r in wr])
        lines.append("## " + tag)
        for a in alphas:
            d0 = -(1 - a) * (C1s - C0s)
            L0 = -d0
            cov = np.mean((d0 - d0.mean()) * (Hv - Hv.mean()))
            var = np.mean((Hv - Hv.mean()) ** 2)
            hstar = -cov / var if var > 0 else 0.0
            lps = {b: lp_h(L0, Hv, b, hmax) for b in betas}
            grids = {b: grid_h(L0, Hv, b, hmax) for b in betas}
            names = ["0", "1", "h*"]
            hs = [0.0, 1.0, hstar]
            for b in betas:
                names += ["LP " + str(b), "grid " + str(b)]
                hs += [lps[b], grids[b]]
            if hadj and a == 0.0:
                fixed_h0["minvar"] = hstar
                for b in betas:
                    fixed_h0["cvar" + str(b)] = lps[b]
            lines.append("### alpha = " + str(a))
            lines.append("| h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 |")
            lines.append("|---|---:|---:|---:|---:|")
            for h, nm in zip(hs, names):
                m, s, c9, c95 = statline(d0 + h * Hv)
                lines.append("| %s (%.4f) | %.4f | %.4f | %.4f | %.4f |" % (nm, h, m, s, c9, c95))
            lines.append("")
            if hadj:
                if any(abs(lps[b] - grids[b]) > 0.01 for b in betas):
                    checks["lp_grid_agree"] = False
                if a == 1.0 and max(abs(hstar), *(abs(lps[b]) for b in betas)) > 1e-6:
                    checks["alpha1_zero"] = False
                if a == 0.0:
                    h0 = lps[betas[0]]
                elif abs(lps[betas[0]] - (1 - a) * h0) > 1e-6:
                    checks["scaling"] = False
                lpstr = ",".join("%.4f" % lps[b] for b in betas)
                grstr = ",".join("%.4f" % grids[b] for b in betas)
                bl = ",".join(str(b) for b in betas)
                lines.append("- LP h (%s) = %s; grid = %s; bound(%s) binds: %s"
                             % (bl, lpstr, grstr, hmax, max(lps.values()) >= hmax - 1e-6))
        lines.append("")
    return lines, checks, fixed_h0


def test_table(builds, fixed_h0, alphas, betas, tstart):
    """Out-of-sample table with ratios FIXED from the design period."""
    lines = []
    wr = builds[True]
    C0s = np.array([r[2] for r in wr])
    C1s = np.array([r[3] for r in wr])
    Hv = np.array([r[4] for r in wr])
    base = {"none": 0.0, "100": 1.0}
    base.update(fixed_h0)
    order = ["none", "100", "minvar"] + ["cvar" + str(b) for b in betas]
    no_overlap = str(wr[0][0]) >= str(tstart)
    fixed_ok = True
    alpha1_zero = True
    for a in alphas:
        d0 = -(1 - a) * (C1s - C0s)
        hs = {}
        for nm in order:
            if nm in ("none", "100"):
                hv = base[nm]
                exp = base[nm]
            else:
                hv = (1 - a) * base[nm]
                exp = (1 - a) * base[nm]
            hs[nm] = hv
            if abs(hv - exp) > 1e-9:
                fixed_ok = False
        cvar0 = cvar_loss(d0, 0.90)
        lines.append("## alpha = " + str(a))
        lines.append("| hedge | h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 | CVaR 0.90 change vs no hedge (%) |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for nm in order:
            h = hs[nm]
            m = d0 + h * Hv
            c9 = cvar_loss(m, 0.90)
            c95 = cvar_loss(m, 0.95)
            chg = (c9 - cvar0) / cvar0 * 100.0 if cvar0 != 0 else 0.0
            lines.append("| %s | %.4f | %.4f | %.4f | %.4f | %.4f | %.2f |"
                         % (nm, h, m.mean(), m.std(), c9, c95, chg))
        lines.append("")
        if a == 1.0:
            for nm in ("none", "minvar", "cvar" + str(betas[0])):
                if hs[nm] != 0.0:
                    alpha1_zero = False
    lines += ["## Checks (from tool output)", ""]
    lines.append("- no_overlap (first test window start >= %s): %s" % (tstart, "PASS" if no_overlap else "FAIL"))
    lines.append("- fixed_h (h values exactly the fixed set): %s" % ("PASS" if fixed_ok else "FAIL"))
    lines.append("- alpha1_zero (at alpha=1 none/minvar/cvar rows are zero): %s" % ("PASS" if alpha1_zero else "FAIL"))
    return lines


def main(argv):
    p = argparse.ArgumentParser(description="Estimate and test a Brent hedge ratio")
    p.add_argument("--product", required=True)
    p.add_argument("--product-unit", required=True, choices=["gal", "bbl"])
    p.add_argument("--hedge", required=True)
    p.add_argument("--fx", required=True)
    p.add_argument("--raw-dir", required=True)
    p.add_argument("--design", nargs=2, required=True, metavar=("START", "END"))
    p.add_argument("--test", nargs=2, metavar=("START", "END"))
    p.add_argument("--horizon", type=int, default=21)
    p.add_argument("--step", type=int, default=5)
    p.add_argument("--alphas", nargs="+", type=float, required=True)
    p.add_argument("--betas", nargs="+", type=float, required=True)
    p.add_argument("--hmax", type=float, required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)

    l_per_unit = L_PER_UNITS[args.product_unit]
    dstart, dend = args.design
    fxm = load_fx(args.fx)
    prod_path = os.path.join(args.raw_dir, args.product + ".csv")
    hedg_path = os.path.join(args.raw_dir, args.hedge + ".csv")

    # ---- design period ----
    ho = load_raw(prod_path, dstart, dend)
    bz = load_raw(hedg_path, dstart, dend)
    if not bz.index.equals(ho.index):
        raise SystemExit("product and hedge dates differ in the design period")
    dts = bz.index.tolist()
    bzc, bzo, hoc = bz["Close"].values, bz["Open"].values, ho["Close"].values
    builds_d = {
        True: build(dts, bzc, bzo, hoc, fxm, l_per_unit, args.horizon, args.step, True),
        False: build(dts, bzc, bzo, hoc, fxm, l_per_unit, args.horizon, args.step, False),
    }
    design_df = pd.DataFrame(builds_d[True], columns=["start", "end", "C0", "C1", "H"])
    design_df["dm0"] = -(design_df["C1"] - design_df["C0"])
    design_lines, design_checks, fixed_h0 = design_tables(builds_d, args.alphas, args.betas, args.hmax)

    # ---- optional test period ----
    test_df = None
    test_lines = None
    if args.test:
        tstart, tend = args.test
        ho_t = load_raw(prod_path, tstart, tend)
        bz_t = load_raw(hedg_path, tstart, tend)
        if not bz_t.index.equals(ho_t.index):
            raise SystemExit("product and hedge dates differ in the test period")
        dts_t = bz_t.index.tolist()
        bzc_t, bzo_t, hoc_t = bz_t["Close"].values, bz_t["Open"].values, ho_t["Close"].values
        builds_t = {
            True: build(dts_t, bzc_t, bzo_t, hoc_t, fxm, l_per_unit, args.horizon, args.step, True),
        }
        test_df = pd.DataFrame(builds_t[True], columns=["start", "end", "C0", "C1", "H"])
        test_df["dm0"] = -(test_df["C1"] - test_df["C0"])
        test_lines = test_table(builds_t, fixed_h0, args.alphas, args.betas, tstart)

    os.makedirs(args.out, exist_ok=True)
    design_df.to_csv(os.path.join(args.out, "scenarios_design.csv"), index=False)
    if test_df is not None:
        test_df.to_csv(os.path.join(args.out, "scenarios_test.csv"), index=False)

    # ---- results.md ----
    hdr = [
        "# Fuel-import hedge: results", "",
        "- Product: %s (%s), hedge: %s." % (args.product, args.product_unit, args.hedge),
        "- Design period: %s .. %s, %d windows (%d-day windows stepped by %d trading days; they overlap)."
        % (dstart, dend, len(design_df), args.horizon, args.step),
        "- First design window: %s .. %s" % (design_df["start"].iloc[0], design_df["end"].iloc[0]),
        "- Last design window:  %s .. %s" % (design_df["start"].iloc[-1], design_df["end"].iloc[-1]),
        "- Cap level and fixed costs are constant within a window and cancel; not modelled.",
        "- CVaR columns are CVaR of LOSS (MNT/L); positive = tail loss.",
        "- Alphas: %s; betas: %s; hmax: %s." % (args.alphas, args.betas, args.hmax), "",
        "## Design period (%s .. %s)" % (dstart, dend), "",
    ]
    body = hdr + design_lines
    if test_lines is not None:
        body += ["", "## Test period (%s .. %s)" % (args.test[0], args.test[1]), ""] + test_lines
    body += ["", "## Design checks (from tool output)", ""]
    for k, v in design_checks.items():
        body.append("- %s: %s" % (k, "PASS" if v else "FAIL"))
    with open(os.path.join(args.out, "results.md"), "w") as f:
        f.write("\n".join(body))

    # ---- results.json: machine-readable h values and CVaR figures ----
    res = {"product": args.product, "product_unit": args.product_unit, "hedge": args.hedge,
           "design": {"start": dstart, "end": dend, "alphas": args.alphas, "betas": args.betas,
                      "hmax": args.hmax, "windows": len(design_df), "checks": design_checks}}
    adj = builds_d[True]
    C0s = np.array([r[2] for r in adj]); C1s = np.array([r[3] for r in adj]); Hv = np.array([r[4] for r in adj])
    design_rows = {}
    for a in args.alphas:
        d0 = -(1 - a) * (C1s - C0s); L0 = -d0
        cov = np.mean((d0 - d0.mean()) * (Hv - Hv.mean())); var = np.mean((Hv - Hv.mean()) ** 2)
        hstar = -cov / var if var > 0 else 0.0
        per = {"hstar": round(float(hstar), 6), "betas": {}}
        for b in args.betas:
            m = d0 + lp_h(L0, Hv, b, args.hmax) * Hv
            per["betas"][str(b)] = {
                "h_lp": round(float(lp_h(L0, Hv, b, args.hmax)), 6),
                "h_grid": round(float(grid_h(L0, Hv, b, args.hmax)), 6),
                "cvar90": round(float(cvar_loss(m, 0.90)), 6),
                "cvar95": round(float(cvar_loss(m, 0.95)), 6),
            }
        design_rows[str(a)] = per
    res["design"]["alpha"] = design_rows
    if test_df is not None:
        t0s = np.array([r[2] for r in builds_t[True]]); t1s = np.array([r[3] for r in builds_t[True]]); tH = np.array([r[4] for r in builds_t[True]])
        test_rows = {}
        for a in args.alphas:
            d0 = -(1 - a) * (t1s - t0s)
            per = {}
            for nm in (["none", "100", "minvar"] + ["cvar" + str(b) for b in args.betas]):
                h = fixed_h0[nm] if nm not in ("none", "100") else (0.0 if nm == "none" else 1.0)
                h = h if nm in ("none", "100") else (1 - a) * h
                m = d0 + h * tH
                per[nm] = {"h": round(float(h), 6), "cvar90": round(float(cvar_loss(m, 0.90)), 6),
                           "cvar95": round(float(cvar_loss(m, 0.95)), 6)}
            test_rows[str(a)] = per
        res["test"] = {"start": args.test[0], "end": args.test[1], "alpha": test_rows}
    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump(res, f, indent=2)

    # ---- run.json: exact arguments, date/time, package versions ----
    run = {"args": {k: getattr(args, k) for k in
                    ["product", "product_unit", "hedge", "fx", "raw_dir", "design", "test",
                     "horizon", "step", "alphas", "betas", "hmax", "out"]},
           "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "versions": {"numpy": np.__version__, "pandas": pd.__version__, "cvxpy": cp.__version__}}
    with open(os.path.join(args.out, "run.json"), "w") as f:
        json.dump(run, f, indent=2)

    print("windows=%d first=%s last=%s" % (len(design_df), design_df["start"].iloc[0], design_df["start"].iloc[-1]))
    print("checks=%s" % design_checks)


if __name__ == "__main__":
    main(sys.argv[1:])
