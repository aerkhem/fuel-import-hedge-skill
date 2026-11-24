# Skill brief: generalise the reviewed hedge workflow

The diesel workflow (`scripts/stage1_download.py`, `scripts/stage2_design.py`,
`scripts/stage2_test.py`, briefs `stage2_design.md` and `stage2_test.md`,
`assumptions.md` A1 to A10) has been reviewed and its results independently
verified. This brief turns it into a reusable Skill in
`skills/fuel-import-hedge/`, without changing any existing file.

## GOAL
A Skill another WorkSwarm user can load to estimate and test a Brent hedge
ratio for a USD-priced fuel bought by an importer who sells in MNT, for a
product and period they choose.

## TARGET STRUCTURE
```
skills/fuel-import-hedge/
  SKILL.md              (written in a later turn)
  scripts/fetch.py      (written in a later turn)
  scripts/hedge.py      (this turn)
```
Scripts must work when run from any folder: resolve every path from the
command-line arguments, not from the script's own location or a fixed path.
No personal or absolute paths in code or outputs.

## hedge.py: command line
```
python skills/fuel-import-hedge/scripts/hedge.py \
  --product HO=F --product-unit gal --hedge BZ=F \
  --fx data/raw/bom_currency-rate-USD.xlsx --raw-dir data/raw \
  --design 2021-09-01 2024-08-31 --test 2024-09-01 2026-08-31 \
  --horizon 21 --step 5 --alphas 0 0.25 0.5 0.75 1 --betas 0.90 0.95 \
  --hmax 2 --out outputs/skill_regression_diesel
```
- `--product-unit`: `gal` (USD per US gallon) or `bbl` (USD per barrel).
- Raw files are `<raw-dir>/<ticker>.csv` in the yfinance format already used.
- `--test` is optional; without it, only the design period is run.

## hedge.py: method (identical to the reviewed diesel workflow)
Scenarios, roll adjustment on the hedge leg only (Brent rule, A7), FX pairing
(A8), margin change, H, losses, baselines (h = 0, h = 1), min-variance h*,
CVaR LP with cvxpy (0 ≤ h ≤ hmax) for each β, brute-force grid (step 0.01)
with the exact CVaR definition, raw-return sensitivity, and the test period
with ratios FIXED from the design period. Reuse the logic of
`scripts/stage2_design.py` and `scripts/stage2_test.py`; do not change it.

## hedge.py: outputs in `--out`
- `scenarios_design.csv`, `scenarios_test.csv` (if `--test`).
- `results.md`: design and test tables per α, as in the existing results files.
- `results.json`: machine-readable h values and CVaR figures per α, β, hedge.
- `run.json`: the exact arguments, the date and time, and package versions.

## CHECKS
1. Regression: run the diesel command above and confirm that the design
   h values and CVaR figures equal `outputs/stage2_design_results.md` and
   the test figures equal `outputs/stage2_test_results.md` to 4 decimals.
   Report any difference; do not adjust the code to force a match.
2. The built-in checks from the briefs: LP = grid within 0.01; α = 1 gives
   h = 0; every h scales with (1 − α) unless the bound binds; no test window
   starts before the test start date.
3. Stop with a clear message, not a traceback, if a raw file or an FX date
   is missing, or if the product and hedge dates differ in the design period.

## BOUNDARIES
No network, no installs, no Git. Do not modify anything outside
`skills/fuel-import-hedge/` and the new `--out` folder; in particular leave
`scripts/`, `outputs/` (existing files), `briefs/`, `data/raw/`,
`assumptions.md`, `README.md` and `requirements.txt` unchanged.
