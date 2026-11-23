import numpy as np, pandas as pd, os, cvxpy as cp

GAL_PER_BBL = 42.0; L_PER_GAL = 3.785411784; L_PER_BBL = GAL_PER_BBL * L_PER_GAL
DP0, DP1 = "2021-09-01", "2024-08-31"
ALPHAS = (0.0, 0.25, 0.5, 0.75, 1.0); BETAS = (0.90, 0.95); HBOUND = 2.0

def load_csv(p):
    df = pd.read_csv(p); df["date"] = df["Date"].astype(str).str[:10]
    df = df.set_index("date")[["Open", "Close"]]
    df = df[(df.index >= DP0) & (df.index <= DP1)]
    return df[~df.index.duplicated(keep="first")].sort_index()

bz = load_csv("data/raw/BZ=F.csv"); ho = load_csv("data/raw/HO=F.csv")
assert bz.index.equals(ho.index), "BZ=F and HO=F dates differ in design period"
fx = pd.read_excel("data/raw/bom_currency-rate-USD.xlsx")
fx["date"] = pd.to_datetime(fx["Date"]).dt.strftime("%Y-%m-%d")
fxm = dict(zip(fx["date"], fx["USD - US dollar"].astype(float)))

ys = bz.index.to_series(); g = ys.groupby(ys.str[:7])
firsts = set(g.min()); lasts = set(g.max())
roll = {d for d in bz.index if (d[5:7] != "01" and d in firsts) or (d[5:7] == "12" and d in lasts)}

BZc = bz["Close"].values; BZo = bz["Open"].values; HOc = ho["Close"].values; dts = bz.index.tolist()
N = len(dts)

def build(hadj):
    rows = []
    for i in range(0, N - 21 + 1, 5):
        j = i + 21; B0 = BZc[i]; B1 = B0
        for t in range(i + 1, j + 1):
            r = (BZc[t] / BZo[t] - 1) if (hadj and dts[t] in roll) else (BZc[t] / BZc[t - 1] - 1)
            B1 *= (1 + r)
        if dts[i] not in fxm or dts[j] not in fxm:
            raise SystemExit(f"missing FX for window {dts[i]}..{dts[j]}")
        S0 = fxm[dts[i]]; S1 = fxm[dts[j]]
        C0 = HOc[i] / L_PER_GAL * S0; C1 = HOc[j] / L_PER_GAL * S1
        rows.append((dts[i], dts[j], C0, C1, (B1 - B0) / L_PER_BBL * S1))
    return rows

def cvar_loss(margin, beta):
    xs = np.sort(margin); q = 1.0 - beta; M = len(xs); k = int(q * M)
    s = float(xs[:k].sum())
    if k < M: s += (q * M - k) * xs[k]
    return -s / (q * M)          # CVaR of LOSS (positive MNT/L)

def lp_h(L0, Hv, beta):
    M = len(L0); q = 1.0 - beta
    h = cp.Variable(); eta = cp.Variable(); u = cp.Variable(M)
    cons = [u >= L0 - Hv * h - eta, u >= 0, 0 <= h, h <= HBOUND]
    cp.Problem(cp.Minimize(eta + cp.sum(u) / (q * M)), cons).solve()
    return h.value

def grid_h(L0, Hv, beta):
    best = (1e18, 0.0)
    for h in np.arange(0, 2.0001, 0.01):
        cv = cvar_loss(-(L0 - Hv * h), beta)   # margin = -(loss)
        if cv < best[0]: best = (cv, h)
    return best[1]

def statline(m):
    return (m.mean(), m.std(), cvar_loss(m, 0.90), cvar_loss(m, 0.95))

os.makedirs("outputs", exist_ok=True)
scen = pd.DataFrame(build(True), columns=["start", "end", "C0", "C1", "H"])
scen["dm0"] = -(scen["C1"] - scen["C0"])
scen.to_csv("outputs/stage2_design_scenarios.csv", index=False)

lines = ["# Stage 2 design: diesel hedge ratio (full method, preliminary)", "",
         f"- Windows: {len(scen)} (21-day windows stepped by 5 trading days; they overlap).",
         f"- First window: {scen['start'].iloc[0]} .. {scen['end'].iloc[0]}",
         f"- Last window:  {scen['start'].iloc[-1]} .. {scen['end'].iloc[-1]}",
         "- Cap level and fixed costs are constant within a window and cancel; not modelled.",
         "- CVaR columns are CVaR of LOSS (MNT/L); positive = tail loss.", ""]
checks = {"lp_grid_agree": True, "alpha1_zero": True, "scaling": True}

for hadj in (True, False):
    wr = build(hadj)
    C0s = np.array([r[2] for r in wr]); C1s = np.array([r[3] for r in wr]); Hv = np.array([r[4] for r in wr])
    lines.append(f"## {'Adjusted (A7 roll adj on hedge leg)' if hadj else 'Raw (sensitivity)'}")
    for a in ALPHAS:
        d0 = -(1 - a) * (C1s - C0s); L0 = -d0
        cov = np.mean((d0 - d0.mean()) * (Hv - Hv.mean())); var = np.mean((Hv - Hv.mean()) ** 2)
        hstar = -cov / var if var > 0 else 0.0
        lp90, lp95 = lp_h(L0, Hv, 0.90), lp_h(L0, Hv, 0.95)
        gr90, gr95 = grid_h(L0, Hv, 0.90), grid_h(L0, Hv, 0.95)
        hs = [0.0, 1.0, hstar, lp90, gr90, lp95, gr95]
        names = ["0", "1", "h*", "LP 0.90", "grid 0.90", "LP 0.95", "grid 0.95"]
        lines.append(f"### alpha = {a:g}")
        lines.append("| h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 |")
        lines.append("|---|---:|---:|---:|---:|")
        for h, nm in zip(hs, names):
            m, s, c9, c95 = statline(d0 + h * Hv)
            lines.append(f"| {nm} ({h:.4f}) | {m:.4f} | {s:.4f} | {c9:.4f} | {c95:.4f} |")
        lines.append("")
        if hadj:
            if abs(lp90 - gr90) > 0.01 or abs(lp95 - gr95) > 0.01: checks["lp_grid_agree"] = False
            if a == 1.0 and max(abs(hstar), abs(lp90), abs(lp95)) > 1e-6: checks["alpha1_zero"] = False
            if a == 0.0: h0 = lp90
            elif abs(lp90 - (1 - a) * h0) > 1e-6: checks["scaling"] = False
            lines.append(f"- LP h (0.90,0.95) = {lp90:.4f},{lp95:.4f}; grid = {gr90:.4f},{gr95:.4f}; bound(2.0) binds: {max(lp90,lp95) >= HBOUND-1e-6}")
    lines.append("")

lines += ["## Checks (from tool output)", ""]
for k, v in checks.items():
    lines.append(f"- {k}: {'PASS' if v else 'FAIL'}")
open("outputs/stage2_design_results.md", "w").write("\n".join(lines))

print(f"windows={len(scen)} first={scen['start'].iloc[0]} last={scen['start'].iloc[-1]}")
print(f"checks={checks}")
for a in ALPHAS:
    d0 = -(1 - a) * (scen.C1 - scen.C0).values; Hv = scen.H.values
    lp90, lp95 = lp_h(-d0, Hv, 0.90), lp_h(-d0, Hv, 0.95)
    gr90, gr95 = grid_h(-d0, Hv, 0.90), grid_h(-d0, Hv, 0.95)
    print(f"alpha={a:g} h*={-np.mean((d0-d0.mean())*(Hv-Hv.mean()))/np.mean((Hv-Hv.mean())**2):.4f} "
          f"lp={lp90:.4f}/{lp95:.4f} grid={gr90:.4f}/{gr95:.4f}")
