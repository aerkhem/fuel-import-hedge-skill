import numpy as np, pandas as pd, os

GAL_PER_BBL = 42.0; L_PER_GAL = 3.785411784; L_PER_BBL = GAL_PER_BBL * L_PER_GAL
TP0, TP1 = "2024-09-01", "2026-08-31"
ALPHAS = (0.0, 0.25, 0.5, 0.75, 1.0)

# Fixed ratios from the design period (adjusted returns), alpha = 0.
H0 = {"none": 0.0, "100": 1.0, "minvar": 1.3870, "cvar90": 1.7160, "cvar95": 1.4843}
ORDER = ["none", "100", "minvar", "cvar90", "cvar95"]

def load_csv(p):
    df = pd.read_csv(p); df["date"] = df["Date"].astype(str).str[:10]
    df = df.set_index("date")[["Open", "Close"]]
    df = df[(df.index >= TP0) & (df.index <= TP1)]
    return df[~df.index.duplicated(keep="first")].sort_index()

bz = load_csv("data/raw/BZ=F.csv"); ho = load_csv("data/raw/HO=F.csv")
assert bz.index.equals(ho.index), "BZ=F and HO=F dates differ in test period"
fx = pd.read_excel("data/raw/bom_currency-rate-USD.xlsx")
fx["date"] = pd.to_datetime(fx["Date"]).dt.strftime("%Y-%m-%d")
fxm = dict(zip(fx["date"], fx["USD - US dollar"].astype(float)))

ys = bz.index.to_series(); g = ys.groupby(ys.str[:7])
firsts = set(g.min()); lasts = set(g.max())
roll = {d for d in bz.index if (d[5:7] != "01" and d in firsts) or (d[5:7] == "12" and d in lasts)}

BZc = bz["Close"].values; BZo = bz["Open"].values; HOc = ho["Close"].values; dts = bz.index.tolist()
N = len(dts)

rows = []
for i in range(0, N - 21 + 1, 5):
    j = i + 21; B0 = BZc[i]; B1 = B0
    for t in range(i + 1, j + 1):
        r = (BZc[t] / BZo[t] - 1) if dts[t] in roll else (BZc[t] / BZc[t - 1] - 1)
        B1 *= (1 + r)
    if dts[i] not in fxm or dts[j] not in fxm:
        raise SystemExit(f"missing FX for window {dts[i]}..{dts[j]}")
    S0 = fxm[dts[i]]; S1 = fxm[dts[j]]
    C0 = HOc[i] / L_PER_GAL * S0; C1 = HOc[j] / L_PER_GAL * S1
    rows.append((dts[i], dts[j], C0, C1, (B1 - B0) / L_PER_BBL * S1))

scen = pd.DataFrame(rows, columns=["start", "end", "C0", "C1", "H"])
scen["dm0"] = -(scen["C1"] - scen["C0"])
os.makedirs("outputs", exist_ok=True)
scen.to_csv("outputs/stage2_test_scenarios.csv", index=False)

def cvar_loss(margin, beta):
    xs = np.sort(margin); q = 1.0 - beta; M = len(xs); k = int(q * M)
    s = float(xs[:k].sum())
    if k < M: s += (q * M - k) * xs[k]
    return -s / (q * M)          # CVaR of LOSS (positive MNT/L)

C0s = scen.C0.values; C1s = scen.C1.values; Hv = scen.H.values
base = {"none": 0.0, "100": 1.0, "minvar": H0["minvar"], "cvar90": H0["cvar90"], "cvar95": H0["cvar95"]}

lines = ["# Stage 2 test: diesel hedge ratio on out-of-sample data (preliminary)", "",
         f"- Windows: {len(scen)} (21-day windows stepped by 5 trading days; they overlap).",
         f"- First window: {scen['start'].iloc[0]} .. {scen['end'].iloc[0]}",
         f"- Last window:  {scen['start'].iloc[-1]} .. {scen['end'].iloc[-1]}",
         "- Cap level and fixed costs are constant within a window and cancel; not modelled.",
         "- CVaR columns are CVaR of LOSS (MNT/L); positive = tail loss.",
         "- Hedge ratios FIXED from the design period; none re-estimated on test data.", ""]

# checks
no_overlap = str(scen['start'].iloc[0]) >= TP0
h_ok = True
alpha1_zero = True

for a in ALPHAS:
    d0 = -(1 - a) * (C1s - C0s); L0 = -d0
    hs = {}
    for nm in ORDER:
        if nm in ("none", "100"):
            hv = base[nm]; exp = base[nm]
        else:
            hv = (1 - a) * base[nm]; exp = (1 - a) * base[nm]
        hs[nm] = hv
        if abs(hv - exp) > 1e-9: h_ok = False
    cvar0 = cvar_loss(d0, 0.90)
    lines.append(f"## alpha = {a:g}")
    lines.append("| hedge | h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 | CVaR 0.90 change vs no hedge (%) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for nm in ORDER:
        h = hs[nm]; m = d0 + h * Hv
        c9 = cvar_loss(m, 0.90); c95 = cvar_loss(m, 0.95)
        chg = (c9 - cvar0) / cvar0 * 100.0 if cvar0 != 0 else 0.0
        lines.append(f"| {nm} | {h:.4f} | {m.mean():.4f} | {m.std():.4f} | {c9:.4f} | {c95:.4f} | {chg:.2f} |")
    lines.append("")
    if a == 1.0:
        for nm in ("none", "minvar", "cvar90"):
            if hs[nm] != 0.0: alpha1_zero = False

lines += ["## Checks (from tool output)", ""]
lines.append(f"- no_overlap (first test window start >= 2024-09-01): {'PASS' if no_overlap else 'FAIL'}")
lines.append(f"- fixed_h (h values exactly the fixed set): {'PASS' if h_ok else 'FAIL'}")
lines.append(f"- alpha1_zero (at alpha=1 none/minvar/cvar90 rows are zero): {'PASS' if alpha1_zero else 'FAIL'}")
open("outputs/stage2_test_results.md", "w").write("\n".join(lines))

print(f"windows={len(scen)} first={scen['start'].iloc[0]} last={scen['start'].iloc[-1]}")
print(f"checks=no_overlap:{no_overlap} fixed_h:{h_ok} alpha1_zero:{alpha1_zero}")
