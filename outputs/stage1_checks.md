# Stage 1 checks (part C) - integrity, weekdays, moves

- Script: `scripts/stage1_checks.py`
- Input: `data/raw/{BZ=F,HO=F,RB=F}.csv` and `data/raw/bom_currency-rate-USD.xlsx` (untouched)

- Script: `scripts/stage1_checks.py`
- Input: `data/raw/{BZ=F,HO=F,RB=F}.csv` (untouched)
- Output: `outputs/stage1_checks.md`

> Close is Yahoo daily close; not verified to equal the official exchange settlement price.

## Holiday list used (for user verification)

Legend:
- `CME holiday (for user verification)`: the dates below, except Juneteenth
- `to verify`: Juneteenth dates
- `US holiday, no Yahoo bar (CME status to verify)`: MLK and Presidents' Day
- `unexplained`: any other missing weekday
- 2025-01-09: removed from the list; it HAS a bar (see holiday-bars table)

CME holidays:
- 2021-09-06 (CME holiday)
- 2021-11-25 (CME holiday)
- 2021-12-24 (CME holiday)
- 2022-04-15 (CME holiday)
- 2022-05-30 (CME holiday)
- 2022-07-04 (CME holiday)
- 2022-09-05 (CME holiday)
- 2022-11-24 (CME holiday)
- 2022-12-26 (CME holiday)
- 2023-01-02 (CME holiday)
- 2023-04-07 (CME holiday)
- 2023-05-29 (CME holiday)
- 2023-07-04 (CME holiday)
- 2023-09-04 (CME holiday)
- 2023-11-23 (CME holiday)
- 2023-12-25 (CME holiday)
- 2024-01-01 (CME holiday)
- 2024-03-29 (CME holiday)
- 2024-05-27 (CME holiday)
- 2024-07-04 (CME holiday)
- 2024-09-02 (CME holiday)
- 2024-11-28 (CME holiday)
- 2024-12-25 (CME holiday)
- 2025-01-01 (CME holiday)
- 2025-04-18 (CME holiday)
- 2025-05-26 (CME holiday)
- 2025-07-04 (CME holiday)
- 2025-09-01 (CME holiday)
- 2025-11-27 (CME holiday)
- 2025-12-25 (CME holiday)
- 2026-01-01 (CME holiday)
- 2026-04-03 (CME holiday)
- 2026-05-25 (CME holiday)
- 2026-07-03 (CME holiday)

Juneteenth (to verify):
- 2022-06-20 (to verify)
- 2023-06-19 (to verify)
- 2024-06-19 (to verify)
- 2025-06-19 (to verify)
- 2026-06-19 (to verify)

MLK / Presidents' Day (US holiday, no Yahoo bar; CME status to verify):
- 2022-01-17 (US holiday, no Yahoo bar)
- 2022-02-21 (US holiday, no Yahoo bar)
- 2023-01-16 (US holiday, no Yahoo bar)
- 2023-02-20 (US holiday, no Yahoo bar)
- 2024-01-15 (US holiday, no Yahoo bar)
- 2024-02-19 (US holiday, no Yahoo bar)
- 2025-01-20 (US holiday, no Yahoo bar)
- 2025-02-17 (US holiday, no Yahoo bar)
- 2026-01-19 (US holiday, no Yahoo bar)
- 2026-02-16 (US holiday, no Yahoo bar)

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
| 2022-01-17 | US holiday, no Yahoo bar (CME status to verify) |
| 2022-02-21 | US holiday, no Yahoo bar (CME status to verify) |
| 2022-04-15 | CME holiday (for user verification) |
| 2022-05-30 | CME holiday (for user verification) |
| 2022-06-20 | to verify |
| 2022-07-04 | CME holiday (for user verification) |
| 2022-09-05 | CME holiday (for user verification) |
| 2022-11-24 | CME holiday (for user verification) |
| 2022-12-26 | CME holiday (for user verification) |
| 2023-01-02 | CME holiday (for user verification) |
| 2023-01-16 | US holiday, no Yahoo bar (CME status to verify) |
| 2023-02-20 | US holiday, no Yahoo bar (CME status to verify) |
| 2023-04-07 | CME holiday (for user verification) |
| 2023-05-29 | CME holiday (for user verification) |
| 2023-06-19 | to verify |
| 2023-07-04 | CME holiday (for user verification) |
| 2023-09-04 | CME holiday (for user verification) |
| 2023-12-25 | CME holiday (for user verification) |
| 2024-01-01 | CME holiday (for user verification) |
| 2024-01-15 | US holiday, no Yahoo bar (CME status to verify) |
| 2024-02-19 | US holiday, no Yahoo bar (CME status to verify) |
| 2024-03-29 | CME holiday (for user verification) |
| 2024-05-27 | CME holiday (for user verification) |
| 2024-06-19 | to verify |
| 2024-07-04 | CME holiday (for user verification) |
| 2024-09-02 | CME holiday (for user verification) |
| 2024-11-28 | CME holiday (for user verification) |
| 2024-12-25 | CME holiday (for user verification) |
| 2025-01-01 | CME holiday (for user verification) |
| 2025-01-20 | US holiday, no Yahoo bar (CME status to verify) |
| 2025-02-17 | US holiday, no Yahoo bar (CME status to verify) |
| 2025-04-18 | CME holiday (for user verification) |
| 2025-05-26 | CME holiday (for user verification) |
| 2025-06-19 | to verify |
| 2025-09-01 | CME holiday (for user verification) |
| 2025-11-27 | CME holiday (for user verification) |
| 2025-12-25 | CME holiday (for user verification) |
| 2026-01-01 | CME holiday (for user verification) |
| 2026-01-19 | US holiday, no Yahoo bar (CME status to verify) |
| 2026-02-16 | US holiday, no Yahoo bar (CME status to verify) |
| 2026-04-03 | CME holiday (for user verification) |
| 2026-05-25 | CME holiday (for user verification) |
| 2026-06-19 | to verify |
| 2026-07-03 | CME holiday (for user verification) |

**Bars dated on a holiday date**

| Bar date | Close | Volume | Volume equals previous row | Note |
|---|---|---|---|---|
| 2023-11-23 | 81.37000274658203 | 40651.0 | True | bar dated on holiday (for user verification) |
| 2025-01-09 | 76.91999816894531 | 31706.0 | False | bar with volume: traded despite NYSE closure (to verify) |
| 2025-07-04 | 68.29000091552734 | 0.0 | True | bar dated on holiday (for user verification) |

**Top 10 absolute % daily moves on Close**

| Date | Prev Close | Close | % move |
|---|---|---|---|
| 2026-04-01 | 118.35 | 101.16 | -14.525 |
| 2026-04-08 | 109.27 | 94.75 | -13.288 |
| 2022-03-09 | 127.98 | 111.14 | -13.158 |
| 2021-11-26 | 82.25 | 72.72 | -11.587 |
| 2026-03-10 | 98.96 | 87.8 | -11.277 |
| 2026-03-23 | 112.19 | 99.94 | -10.919 |
| 2026-07-13 | 76.01 | 83.3 | 9.591 |
| 2026-03-12 | 91.98 | 100.46 | 9.219 |
| 2022-08-01 | 110.01 | 100.03 | -9.072 |
| 2026-04-17 | 99.39 | 90.38 | -9.065 |

**Roll candidates (tentative)**

> Roll candidates (tentative; none of these is a confirmed roll). HO=F/RB=F: expected expiry = last business day of each calendar month (CME rule: last trading day is the last business day of the month before the contract month); RB rule to verify by user. Business days = weekdays not in HOLIDAYS. BZ=F: NYMEX ch.698 - last UK business day of each calendar month, except December uses the second-to-last; weekdays only; UK bank holidays not applied; the +/-3-day window absorbs a 1-day shift.

Expected expiries (monthly, 2021-09 .. 2026-08) and the first trading day after each:

| Expected expiry | First trading day after | Close % move | Overnight gap (Open_t/Close_t-1 - 1) |
|---|---|---|---|
| 2021-09-30 | 2021-10-01 | 0.968 | -0.14 |
| 2021-10-29 | 2021-11-01 | 0.391 | -0.77 |
| 2021-11-30 | 2021-12-01 | -2.409 | -0.609 |
| 2021-12-30 | 2021-12-31 | -1.942 | -0.214 |
| 2022-01-31 | 2022-02-01 | -2.248 | -2.006 |
| 2022-02-28 | 2022-03-01 | 3.941 | -2.852 |
| 2022-03-31 | 2022-04-01 | -3.262 | -1.779 |
| 2022-04-29 | 2022-05-02 | -1.61 | -2.872 |
| 2022-05-31 | 2022-06-01 | -5.332 | -5.055 |
| 2022-06-30 | 2022-07-01 | -2.77 | -4.66 |
| 2022-07-29 | 2022-08-01 | -9.072 | -5.581 |
| 2022-08-31 | 2022-09-01 | -4.28 | -1.772 |
| 2022-09-30 | 2022-10-03 | 1.023 | -1.648 |
| 2022-10-31 | 2022-11-01 | -0.19 | -2.141 |
| 2022-11-30 | 2022-12-01 | 1.697 | 1.37 |
| 2022-12-29 | 2022-12-30 | 4.437 | 1.702 |
| 2023-01-31 | 2023-02-01 | -1.953 | 1.219 |
| 2023-02-28 | 2023-03-01 | 0.501 | -0.942 |
| 2023-03-31 | 2023-04-03 | 6.469 | 4.413 |
| 2023-04-28 | 2023-05-01 | -0.289 | 0.805 |
| 2023-05-31 | 2023-06-01 | 2.23 | -0.784 |
| 2023-06-30 | 2023-07-03 | -0.334 | 0.307 |
| 2023-07-31 | 2023-08-01 | -0.76 | -0.245 |
| 2023-08-31 | 2023-09-01 | 1.946 | -0.046 |
| 2023-09-29 | 2023-10-02 | -4.826 | -3.274 |
| 2023-10-31 | 2023-11-01 | -3.18 | -2.242 |
| 2023-11-30 | 2023-12-01 | -4.769 | -2.849 |
| 2023-12-28 | 2023-12-29 | -1.722 | -1.237 |
| 2024-01-31 | 2024-02-01 | -3.684 | -1.273 |
| 2024-02-29 | 2024-03-01 | -0.084 | -1.973 |
| 2024-03-29 | 2024-04-01 | -0.069 | -0.629 |
| 2024-04-30 | 2024-05-01 | -5.031 | -2.163 |
| 2024-05-31 | 2024-06-03 | -3.994 | -0.527 |
| 2024-06-28 | 2024-07-01 | 0.22 | -1.747 |
| 2024-07-31 | 2024-08-01 | -1.487 | 0.979 |
| 2024-08-30 | 2024-09-03 | -6.409 | -2.424 |
| 2024-09-30 | 2024-10-01 | 2.494 | 0.32 |
| 2024-10-31 | 2024-11-01 | -0.082 | 1.326 |
| 2024-11-29 | 2024-12-02 | -1.522 | -1.645 |
| 2024-12-30 | 2024-12-31 | 0.336 | -0.39 |
| 2025-01-31 | 2025-02-03 | -1.042 | 0.078 |
| 2025-02-28 | 2025-03-03 | -2.132 | -0.15 |
| 2025-03-31 | 2025-04-01 | -0.334 | -0.147 |
| 2025-04-30 | 2025-05-01 | -1.568 | -3.137 |
| 2025-05-30 | 2025-06-02 | 1.142 | -1.346 |
| 2025-06-30 | 2025-07-01 | -0.74 | -1.509 |
| 2025-07-31 | 2025-08-01 | -3.943 | -1.048 |
| 2025-08-29 | 2025-09-02 | 1.497 | -1.013 |
| 2025-09-30 | 2025-10-01 | -2.492 | -1.388 |
| 2025-10-31 | 2025-11-03 | -0.277 | 0.0 |
| 2025-11-28 | 2025-12-01 | -0.047 | -0.807 |
| 2025-12-30 | 2025-12-31 | -1.728 | -1.05 |
| 2026-01-30 | 2026-02-02 | -6.21 | -2.787 |
| 2026-02-27 | 2026-03-02 | 7.257 | 6.236 |
| 2026-03-31 | 2026-04-01 | -14.525 | -12.21 |
| 2026-04-30 | 2026-05-01 | -5.122 | -2.631 |
| 2026-05-29 | 2026-06-01 | 3.183 | 0.391 |
| 2026-06-30 | 2026-07-01 | -1.851 | 0.631 |
| 2026-07-31 | 2026-08-03 | -7.046 | -7.501 |

Top-10 moves tagged against the roll window (+/-3 trading days of an expected expiry; tentative, not confirmed):

| Date | % move | Roll window |
|---|---|---|
| 2026-04-01 | -14.525 | in roll window |
| 2026-04-08 | -13.288 | outside |
| 2022-03-09 | -13.158 | outside |
| 2021-11-26 | -11.587 | in roll window |
| 2026-03-10 | -11.277 | outside |
| 2026-03-23 | -10.919 | outside |
| 2026-07-13 | 9.591 | outside |
| 2026-03-12 | 9.219 | outside |
| 2022-08-01 | -9.072 | in roll window |
| 2026-04-17 | -9.065 | outside |

Summary (tentative):

| Group | Mean absolute Close % move |
|---|---|
| First day after expiry | 2.7474 |
| All other rows | 1.7229 |

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
| 2022-01-17 | US holiday, no Yahoo bar (CME status to verify) |
| 2022-02-21 | US holiday, no Yahoo bar (CME status to verify) |
| 2022-04-15 | CME holiday (for user verification) |
| 2022-05-30 | CME holiday (for user verification) |
| 2022-06-20 | to verify |
| 2022-07-04 | CME holiday (for user verification) |
| 2022-09-05 | CME holiday (for user verification) |
| 2022-11-24 | CME holiday (for user verification) |
| 2022-12-26 | CME holiday (for user verification) |
| 2023-01-02 | CME holiday (for user verification) |
| 2023-01-16 | US holiday, no Yahoo bar (CME status to verify) |
| 2023-02-20 | US holiday, no Yahoo bar (CME status to verify) |
| 2023-04-07 | CME holiday (for user verification) |
| 2023-05-29 | CME holiday (for user verification) |
| 2023-06-19 | to verify |
| 2023-07-04 | CME holiday (for user verification) |
| 2023-09-04 | CME holiday (for user verification) |
| 2023-12-25 | CME holiday (for user verification) |
| 2024-01-01 | CME holiday (for user verification) |
| 2024-01-15 | US holiday, no Yahoo bar (CME status to verify) |
| 2024-02-19 | US holiday, no Yahoo bar (CME status to verify) |
| 2024-03-29 | CME holiday (for user verification) |
| 2024-05-27 | CME holiday (for user verification) |
| 2024-06-19 | to verify |
| 2024-07-04 | CME holiday (for user verification) |
| 2024-09-02 | CME holiday (for user verification) |
| 2024-11-28 | CME holiday (for user verification) |
| 2024-12-25 | CME holiday (for user verification) |
| 2025-01-01 | CME holiday (for user verification) |
| 2025-01-20 | US holiday, no Yahoo bar (CME status to verify) |
| 2025-02-17 | US holiday, no Yahoo bar (CME status to verify) |
| 2025-04-18 | CME holiday (for user verification) |
| 2025-05-26 | CME holiday (for user verification) |
| 2025-06-19 | to verify |
| 2025-09-01 | CME holiday (for user verification) |
| 2025-11-27 | CME holiday (for user verification) |
| 2025-12-25 | CME holiday (for user verification) |
| 2026-01-01 | CME holiday (for user verification) |
| 2026-01-19 | US holiday, no Yahoo bar (CME status to verify) |
| 2026-02-16 | US holiday, no Yahoo bar (CME status to verify) |
| 2026-04-03 | CME holiday (for user verification) |
| 2026-05-25 | CME holiday (for user verification) |
| 2026-06-19 | to verify |
| 2026-07-03 | CME holiday (for user verification) |

**Bars dated on a holiday date**

| Bar date | Close | Volume | Volume equals previous row | Note |
|---|---|---|---|---|
| 2023-11-23 | 2.8712000846862793 | 33069.0 | True | bar dated on holiday (for user verification) |
| 2025-01-09 | 2.378200054168701 | 74771.0 | False | bar with volume: traded despite NYSE closure (to verify) |
| 2025-07-04 | 2.4089999198913574 | 0.0 | True | bar dated on holiday (for user verification) |

**Top 10 absolute % daily moves on Close**

| Date | Prev Close | Close | % move |
|---|---|---|---|
| 2022-03-09 | 4.4373 | 3.4643 | -21.928 |
| 2026-04-08 | 4.4774 | 3.8084 | -14.942 |
| 2026-02-02 | 2.7356 | 2.3598 | -13.737 |
| 2022-11-01 | 4.1909 | 3.6211 | -13.596 |
| 2022-03-08 | 3.9215 | 4.4373 | 13.153 |
| 2022-03-17 | 3.1001 | 3.4874 | 12.493 |
| 2021-11-26 | 2.383 | 2.0945 | -12.107 |
| 2022-05-02 | 4.7817 | 4.2049 | -12.063 |
| 2026-03-23 | 4.6084 | 4.056 | -11.987 |
| 2026-04-17 | 3.8329 | 3.3974 | -11.362 |

**Roll candidates (tentative)**

> Roll candidates (tentative; none of these is a confirmed roll). HO=F/RB=F: expected expiry = last business day of each calendar month (CME rule: last trading day is the last business day of the month before the contract month); RB rule to verify by user. Business days = weekdays not in HOLIDAYS. BZ=F: NYMEX ch.698 - last UK business day of each calendar month, except December uses the second-to-last; weekdays only; UK bank holidays not applied; the +/-3-day window absorbs a 1-day shift.

Expected expiries (monthly, 2021-09 .. 2026-08) and the first trading day after each:

| Expected expiry | First trading day after | Close % move | Overnight gap (Open_t/Close_t-1 - 1) |
|---|---|---|---|
| 2021-09-30 | 2021-10-01 | 1.751 | -0.09 |
| 2021-10-29 | 2021-11-01 | 0.268 | -0.801 |
| 2021-11-30 | 2021-12-01 | 0.644 | 0.959 |
| 2021-12-31 | 2022-01-03 | 1.172 | -0.077 |
| 2022-01-31 | 2022-02-01 | -0.652 | -1.461 |
| 2022-02-28 | 2022-03-01 | 4.57 | -2.734 |
| 2022-03-31 | 2022-04-01 | -7.239 | -8.702 |
| 2022-04-29 | 2022-05-02 | -12.063 | -16.473 |
| 2022-05-31 | 2022-06-01 | 1.281 | -1.733 |
| 2022-06-30 | 2022-07-01 | 1.044 | -1.275 |
| 2022-07-29 | 2022-08-01 | -5.096 | -2.276 |
| 2022-08-31 | 2022-09-01 | -4.15 | -1.731 |
| 2022-09-30 | 2022-10-03 | 0.003 | -3.087 |
| 2022-10-31 | 2022-11-01 | -13.596 | -12.15 |
| 2022-11-30 | 2022-12-01 | -2.988 | -0.268 |
| 2022-12-30 | 2023-01-03 | -8.2 | -1.954 |
| 2023-01-31 | 2023-02-01 | -7.265 | -1.263 |
| 2023-02-28 | 2023-03-01 | 1.875 | -0.805 |
| 2023-03-31 | 2023-04-03 | -0.512 | 1.764 |
| 2023-04-28 | 2023-05-01 | 0.151 | -0.273 |
| 2023-05-31 | 2023-06-01 | 2.438 | -0.867 |
| 2023-06-30 | 2023-07-03 | -2.896 | -0.474 |
| 2023-07-31 | 2023-08-01 | 1.087 | 0.184 |
| 2023-08-31 | 2023-09-01 | -1.196 | -0.831 |
| 2023-09-29 | 2023-10-02 | -4.155 | -2.156 |
| 2023-10-31 | 2023-11-01 | -0.986 | -2.103 |
| 2023-11-30 | 2023-12-01 | -5.971 | -3.091 |
| 2023-12-29 | 2024-01-02 | -1.069 | 0.008 |
| 2024-01-31 | 2024-02-01 | -3.394 | -0.491 |
| 2024-02-29 | 2024-03-01 | 0.76 | -1.174 |
| 2024-03-28 | 2024-04-01 | 0.44 | 0.226 |
| 2024-04-30 | 2024-05-01 | -2.447 | 0.342 |
| 2024-05-31 | 2024-06-03 | -2.852 | 0.998 |
| 2024-06-28 | 2024-07-01 | 3.886 | 1.101 |
| 2024-07-31 | 2024-08-01 | -0.377 | 1.677 |
| 2024-08-30 | 2024-09-03 | -2.021 | 1.292 |
| 2024-09-30 | 2024-10-01 | 1.989 | 1.21 |
| 2024-10-31 | 2024-11-01 | 0.662 | 2.046 |
| 2024-11-29 | 2024-12-02 | -0.698 | 0.497 |
| 2024-12-31 | 2025-01-02 | 1.439 | -0.06 |
| 2025-01-31 | 2025-02-03 | -0.861 | -0.724 |
| 2025-02-28 | 2025-03-03 | -4.013 | -1.316 |
| 2025-03-31 | 2025-04-01 | -1.085 | -1.465 |
| 2025-04-30 | 2025-05-01 | -1.213 | -1.689 |
| 2025-05-30 | 2025-06-02 | 1.353 | -0.664 |
| 2025-06-30 | 2025-07-01 | -0.806 | -3.253 |
| 2025-07-31 | 2025-08-01 | -4.151 | -0.042 |
| 2025-08-29 | 2025-09-02 | 4.751 | -0.049 |
| 2025-09-30 | 2025-10-01 | -1.312 | -0.527 |
| 2025-10-31 | 2025-11-03 | -1.065 | -1.246 |
| 2025-11-28 | 2025-12-01 | 0.3 | -0.566 |
| 2025-12-31 | 2026-01-02 | -0.259 | 0.816 |
| 2026-01-30 | 2026-02-02 | -13.737 | -8.057 |
| 2026-02-27 | 2026-03-02 | 8.593 | 7.17 |
| 2026-03-31 | 2026-04-01 | -2.56 | -0.946 |
| 2026-04-30 | 2026-05-01 | -4.639 | -1.073 |
| 2026-05-29 | 2026-06-01 | 2.886 | 0.212 |
| 2026-06-30 | 2026-07-01 | -2.982 | -2.765 |
| 2026-07-31 | 2026-08-03 | -5.927 | -3.482 |

Top-10 moves tagged against the roll window (+/-3 trading days of an expected expiry; tentative, not confirmed):

| Date | % move | Roll window |
|---|---|---|
| 2022-03-09 | -21.928 | outside |
| 2026-04-08 | -14.942 | outside |
| 2026-02-02 | -13.737 | in roll window |
| 2022-11-01 | -13.596 | in roll window |
| 2022-03-08 | 13.153 | outside |
| 2022-03-17 | 12.493 | outside |
| 2021-11-26 | -12.107 | in roll window |
| 2022-05-02 | -12.063 | in roll window |
| 2026-03-23 | -11.987 | outside |
| 2026-04-17 | -11.362 | outside |

Summary (tentative):

| Group | Mean absolute Close % move |
|---|---|
| First day after expiry | 3.0132 |
| All other rows | 1.9521 |

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
| 2022-01-17 | US holiday, no Yahoo bar (CME status to verify) |
| 2022-02-21 | US holiday, no Yahoo bar (CME status to verify) |
| 2022-04-15 | CME holiday (for user verification) |
| 2022-05-30 | CME holiday (for user verification) |
| 2022-06-20 | to verify |
| 2022-07-04 | CME holiday (for user verification) |
| 2022-09-05 | CME holiday (for user verification) |
| 2022-11-24 | CME holiday (for user verification) |
| 2022-12-26 | CME holiday (for user verification) |
| 2023-01-02 | CME holiday (for user verification) |
| 2023-01-16 | US holiday, no Yahoo bar (CME status to verify) |
| 2023-02-20 | US holiday, no Yahoo bar (CME status to verify) |
| 2023-04-07 | CME holiday (for user verification) |
| 2023-05-29 | CME holiday (for user verification) |
| 2023-06-19 | to verify |
| 2023-07-04 | CME holiday (for user verification) |
| 2023-09-04 | CME holiday (for user verification) |
| 2023-12-25 | CME holiday (for user verification) |
| 2024-01-01 | CME holiday (for user verification) |
| 2024-01-15 | US holiday, no Yahoo bar (CME status to verify) |
| 2024-02-19 | US holiday, no Yahoo bar (CME status to verify) |
| 2024-03-29 | CME holiday (for user verification) |
| 2024-05-27 | CME holiday (for user verification) |
| 2024-06-19 | to verify |
| 2024-07-04 | CME holiday (for user verification) |
| 2024-09-02 | CME holiday (for user verification) |
| 2024-11-28 | CME holiday (for user verification) |
| 2024-12-25 | CME holiday (for user verification) |
| 2025-01-01 | CME holiday (for user verification) |
| 2025-01-20 | US holiday, no Yahoo bar (CME status to verify) |
| 2025-02-17 | US holiday, no Yahoo bar (CME status to verify) |
| 2025-04-18 | CME holiday (for user verification) |
| 2025-05-26 | CME holiday (for user verification) |
| 2025-06-19 | to verify |
| 2025-09-01 | CME holiday (for user verification) |
| 2025-11-27 | CME holiday (for user verification) |
| 2025-12-25 | CME holiday (for user verification) |
| 2026-01-01 | CME holiday (for user verification) |
| 2026-01-19 | US holiday, no Yahoo bar (CME status to verify) |
| 2026-02-16 | US holiday, no Yahoo bar (CME status to verify) |
| 2026-04-03 | CME holiday (for user verification) |
| 2026-05-25 | CME holiday (for user verification) |
| 2026-06-19 | to verify |
| 2026-07-03 | CME holiday (for user verification) |

**Bars dated on a holiday date**

| Bar date | Close | Volume | Volume equals previous row | Note |
|---|---|---|---|---|
| 2023-11-23 | 2.214400053024292 | 38662.0 | True | bar dated on holiday (for user verification) |
| 2025-01-09 | 2.0283000469207764 | 45540.0 | False | bar with volume: traded despite NYSE closure (to verify) |
| 2025-07-04 | 2.1171000003814697 | 0.0 | True | bar dated on holiday (for user verification) |

**Top 10 absolute % daily moves on Close**

| Date | Prev Close | Close | % move |
|---|---|---|---|
| 2026-03-02 | 2.0779 | 2.3706 | 14.086 |
| 2022-08-01 | 3.4881 | 2.9981 | -14.048 |
| 2024-03-01 | 2.3043 | 2.6144 | 13.457 |
| 2021-11-26 | 2.3197 | 2.0294 | -12.515 |
| 2025-03-03 | 1.9703 | 2.1878 | 11.039 |
| 2024-09-03 | 2.2117 | 1.9777 | -10.58 |
| 2022-03-09 | 3.6826 | 3.2938 | -10.558 |
| 2022-03-01 | 2.797 | 3.0887 | 10.429 |
| 2023-03-01 | 2.4343 | 2.6748 | 9.88 |
| 2022-07-05 | 3.6878 | 3.329 | -9.729 |

**Roll candidates (tentative)**

> Roll candidates (tentative; none of these is a confirmed roll). HO=F/RB=F: expected expiry = last business day of each calendar month (CME rule: last trading day is the last business day of the month before the contract month); RB rule to verify by user. Business days = weekdays not in HOLIDAYS. BZ=F: NYMEX ch.698 - last UK business day of each calendar month, except December uses the second-to-last; weekdays only; UK bank holidays not applied; the +/-3-day window absorbs a 1-day shift.

Expected expiries (monthly, 2021-09 .. 2026-08) and the first trading day after each:

| Expected expiry | First trading day after | Close % move | Overnight gap (Open_t/Close_t-1 - 1) |
|---|---|---|---|
| 2021-09-30 | 2021-10-01 | -0.16 | -2.782 |
| 2021-10-29 | 2021-11-01 | -2.141 | -3.928 |
| 2021-11-30 | 2021-12-01 | -1.465 | -1.035 |
| 2021-12-31 | 2022-01-03 | 1.256 | -0.354 |
| 2022-01-31 | 2022-02-01 | 0.818 | 0.106 |
| 2022-02-28 | 2022-03-01 | 10.429 | 5.309 |
| 2022-03-31 | 2022-04-01 | -1.132 | -0.944 |
| 2022-04-29 | 2022-05-02 | 1.094 | -1.069 |
| 2022-05-31 | 2022-06-01 | -0.216 | -2.956 |
| 2022-06-30 | 2022-07-01 | 1.041 | -2.54 |
| 2022-07-29 | 2022-08-01 | -14.048 | -10.926 |
| 2022-08-31 | 2022-09-01 | -8.465 | -7.506 |
| 2022-09-30 | 2022-10-03 | 1.63 | -3.393 |
| 2022-10-31 | 2022-11-01 | -7.692 | -10.488 |
| 2022-11-30 | 2022-12-01 | -3.163 | -1.852 |
| 2022-12-30 | 2023-01-03 | -3.997 | 1.277 |
| 2023-01-31 | 2023-02-01 | -3.527 | 0.751 |
| 2023-02-28 | 2023-03-01 | 9.88 | 8.532 |
| 2023-03-31 | 2023-04-03 | 2.111 | 3.388 |
| 2023-04-28 | 2023-05-01 | -1.071 | -1.765 |
| 2023-05-31 | 2023-06-01 | -4.832 | -5.18 |
| 2023-06-30 | 2023-07-03 | -6.515 | -3.705 |
| 2023-07-31 | 2023-08-01 | -1.912 | -0.867 |
| 2023-08-31 | 2023-09-01 | -6.333 | -7.468 |
| 2023-09-29 | 2023-10-02 | -1.135 | -1.857 |
| 2023-10-31 | 2023-11-01 | -1.674 | 0.216 |
| 2023-11-30 | 2023-12-01 | -3.578 | -1.741 |
| 2023-12-29 | 2024-01-02 | -0.366 | 0.304 |
| 2024-01-31 | 2024-02-01 | 0.527 | 2.015 |
| 2024-02-29 | 2024-03-01 | 13.457 | 11.973 |
| 2024-03-28 | 2024-04-01 | -1.851 | -1.46 |
| 2024-04-30 | 2024-05-01 | -4.921 | -1.125 |
| 2024-05-31 | 2024-06-03 | -3.726 | -0.243 |
| 2024-06-28 | 2024-07-01 | 1.945 | -0.759 |
| 2024-07-31 | 2024-08-01 | -3.384 | -0.806 |
| 2024-08-30 | 2024-09-03 | -10.58 | -5.34 |
| 2024-09-30 | 2024-10-01 | 0.229 | -1.595 |
| 2024-10-31 | 2024-11-01 | -1.847 | -0.125 |
| 2024-11-29 | 2024-12-02 | -1.363 | -1.991 |
| 2024-12-31 | 2025-01-02 | 2.518 | 0.375 |
| 2025-01-31 | 2025-02-03 | 3.987 | 4.041 |
| 2025-02-28 | 2025-03-03 | 11.039 | 13.135 |
| 2025-03-31 | 2025-04-01 | 0.85 | 0.215 |
| 2025-04-30 | 2025-05-01 | 0.599 | -0.648 |
| 2025-05-30 | 2025-06-02 | 0.692 | -1.143 |
| 2025-06-30 | 2025-07-01 | 0.986 | -0.692 |
| 2025-07-31 | 2025-08-01 | -4.378 | -1.891 |
| 2025-08-29 | 2025-09-02 | -6.619 | -10.23 |
| 2025-09-30 | 2025-10-01 | -4.41 | -2.742 |
| 2025-10-31 | 2025-11-03 | -3.863 | -4.631 |
| 2025-11-28 | 2025-12-01 | -1.424 | -3.682 |
| 2025-12-31 | 2026-01-02 | -0.422 | 0.299 |
| 2026-01-30 | 2026-02-02 | -3.713 | 0.889 |
| 2026-02-27 | 2026-03-02 | 14.086 | 19.544 |
| 2026-03-31 | 2026-04-01 | -6.669 | -3.762 |
| 2026-04-30 | 2026-05-01 | -4.675 | -3.723 |
| 2026-05-29 | 2026-06-01 | -1.343 | -2.303 |
| 2026-06-30 | 2026-07-01 | -2.296 | -3.493 |
| 2026-07-31 | 2026-08-03 | -7.912 | -5.327 |

Top-10 moves tagged against the roll window (+/-3 trading days of an expected expiry; tentative, not confirmed):

| Date | % move | Roll window |
|---|---|---|
| 2026-03-02 | 14.086 | in roll window |
| 2022-08-01 | -14.048 | in roll window |
| 2024-03-01 | 13.457 | in roll window |
| 2021-11-26 | -12.515 | in roll window |
| 2025-03-03 | 11.039 | in roll window |
| 2024-09-03 | -10.58 | in roll window |
| 2022-03-09 | -10.558 | outside |
| 2022-03-01 | 10.429 | in roll window |
| 2023-03-01 | 9.88 | in roll window |
| 2022-07-05 | -9.729 | in roll window |

Summary (tentative):

| Group | Mean absolute Close % move |
|---|---|
| First day after expiry | 3.8643 |
| All other rows | 1.7133 |

## USD/MNT: Bank of Mongolia

- Input: `data/raw/bom_currency-rate-USD.xlsx`, columns `Date`, `USD - US dollar` (untouched; no fill/drop/align).
- Source: https://www.mongolbank.mn/en/currency-rates (retrieved 2026-11-20).
- User spot-checked: 2021-09-01 = 2848.60 and 2026-08-31 = 3595.14 on the website.

| Check | Result |
|---|---|
| Row count | 1826 |
| Date range | 2021-09-01 .. 2026-08-31 |
| Duplicate dates | 0 |
| Timestamps not 08:00 | 0 (date part used for all checks below) |
| Minimum | 2848.44 on 2021-11-24 |
| Maximum | 3595.66 on 2026-08-27 |
| Share of unchanged days (weekdays only) | 0.056 |
| Longest run of unchanged weekdays | 6 (2025-07-10 .. 2025-07-17) |

**Top 5 absolute % daily moves (weekdays only)**

| Date | Abs % move |
|---|---|
| 2022-04-05 | 0.818 |
| 2022-04-01 | 0.762 |
| 2022-10-04 | 0.495 |
| 2022-09-26 | 0.47 |
| 2022-09-19 | 0.46 |

## USDMNT=X

- Download call (`scripts/stage1_download.py`): `yf.Ticker("USDMNT=X").history(start="2021-09-01", end="2026-09-01", auto_adjust=False, actions=False, timeout=30)`, retried 3x.
- Error: `YFPricesMissingError: $USDMNT=X: possibly delisted; no price data found (1d 2021-09-01 -> 2026-09-01)` on all 3 attempts.
- Yahoo offers only 1d/5d periods for this ticker (user-confirmed 2026-11-20), so no historical daily series is available; USDMNT is excluded from Stage 1. Bank of Mongolia rates to be supplied separately.
