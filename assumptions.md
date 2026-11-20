# Assumptions

Each line below is an **assumption**: a choice made to keep the analysis
tractable, not a measured fact. Each one lists what it affects and what would
change it. When an assumption is replaced by a sourced fact, move it to the
"Resolved" section with the source.

---

## A1. Hedging horizon: about 1 month (21 trading days). ASSUMPTION

- **Statement:** the hedge is held for 21 trading days. This stands in for
  the delay between buying the fuel (price fixed in USD) and paying for it
  (USD converted from MNT).
- **Windows:** windows of 21 trading days, with a new window starting every
  week (every 5 trading days).
- **The windows overlap.** A 21-day window stepped by 5 days shares about 16
  of its 21 days with the next window. So consecutive window outcomes are
  not independent, and the effective number of independent observations is
  much smaller than the number of windows. Report results with this in mind.
- **Affects:** every margin distribution, CVaR estimate and hedge ratio.
- **Would change if:** the actual purchase-to-payment delay is documented
  from a public source or confirmed differently.
- **Basis for 21 days:** TODO (Anar to state).

## A2. AI-92 retail cap held fixed through each test window. ASSUMPTION

- **Statement:** within each test window, the AI-92 retail price stays at
  the cap level in force at the start of the window.
- **Cap level:** NOT YET SOURCED. TODO: public source, date and level in
  MNT/litre, plus any revisions during 2021-09-01 to 2026-08-31.
- **Affects:** AI-92 retail price, and so AI-92 margin.
- **Would change if:** the cap was revised inside a window.

## A3. Pass-through alpha is run as a grid, not estimated. ASSUMPTION

- **Statement:** alpha is run over {0, 0.25, 0.5, 0.75, 1}, where 0 means
  retail price fully fixed (capped) and 1 means retail price fully follows
  cost. No single value is claimed to be correct.
- **Affects:** how much of a cost shock reaches the margin, and so the
  hedge ratio.
- **Would change if:** a public price series lets alpha be estimated.

## A4. Price proxies. ASSUMPTION (basis risk is a stated limitation)

| Exposure | Proxy | Units on Yahoo |
|---|---|---|
| Diesel cost | `HO=F` (NY Harbor ULSD / heating oil futures) | USD/gal |
| Gasoline cost | `RB=F` (RBOB gasoline futures) | USD/gal |
| Hedge instrument | `BZ=F` (Brent crude futures) | USD/bbl |

- **Statement:** daily changes in these US benchmark prices stand in for
  changes in the importer's USD purchase cost.
- **Limitation (basis risk):** actual purchases are Russian-origin product
  bought through intermediaries. Their invoice prices are not public, so the
  gap between proxy and invoice price is not measured. A hedge that looks
  effective against the proxy may be less effective against real invoices.
- **Would change if:** a public price series for Russian-origin product
  delivered to Mongolia becomes available.

## A5. Public data only; no company named. ASSUMPTION / CONSTRAINT

- **Statement:** all inputs come from public sources. The importer is
  stylised and is not named anywhere in this repository, the report or the
  demo.
- **Affects:** what can be claimed. Results describe a stylised importer,
  not any real company's position.

---

## Open questions (not yet assumptions)

- A2 and A3 together: if the AI-92 cap is fixed inside each window (A2),
  then alpha is 0 for AI-92 within that window. To be decided: does the
  alpha grid apply to AI-92 at all, or only to the less-regulated products
  (diesel, Euro-92, 95)?
- Fixed costs per litre (MNT): source or assumption still needed.
- USD/MNT source: `USDMNT=X`, or Bank of Mongolia rates if `USDMNT=X` fails
  the Stage 1 checks.

## Resolved

(none yet)
