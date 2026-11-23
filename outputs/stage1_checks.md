# Stage 1 checks (part B) - integrity + missing weekdays

- Script: `scripts/stage1_checks.py`
- Input: `data/raw/{BZ=F,HO=F,RB=F}.csv` (untouched)
- Output: `outputs/stage1_checks.md`

> Close is Yahoo daily close; not verified to equal the official exchange settlement price.

## CME holiday list used (for user verification)

Legend:
- `to verify`: 2025-01-09 (national day of mourning) and Juneteenth dates
- `CME holiday (for user verification)`: all other dates in the list
- `unexplained`: any other missing weekday

- 2021-09-06 (CME holiday)
- 2021-11-25 (CME holiday)
- 2021-12-24 (CME holiday)
- 2022-04-15 (CME holiday)
- 2022-05-30 (CME holiday)
- 2022-06-20 (to verify)
- 2022-07-04 (CME holiday)
- 2022-09-05 (CME holiday)
- 2022-11-24 (CME holiday)
- 2022-12-26 (CME holiday)
- 2023-01-02 (CME holiday)
- 2023-04-07 (CME holiday)
- 2023-05-29 (CME holiday)
- 2023-06-19 (to verify)
- 2023-07-04 (CME holiday)
- 2023-09-04 (CME holiday)
- 2023-11-23 (CME holiday)
- 2023-12-25 (CME holiday)
- 2024-01-01 (CME holiday)
- 2024-03-29 (CME holiday)
- 2024-05-27 (CME holiday)
- 2024-06-19 (to verify)
- 2024-07-04 (CME holiday)
- 2024-09-02 (CME holiday)
- 2024-11-28 (CME holiday)
- 2024-12-25 (CME holiday)
- 2025-01-01 (CME holiday)
- 2025-01-09 (to verify)
- 2025-04-18 (CME holiday)
- 2025-05-26 (CME holiday)
- 2025-06-19 (to verify)
- 2025-07-04 (CME holiday)
- 2025-09-01 (CME holiday)
- 2025-11-27 (CME holiday)
- 2025-12-25 (CME holiday)
- 2026-01-01 (CME holiday)
- 2026-04-03 (CME holiday)
- 2026-05-25 (CME holiday)
- 2026-06-19 (to verify)
- 2026-07-03 (CME holiday)

## Per-series checks

### BZ=F

| Check | Result |
|---|---|
| Row count | 1257 |
| Date range | 2021-09-01 .. 2026-08-31 |
| Index timezone (measured) | see offset table below |
| Conversion to plain dates | tz_convert to America/New_York, then `.date()` |
| Duplicate dates | 0 |
| Zero/negative prices per column | |
| &nbsp;&nbsp;Open | 0 |
| &nbsp;&nbsp;High | 0 |
| &nbsp;&nbsp;Low | 0 |
| &nbsp;&nbsp;Close | 0 |
| &nbsp;&nbsp;Adj Close | 0 |
| Zero-volume days | 8 |
| &nbsp;&nbsp;Dates | 2023-04-06, 2025-06-18, 2025-07-03, 2025-07-04, 2025-08-29, 2025-11-03, 2026-04-02, 2026-07-02 |
| Rows where Adj Close != Close | 0 |

**Index timezone (measured)**

| UTC offset | Rows |
|---|---|
| -05:00 (UTC-300 min) | 427 |
| -04:00 (UTC-240 min) | 830 |
| Rows whose local time is not 00:00 | 0 |

**Missing weekdays**

| Missing weekday | Classification |
|---|---|
| 2021-09-06 | CME holiday (for user verification) |
| 2021-11-25 | CME holiday (for user verification) |
| 2021-12-24 | CME holiday (for user verification) |
| 2022-01-17 | unexplained |
| 2022-02-21 | unexplained |
| 2022-04-15 | CME holiday (for user verification) |
| 2022-05-30 | CME holiday (for user verification) |
| 2022-06-20 | to verify |
| 2022-07-04 | CME holiday (for user verification) |
| 2022-09-05 | CME holiday (for user verification) |
| 2022-11-24 | CME holiday (for user verification) |
| 2022-12-26 | CME holiday (for user verification) |
| 2023-01-02 | CME holiday (for user verification) |
| 2023-01-16 | unexplained |
| 2023-02-20 | unexplained |
| 2023-04-07 | CME holiday (for user verification) |
| 2023-05-29 | CME holiday (for user verification) |
| 2023-06-19 | to verify |
| 2023-07-04 | CME holiday (for user verification) |
| 2023-09-04 | CME holiday (for user verification) |
| 2023-12-25 | CME holiday (for user verification) |
| 2024-01-01 | CME holiday (for user verification) |
| 2024-01-15 | unexplained |
| 2024-02-19 | unexplained |
| 2024-03-29 | CME holiday (for user verification) |
| 2024-05-27 | CME holiday (for user verification) |
| 2024-06-19 | to verify |
| 2024-07-04 | CME holiday (for user verification) |
| 2024-09-02 | CME holiday (for user verification) |
| 2024-11-28 | CME holiday (for user verification) |
| 2024-12-25 | CME holiday (for user verification) |
| 2025-01-01 | CME holiday (for user verification) |
| 2025-01-20 | unexplained |
| 2025-02-17 | unexplained |
| 2025-04-18 | CME holiday (for user verification) |
| 2025-05-26 | CME holiday (for user verification) |
| 2025-06-19 | to verify |
| 2025-09-01 | CME holiday (for user verification) |
| 2025-11-27 | CME holiday (for user verification) |
| 2025-12-25 | CME holiday (for user verification) |
| 2026-01-01 | CME holiday (for user verification) |
| 2026-01-19 | unexplained |
| 2026-02-16 | unexplained |
| 2026-04-03 | CME holiday (for user verification) |
| 2026-05-25 | CME holiday (for user verification) |
| 2026-06-19 | to verify |
| 2026-07-03 | CME holiday (for user verification) |

**Bars dated on a CME holiday date**

| Bar date | Close |
|---|---|
| 2023-11-23 | 81.37000274658203 |
| 2025-01-09 | 76.91999816894531 |
| 2025-07-04 | 68.29000091552734 |

### HO=F

| Check | Result |
|---|---|
| Row count | 1257 |
| Date range | 2021-09-01 .. 2026-08-31 |
| Index timezone (measured) | see offset table below |
| Conversion to plain dates | tz_convert to America/New_York, then `.date()` |
| Duplicate dates | 0 |
| Zero/negative prices per column | |
| &nbsp;&nbsp;Open | 0 |
| &nbsp;&nbsp;High | 0 |
| &nbsp;&nbsp;Low | 0 |
| &nbsp;&nbsp;Close | 0 |
| &nbsp;&nbsp;Adj Close | 0 |
| Zero-volume days | 7 |
| &nbsp;&nbsp;Dates | 2023-04-06, 2025-06-18, 2025-07-03, 2025-07-04, 2025-08-29, 2025-11-03, 2026-04-02 |
| Rows where Adj Close != Close | 0 |

**Index timezone (measured)**

| UTC offset | Rows |
|---|---|
| -05:00 (UTC-300 min) | 427 |
| -04:00 (UTC-240 min) | 830 |
| Rows whose local time is not 00:00 | 0 |

**Missing weekdays**

| Missing weekday | Classification |
|---|---|
| 2021-09-06 | CME holiday (for user verification) |
| 2021-11-25 | CME holiday (for user verification) |
| 2021-12-24 | CME holiday (for user verification) |
| 2022-01-17 | unexplained |
| 2022-02-21 | unexplained |
| 2022-04-15 | CME holiday (for user verification) |
| 2022-05-30 | CME holiday (for user verification) |
| 2022-06-20 | to verify |
| 2022-07-04 | CME holiday (for user verification) |
| 2022-09-05 | CME holiday (for user verification) |
| 2022-11-24 | CME holiday (for user verification) |
| 2022-12-26 | CME holiday (for user verification) |
| 2023-01-02 | CME holiday (for user verification) |
| 2023-01-16 | unexplained |
| 2023-02-20 | unexplained |
| 2023-04-07 | CME holiday (for user verification) |
| 2023-05-29 | CME holiday (for user verification) |
| 2023-06-19 | to verify |
| 2023-07-04 | CME holiday (for user verification) |
| 2023-09-04 | CME holiday (for user verification) |
| 2023-12-25 | CME holiday (for user verification) |
| 2024-01-01 | CME holiday (for user verification) |
| 2024-01-15 | unexplained |
| 2024-02-19 | unexplained |
| 2024-03-29 | CME holiday (for user verification) |
| 2024-05-27 | CME holiday (for user verification) |
| 2024-06-19 | to verify |
| 2024-07-04 | CME holiday (for user verification) |
| 2024-09-02 | CME holiday (for user verification) |
| 2024-11-28 | CME holiday (for user verification) |
| 2024-12-25 | CME holiday (for user verification) |
| 2025-01-01 | CME holiday (for user verification) |
| 2025-01-20 | unexplained |
| 2025-02-17 | unexplained |
| 2025-04-18 | CME holiday (for user verification) |
| 2025-05-26 | CME holiday (for user verification) |
| 2025-06-19 | to verify |
| 2025-09-01 | CME holiday (for user verification) |
| 2025-11-27 | CME holiday (for user verification) |
| 2025-12-25 | CME holiday (for user verification) |
| 2026-01-01 | CME holiday (for user verification) |
| 2026-01-19 | unexplained |
| 2026-02-16 | unexplained |
| 2026-04-03 | CME holiday (for user verification) |
| 2026-05-25 | CME holiday (for user verification) |
| 2026-06-19 | to verify |
| 2026-07-03 | CME holiday (for user verification) |

**Bars dated on a CME holiday date**

| Bar date | Close |
|---|---|
| 2023-11-23 | 2.8712000846862793 |
| 2025-01-09 | 2.378200054168701 |
| 2025-07-04 | 2.4089999198913574 |

### RB=F

| Check | Result |
|---|---|
| Row count | 1257 |
| Date range | 2021-09-01 .. 2026-08-31 |
| Index timezone (measured) | see offset table below |
| Conversion to plain dates | tz_convert to America/New_York, then `.date()` |
| Duplicate dates | 0 |
| Zero/negative prices per column | |
| &nbsp;&nbsp;Open | 0 |
| &nbsp;&nbsp;High | 0 |
| &nbsp;&nbsp;Low | 0 |
| &nbsp;&nbsp;Close | 0 |
| &nbsp;&nbsp;Adj Close | 0 |
| Zero-volume days | 8 |
| &nbsp;&nbsp;Dates | 2023-04-06, 2025-06-18, 2025-07-03, 2025-07-04, 2025-08-29, 2025-11-03, 2026-04-02, 2026-07-02 |
| Rows where Adj Close != Close | 0 |

**Index timezone (measured)**

| UTC offset | Rows |
|---|---|
| -05:00 (UTC-300 min) | 427 |
| -04:00 (UTC-240 min) | 830 |
| Rows whose local time is not 00:00 | 0 |

**Missing weekdays**

| Missing weekday | Classification |
|---|---|
| 2021-09-06 | CME holiday (for user verification) |
| 2021-11-25 | CME holiday (for user verification) |
| 2021-12-24 | CME holiday (for user verification) |
| 2022-01-17 | unexplained |
| 2022-02-21 | unexplained |
| 2022-04-15 | CME holiday (for user verification) |
| 2022-05-30 | CME holiday (for user verification) |
| 2022-06-20 | to verify |
| 2022-07-04 | CME holiday (for user verification) |
| 2022-09-05 | CME holiday (for user verification) |
| 2022-11-24 | CME holiday (for user verification) |
| 2022-12-26 | CME holiday (for user verification) |
| 2023-01-02 | CME holiday (for user verification) |
| 2023-01-16 | unexplained |
| 2023-02-20 | unexplained |
| 2023-04-07 | CME holiday (for user verification) |
| 2023-05-29 | CME holiday (for user verification) |
| 2023-06-19 | to verify |
| 2023-07-04 | CME holiday (for user verification) |
| 2023-09-04 | CME holiday (for user verification) |
| 2023-12-25 | CME holiday (for user verification) |
| 2024-01-01 | CME holiday (for user verification) |
| 2024-01-15 | unexplained |
| 2024-02-19 | unexplained |
| 2024-03-29 | CME holiday (for user verification) |
| 2024-05-27 | CME holiday (for user verification) |
| 2024-06-19 | to verify |
| 2024-07-04 | CME holiday (for user verification) |
| 2024-09-02 | CME holiday (for user verification) |
| 2024-11-28 | CME holiday (for user verification) |
| 2024-12-25 | CME holiday (for user verification) |
| 2025-01-01 | CME holiday (for user verification) |
| 2025-01-20 | unexplained |
| 2025-02-17 | unexplained |
| 2025-04-18 | CME holiday (for user verification) |
| 2025-05-26 | CME holiday (for user verification) |
| 2025-06-19 | to verify |
| 2025-09-01 | CME holiday (for user verification) |
| 2025-11-27 | CME holiday (for user verification) |
| 2025-12-25 | CME holiday (for user verification) |
| 2026-01-01 | CME holiday (for user verification) |
| 2026-01-19 | unexplained |
| 2026-02-16 | unexplained |
| 2026-04-03 | CME holiday (for user verification) |
| 2026-05-25 | CME holiday (for user verification) |
| 2026-06-19 | to verify |
| 2026-07-03 | CME holiday (for user verification) |

**Bars dated on a CME holiday date**

| Bar date | Close |
|---|---|
| 2023-11-23 | 2.214400053024292 |
| 2025-01-09 | 2.0283000469207764 |
| 2025-07-04 | 2.1171000003814697 |
