# fuel-import-hedge-skill

A reusable WorkSwarm Skill for analysing how much of a USD-priced fuel
purchase an importer that sells in a local currency should hedge with Brent
futures, when part of its retail price is government-capped.

> **Status: stub (Stage 1, data assembly).** No model has been run yet. Every
> section marked TODO is unfinished. Do not cite any result from this repo
> until this notice is removed.

Built with WorkSwarm (JiuwenSwarm), the openJiuwen agent app:
**https://github.com/openJiuwen-ai/jiuwenswarm**

---

## 1. User and task

**User:** the finance or procurement team of a fuel importer that buys
refined fuel in USD at market prices and sells it domestically in local
currency (worked case: Mongolia, MNT). For at least one product (AI-92 in the
worked case), the retail price is government-capped.

**Task:** measure how crude-price risk and USD/local-currency risk reach the
margin per litre, then compare hedge ratios on Brent futures. This is
**analysis only**: it does not place trades and needs no brokerage access.

**Supported scope:** TODO (products, currencies and horizons the Skill is
tested on).

The worked case is a stylised importer built from public data. No company is
named, and no private company data is used (see `assumptions.md`).

## 2. Inputs

| Input | Source | Units | Role |
|---|---|---|---|
| `BZ=F` | Yahoo Finance via `yfinance` | USD/bbl | Hedge instrument (Brent) |
| `HO=F` | Yahoo Finance via `yfinance` | USD/gal | Diesel cost proxy (heating oil / ULSD) |
| `RB=F` | Yahoo Finance via `yfinance` | USD/gal | Gasoline cost proxy (RBOB) |
| `USDMNT=X` | Yahoo Finance via `yfinance` | MNT per USD | FX rate |
| Bank of Mongolia USD/MNT rates (fallback) | TODO: URL and retrieval steps | MNT per USD | Replaces `USDMNT=X` if it fails the Stage 1 checks |
| AI-92 retail price cap | TODO: public source | MNT/litre | Retail price for the capped product |
| Fixed costs per litre | TODO: source or stated assumption | MNT/litre | Margin calculation |

Full field definitions, units and transformations: `data/data_dictionary.md`.
Assumptions: `assumptions.md`.

## 3. How to run

**Required software and tested versions:**
- WorkSwarm: TODO (version); model `deepseek-v4-flash-0731`
- Python: Anaconda, called by full path (`/opt/anaconda3/bin/python`)
  because WorkSwarm's shell does not see conda's PATH. TODO: Python version.
- Packages: `yfinance==1.8.0`, `pandas==2.2.2`, `numpy==1.26.4`
  (see `requirements.txt`)
- macOS on Apple silicon (arm64)

**Get the data:** TODO (exact command).

**Run the Skill in WorkSwarm:** TODO (how to import `skills/...` by absolute
path, and the exact prompt or invocation).

**One small example and its expected checks:** TODO.

## 4. Checks

**Stage 1 (data):** for each series, row count, date range, missing days,
duplicate dates, zero or negative prices, largest daily moves, suspected
futures contract-roll jumps, and one hand-worked unit conversion. Output:
`outputs/stage1_checks.md`.

**Planned (Stage 2 onwards; not yet implemented):**
- Baselines: no hedge, and 100% hedge.
- Independent check by a different method: brute-force search over hedge
  ratios, and the closed-form minimum-variance ratio h* = Cov/Var.
- Fresh-run case in a new conversation: gasoline (`RB=F`) with a different
  pass-through parameter.

## 5. Outputs

TODO: list each file in `outputs/` and what it means.

## 6. Limitations

- **Basis risk:** `HO=F` and `RB=F` are US benchmark contracts. Real invoices
  are for Russian-origin product bought through intermediaries, and their
  prices are not public. The proxy-versus-invoice gap is not measured.
- **Continuous futures series:** Yahoo `=F` tickers roll between contract
  months, so the series can jump on roll dates. These jumps are flagged in
  Stage 1. TODO: how they are handled.
- **Price cap:** the cap level and its revision history are inputs, not
  modelled. TODO: source.
- **FX data:** `USDMNT=X` quality is checked in Stage 1 before use.
- TODO: further limitations found during evaluation.

## 7. Attribution and AI use

- Course: IEDA 4000H Optimization in Financial Engineering, HKUST (Prof.
  Zijie Zhou), "Finance with AI Agents" final project.
- Agent: WorkSwarm (JiuwenSwarm), built on openJiuwen. Model: TODO.
- How AI was used: the agent proposed plans and wrote code. Python performed
  every calculation. The author reviewed and approved each stage before it
  ran. TODO: list the substantial AI-written parts.
- Data: Yahoo Finance via `yfinance`. Downloaded data is not redistributed
  in this repository (`data/raw/` and `data/clean/` are git-ignored); run the
  download script to fetch it.
- Reused code: TODO.
- License: TODO.

## 8. openJiuwen

- JiuwenSwarm: https://github.com/openJiuwen-ai/jiuwenswarm
- Version of this project: TODO (exact commit URL)

## Repository layout

```
README.md            this file
assumptions.md       every modelling and data assumption, labelled
requirements.txt     Python dependencies
.gitignore           excludes downloaded data, caches and secrets
data/raw/            untouched downloads (git-ignored)
data/clean/          cleaned, aligned series, prices.csv (git-ignored)
data/data_dictionary.md  sources, units, transformations (committed)
scripts/             download, cleaning and check scripts
skills/              the reusable WorkSwarm Skill (SKILL.md and helpers)
outputs/             checks and results
```
