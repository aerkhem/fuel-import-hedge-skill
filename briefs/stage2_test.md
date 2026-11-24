# Stage 2 brief: out-of-sample test, diesel (preliminary)

Decisions behind this brief: `assumptions.md` A1 to A10, and
`briefs/stage2_design.md` for the scenario and margin definitions. Read both.

## GOAL
Test, on data not used to choose them, whether the hedge ratios estimated on
the design period still reduce the tail risk of the diesel margin per litre.

## INPUTS
- Same files and formats as `briefs/stage2_design.md`. Do not read
  `scripts/stage1_checks.py`.
- Test period: 2024-09-01 to 2026-08-31.
- Hedge ratios, FIXED from the design period (`outputs/stage2_design_results.md`,
  adjusted returns). For α = 0: none h = 0; 100% hedge h = 1;
  min-variance h = 1.3870; CVaR 0.90 (LP) h = 1.7160; CVaR 0.95 (LP)
  h = 1.4843. For α > 0, the none and 100% ratios stay 0 and 1, and the other
  three are (1 − α) times the α = 0 values (the scaling check passed).
  Do not re-estimate any ratio on test data.

## METHOD
1. Build test windows exactly as in `briefs/stage2_design.md` steps 1 to 3
   (21-day windows, start every 5 rows from the first trading row on or
   after 2024-09-01, end row on or before 2026-08-31; Brent roll adjustment
   on the hedge leg only; diesel at raw Close; Bank of Mongolia FX on the
   same calendar date). Windows overlap: say so.
2. For each α ∈ {0, 0.25, 0.5, 0.75, 1} and each of the five fixed ratios,
   compute the margin change Δm(h) = Δm0 + h × H on every test window.
3. Report mean, population standard deviation, CVaR 0.90 and CVaR 0.95 of
   the LOSS (−Δm), using the same CVaR definition as the design brief,
   and the % change in CVaR 0.90 versus no hedge.

## OUTPUT
- `scripts/stage2_test.py` (rerunnable from the repo root; relative paths).
- `outputs/stage2_test_results.md`: number of windows, first and last window
  dates, then one table per α with columns: hedge, h, mean, std,
  CVaR loss 0.90, CVaR loss 0.95, CVaR 0.90 change vs no hedge (%).
- `outputs/stage2_test_scenarios.csv`: one row per test window with dates,
  C0, C1, H, Δm0.

## BOUNDARIES
No network, no installs, no Git. Do not modify `data/raw/`, `README.md`,
`assumptions.md`, `requirements.txt`, the Stage 1 scripts, or
`scripts/stage2_design.py` and its outputs. Use only test-period data for
the evaluation.

## CHECKS
- No test window starts before 2024-09-01 (no overlap with the design period).
- The h values used are exactly the fixed values above.
- At α = 1, the no-hedge, min-variance and CVaR rows are all zero.
- Never claim a run or check succeeded unless the output shows it.
