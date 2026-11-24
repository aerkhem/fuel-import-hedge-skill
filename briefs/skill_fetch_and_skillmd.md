# Skill brief, part 2: fetch.py and SKILL.md

Continues `briefs/skill_generalize.md`. `skills/fuel-import-hedge/scripts/hedge.py`
exists and passed the diesel regression (design identical; test identical
except 4th-decimal differences because the original test used 4-decimal
rounded hedge ratios, while hedge.py uses full precision; accepted).

## Part A: scripts/fetch.py

```
python skills/fuel-import-hedge/scripts/fetch.py \
  --tickers BZ=F RB=F --start 2021-09-01 --end 2026-08-31 \
  --out-raw runs/<case>/raw
```
- Download daily data with yfinance, `auto_adjust=False`. `--end` is
  inclusive: pass end + 1 day to yfinance and say so in the metadata.
- Save each download untouched as `<out-raw>/<ticker>.csv`, in the same
  format as `data/raw/*.csv`. Never overwrite an existing file unless
  `--overwrite` is given.
- Write `<out-raw>/fetch_meta.json`: tickers, dates, adjustment setting,
  retrieval time (UTC), yfinance/pandas versions, row counts, and RELATIVE
  file paths only.
- Write `<out-raw>/fetch_checks.md` per ticker: row count, date range,
  duplicate dates, zero or negative prices, zero-volume days, number of
  missing weekdays, and whether all tickers share the same dates.
- Stop with a clear message and a non-zero exit, not a traceback, if a
  ticker returns no rows (e.g. `USDMNT=X`, which has no history on Yahoo),
  and name the problem so the user can supply another source.
- Network: yfinance downloads only.

**Test:** fetch `BZ=F HO=F` for 2021-09-01 to 2026-08-31 into
`outputs/skill_fetch_test/raw`, then report how many Close values differ
from `data/raw/` for the same dates (Yahoo may revise history; report,
don't fix).

## Part B: SKILL.md

Write `skills/fuel-import-hedge/SKILL.md` for a NEW user. Start with YAML
front matter:
```
---
name: fuel-import-hedge
description: <one or two sentences: what it does and when to use it>
---
```
Then these sections:
1. **Scope**: estimate and test a Brent futures hedge ratio for a USD-priced
   fuel bought by an importer who sells in MNT, over a pass-through grid α.
   Say what it does not do (no trading, no FX hedge, no invoice prices).
2. **Inputs the user must supply**: product proxy ticker and its unit;
   hedge ticker (only `BZ=F` is supported, because the roll rule is
   Brent's); the Bank of Mongolia USD/MNT file (how to download it from
   https://www.mongolbank.mn/en/currency-rates, and its expected columns);
   design and test periods; α grid; β levels; horizon and step.
3. **Procedure with approval gates**: (1) confirm inputs and show a short
   plan, then wait for approval; (2) run fetch.py, show fetch_checks.md,
   and stop for approval if any check fails; (3) run hedge.py; (4) show
   the results and checks, and recommend an independent check by a
   different method before the results are used. Give exact commands with
   `<skill_dir>` meaning the folder that contains SKILL.md, and state that
   commands are run from the user's project root.
4. **Checks**: list every built-in check of fetch.py and hedge.py.
5. **Failure handling**: missing ticker history; FX date missing; product
   and hedge dates differ; the h bound binds; hedge ticker not BZ=F.
6. **Interpretation notes for a new case**: ask the agent to look for
   case-specific issues before modelling, e.g. seasonal contract-grade
   switches in the product proxy, basis risk against real invoices, and
   whether pass-through within the horizon is realistic.
7. **Outputs**: each file and what it means.
8. **Limitations, dependencies** (Python packages and versions from
   `requirements.txt`), **attribution**, and the link
   https://github.com/openJiuwen-ai/jiuwenswarm.

Do NOT include any previous results, hedge ratios, approvals or answers:
a new run must obtain its own inputs and decisions. No personal paths.

## BOUNDARIES
No installs, no Git. Network for the Part A test download only. Do not
modify anything outside `skills/fuel-import-hedge/` and
`outputs/skill_fetch_test/`.
