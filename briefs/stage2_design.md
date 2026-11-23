# Stage 2 brief: diesel hedge ratios, design period (preliminary)

Decisions behind this brief: `assumptions.md` A1 to A10. Read them first.

## GOAL
Estimate the Brent futures hedge ratio that minimises the tail risk of the
importer's diesel margin per litre, for pass-through α ∈ {0, 0.25, 0.5,
0.75, 1}, on the design period only. Compare it with simple baselines and
check it by independent methods. This is a preliminary run: no test period,
no gasoline yet.

## INPUTS
- `data/raw/BZ=F.csv` (Brent, USD/bbl) and `data/raw/HO=F.csv` (diesel
  proxy, USD/gal): use Open and Close; dates = New York date part.
- `data/raw/bom_currency-rate-USD.xlsx` (Bank of Mongolia, MNT per USD):
  date part of "Date", column "USD - US dollar".
- Roll days (Brent hedge leg only, A7): the first trading row of each
  calendar month except January, plus the last trading row of December.
  Do not read `scripts/stage1_checks.py`; this rule is equivalent to it.
- File formats: the CSVs have columns Date,Open,High,Low,Close,Adj Close,
  Volume; Date looks like `2021-09-01 00:00:00-04:00` (take the first 10
  characters). The xlsx has columns `Date` (datetime, 08:00) and
  `USD - US dollar`. No need to inspect the files further.
- Design period: 2021-09-01 to 2024-08-31.
If any input is missing or a date has no FX rate, stop and report it.

## METHOD
1. **Scenarios.** Check that BZ=F and HO=F have identical dates in the
   design period (stop if not). Window s starts at trading row i and ends at
   row i + 21; starts every 5 rows; the end row must be on or before
   2024-08-31. Windows overlap: say so in the output.
2. **Prices at window end.** Diesel (HO): raw Close at row i + 21 (no
   adjustment, A7). Brent (BZ): daily return r_t = Close_t / Close_{t−1} − 1,
   except on roll days r_t = Close_t / Open_t − 1; adjusted end price
   B1 = B0 × Π (1 + r_t) over the 21 days, B0 = Close at the start row.
3. **Margin change per litre (MNT).** Constants in code: GAL_PER_BBL = 42,
   L_PER_GAL = 3.785411784, L_PER_BBL = GAL_PER_BBL × L_PER_GAL.
   - Diesel cost per litre: c = HO (USD/gal) / L_PER_GAL; FX S from the Bank
     of Mongolia on the same calendar date (A8). C0 = c0 × S0, C1 = c1 × S1.
   - Retail change = α × (C1 − C0), so the unhedged margin change is
     Δm0 = −(1 − α) × (C1 − C0). The cap level and fixed costs are constant
     within a window and cancel; say so.
   - Hedge: long h barrels of Brent per barrel of diesel bought.
     Hedge P&L per litre H = (B1 − B0) / L_PER_BBL × S1. Units: USD/bbl
     divided by L/bbl = USD per litre, as for C. S1 only: the futures gain
     is paid in USD at the window end.
   - Δm(h) = Δm0 + h × H; loss ℓ_s(h) = −Δm_s(h).
4. **Baselines:** h = 0 (no hedge) and h = 1 (100% hedge).
5. **Closed form (check 1):** minimum-variance h* = −Cov(Δm0, H) / Var(H).
6. **CVaR LP (main method, Lecture 12):** with cvxpy, minimise
   η + 1/((1 − β)M) Σ u_s subject to u_s ≥ ℓ_s(h) − η, u_s ≥ 0,
   0 ≤ h ≤ 2, for β = 0.90 and β = 0.95 (A9). Report if the h bound binds.
7. **Brute force (check 2):** for h = 0, 0.01, …, 2, compute CVaR directly
   by sorting the M losses and averaging the worst (1 − β) share of
   probability mass: with k = floor((1 − β)M), the worst k losses in full
   plus the next one weighted by (1 − β)M − k, all divided by (1 − β)M
   (this equals the LP optimum). Take the best h on the grid.
8. **Sensitivity:** repeat 5 to 7 with raw, unadjusted Brent returns.

## OUTPUT
- `scripts/stage2_design.py` (rerunnable, relative paths only).
- `outputs/stage2_design_results.md`: number of windows, first and last
  window dates, then for each α a table of h (0, 1, min-variance h*, LP h,
  grid h) with mean, standard deviation, CVaR 0.90 and CVaR 0.95 of the
  margin change (MNT per litre); then the raw-return sensitivity.
- `outputs/stage2_design_scenarios.csv`: one row per window with dates,
  C0, C1, H, Δm0.

## BOUNDARIES
No network, no installs, no Git. Do not modify `data/raw/`, `README.md`,
`assumptions.md`, `requirements.txt` or the Stage 1 scripts. Do not fill,
drop or align values beyond the rules above. Use only the design period.

## CHECKS
- LP h and grid h agree within 0.01 for each α and β.
- At α = 1, Δm0 = 0 for every window, so every method should give h = 0.
- Every optimal h should scale with (1 − α): h(α) = (1 − α) × h(0), unless
  the h bound binds.
- State in the results whether each check passed, from the tool output.
- Never claim a run or check succeeded unless the output shows it.
