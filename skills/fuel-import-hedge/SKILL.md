---
name: fuel-import-hedge
description: Estimate and test a Brent futures hedge ratio for a USD-priced fuel bought by an importer who sells in MNT, across a pass-through grid. Use it when you need a defensible hedge ratio for a fuel import priced in USD with revenue in Mongolian Tögrög.
---

# 1. Scope

Estimate and test a Brent futures hedge ratio for a USD-priced fuel bought by
an importer who sells in Mongolian Tögrög (MNT), evaluated over a
pass-through grid α. The hedge ratio and its performance are computed and
checked on your supplied data.

It does NOT trade, does NOT hedge FX exposure, and does NOT use invoice prices.

# 2. Inputs the user must supply

- Product proxy: a Yahoo futures ticker that fetch.py can download, and its
  unit, which must be `gal` or `bbl` (`hedge.py --product-unit` accepts only
  these two).
- Hedge ticker: only `BZ=F` is supported, because the roll rule is Brent's.
- Bank of Mongolia USD/MNT file: the Excel export from
  https://www.mongolbank.mn/en/currency-rates. `hedge.py` requires columns
  named exactly `Date` and `USD - US dollar` (MNT per USD), with one row per
  calendar day.
- Design period and test period (start and end dates, inclusive).
- α grid: α is the share of a cost change passed through to the selling
  price within the horizon, from 0 to 1.
- β levels: β is the CVaR confidence level (e.g. 0.90 = worst 10% of
  windows). It is NOT a hedge ratio; h is an output.
- Horizon: window length in trading days (default 21); step: trading days
  between window starts (default 5). Windows overlap.
- hmax: upper bound on h for the optimiser; report if it binds.

# 3. Procedure with approval gates

- commands run from the user's project root
- `<skill_dir>` is the folder containing SKILL.md
- use a Python that has the packages in requirements.txt (in WorkSwarm's shell
  give its full path, the default python3 may lack them)

1. confirm inputs, short plan, wait for approval
2. run

```bash
python <skill_dir>/scripts/fetch.py \
  --tickers BZ=F <product> \
  --start <D> \
  --end <D> \
  --out-raw <dir>
```

show fetch_checks.md, stop for approval if any check fails
3. run

```bash
python <skill_dir>/scripts/hedge.py \
  --product <ticker> \
  --product-unit gal|bbl \
  --hedge BZ=F \
  --fx <bom.xlsx> \
  --raw-dir <dir> \
  --design <START> <END> \
  --test <START> <END> \
  --horizon 21 \
  --step 5 \
  --alphas ... \
  --betas ... \
  --hmax ... \
  --out <out_dir>
```

(`<dir>` is the same folder as `--out-raw`)
4. show results and checks, recommend an independent check by a different method
   before use

# 4. Checks

- fetch.py: row count, date range, duplicate dates, zero or negative prices,
  zero-volume days, missing weekdays, shared dates across tickers
- hedge.py design: lp_grid_agree, alpha1_zero, scaling, "bound(hmax) binds" per
  beta
- hedge.py test: no_overlap, fixed_h, alpha1_zero

Missing raw file, missing FX file or FX date, and product/hedge date mismatch
stop with a clear message.

# 5. Failure handling
For each failure: what happens, and what the agent must do; never substitute, fill or drop data without approval:
- ticker has no Yahoo history: `fetch.py` exits 1 with a message; ask the user for another source.
- FX date missing: `hedge.py` stops ("missing FX for window"); ask for a complete BoM file; do not interpolate.
- product and hedge dates differ: `hedge.py` stops; report it, ask before any alignment.
- h bound binds: report it; ask before changing `--hmax`.
- hedge ticker not BZ=F: `hedge.py` does NOT check this; the agent must stop before running.

# 6. Interpretation notes for a new case
Before modelling, look for case-specific issues:
- seasonal contract-grade switches in the product proxy
- basis risk between the proxy and real invoice prices
- whether pass-through within the horizon is realistic (e.g. regulated price caps)
- FX exposure is not hedged

# 7. Outputs
- In `--out-raw`: `<ticker>.csv`, `fetch_meta.json`, `fetch_checks.md`.
- In `--out`: `scenarios_design.csv` and `scenarios_test.csv` (one row per window), `results.md` (tables and checks), `results.json` (hedge ratios and statistics), `run.json` (arguments and versions).

# 8. Limitations, dependencies, attribution
- proxies, not invoice prices
- overlapping windows mean fewer independent observations
- historical results, not forecasts
- Yahoo daily close, not official settlement
- only BZ=F hedge and gal/bbl units
Dependencies: see `requirements.txt` (yfinance, pandas, numpy, openpyxl, cvxpy).
Built with WorkSwarm (JiuwenSwarm): https://github.com/openJiuwen-ai/jiuwenswarm

Author: Anar Erkhembayar. Scripts written by a WorkSwarm agent from the
author's briefs; briefs and code review assisted by Claude (Anthropic).
