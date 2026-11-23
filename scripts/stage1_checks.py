#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stage 1 (checks, part C): integrity, missing weekdays, top moves and
USDMNT record for BZ=F, HO=F, RB=F. Writes outputs/stage1_checks.md.

Scope: data assembly only. No modelling. Reads data/raw/ only. No network.
No installs. Does not fill/drop/align values.
Close is described as "Yahoo daily close; not verified to equal the
official exchange settlement price."
"""
import os
from collections import Counter

import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(REPO, "data", "raw")
OUT_DIR = os.path.join(REPO, "outputs")
OUT_PATH = os.path.join(OUT_DIR, "stage1_checks.md")
OUT_REL = os.path.relpath(OUT_PATH, REPO)

TICKERS = ["BZ=F", "HO=F", "RB=F"]
PRICE_COLS = ["Open", "High", "Low", "Close", "Adj Close"]
VOL_COL = "Volume"
EXCHANGE_TZ = "America/New_York"

CLOSE_NOTE = (
    "Close is Yahoo daily close; not verified to equal the official "
    "exchange settlement price."
)

# Holiday dates within the data window. Hard-coded, exact; all "for user
# verification". 2025-01-09 is no longer in the holiday list (it HAS a bar).
JUNETEENTH = {
    "2022-06-20", "2023-06-19", "2024-06-19", "2025-06-19", "2026-06-19",
}
MLK_DAY = {
    "2022-01-17", "2023-01-16", "2024-01-15", "2025-01-20", "2026-01-19",
}
PRESIDENTS_DAY = {
    "2022-02-21", "2023-02-20", "2024-02-19", "2025-02-17", "2026-02-16",
}
US_HOL_NO_BAR = MLK_DAY | PRESIDENTS_DAY
SPECIAL_20250109 = "2025-01-09"

CME_HOLIDAYS = {
    # New Year
    "2023-01-02", "2024-01-01", "2025-01-01", "2026-01-01",
    # Good Friday
    "2022-04-15", "2023-04-07", "2024-03-29", "2025-04-18", "2026-04-03",
    # Memorial Day
    "2022-05-30", "2023-05-29", "2024-05-27", "2025-05-26", "2026-05-25",
    # Juneteenth
    *JUNETEENTH,
    # Independence Day
    "2022-07-04", "2023-07-04", "2024-07-04", "2025-07-04", "2026-07-03",
    # Labor Day
    "2021-09-06", "2022-09-05", "2023-09-04", "2024-09-02", "2025-09-01",
    # Thanksgiving
    "2021-11-25", "2022-11-24", "2023-11-23", "2024-11-28", "2025-11-27",
    # Christmas
    "2021-12-24", "2022-12-26", "2023-12-25", "2024-12-25", "2025-12-25",
}

# All dates we scan for bars dated on a holiday (CME + US-no-bar + special).
ALL_HOLIDAY_DATES = {pd.Timestamp(s).normalize() for s in
                     (CME_HOLIDAYS | US_HOL_NO_BAR | {SPECIAL_20250109})}


def classify_missing(date_str):
    if date_str in JUNETEENTH:
        return "to verify"
    if date_str in US_HOL_NO_BAR:
        return "US holiday, no Yahoo bar (CME status to verify)"
    if date_str in CME_HOLIDAYS:
        return "CME holiday (for user verification)"
    return "unexplained"


ROLL_RANGE_START = "2021-09-01"
ROLL_RANGE_END = "2026-08-01"

ROLL_NOTE = (
    "Roll candidates (tentative; none of these is a confirmed roll). "
    "HO=F/RB=F: expected expiry = last business day of each calendar month "
    "(CME rule: last trading day is the last business day of the month before "
    "the contract month); RB rule to verify by user. Business days = weekdays "
    "not in HOLIDAYS. BZ=F: NYMEX ch.698 - last UK business day of each "
    "calendar month, except December uses the second-to-last; weekdays only; "
    "UK bank holidays not applied; the +/-3-day window absorbs a 1-day shift."
)


def expected_expiries(ticker):
    """Tentative expected last trading days, 2021-09 .. 2026-08."""
    months = pd.date_range(ROLL_RANGE_START, ROLL_RANGE_END, freq="MS")
    expiries = []
    for m in months:
        start = m
        end = m + pd.offsets.MonthEnd(0)
        weekdays = list(pd.date_range(start, end, freq="B"))
        if ticker in ("HO=F", "RB=F"):
            bus = [d for d in weekdays if d.normalize() not in ALL_HOLIDAY_DATES]
            exp = max(bus)
        else:  # BZ=F
            exp = weekdays[-2] if m.month == 12 else weekdays[-1]
        expiries.append(pd.Timestamp(exp).normalize())
    return expiries


def roll_analysis(ticker, df):
    """Build the tentative roll-candidates table for one series."""
    expiries = expected_expiries(ticker)
    d = df.reset_index(drop=True)
    date_arr = d["date"].to_numpy()  # sorted ascending
    close = d["Close"].astype(float)
    open_ = d["Open"].astype(float)
    prev_close = close.shift(1)
    pct = (close / prev_close - 1) * 100.0
    gap = (open_ / prev_close - 1) * 100.0

    exp_ts = np.array([pd.Timestamp(e).to_datetime64() for e in expiries])
    # Position in the trading-day timeline = # rows with date <= expiry.
    expiry_pos = np.searchsorted(date_arr, exp_ts, side="right")

    # First trading day strictly after each expected expiry.
    first_after = []
    for e, epos in zip(expiries, expiry_pos):
        if epos >= len(d):
            continue  # no data after this expiry (tail of the sample)
        i = int(epos)
        first_after.append(
            {
                "expiry": pd.Timestamp(e).strftime("%Y-%m-%d"),
                "date": d.loc[i, "date"].strftime("%Y-%m-%d"),
                "pct": round(float(pct.iloc[i]), 3),
                "gap": round(float(gap.iloc[i]), 3),
            }
        )

    # Tag each top-10 move: in roll window iff within +/-3 trading days of an
    # expected expiry (trading-day position distance).
    moves = pd.DataFrame({"date": d["date"], "pct": pct}).dropna(subset=["pct"])
    moves = moves.assign(apct=moves["pct"].abs()).sort_values("apct", ascending=False)
    top10_tagged = []
    for r in moves.head(10).itertuples(index=False):
        pos = int(np.searchsorted(date_arr, r.date.to_datetime64(), side="right")) - 1
        in_win = any(abs(pos - int(ep)) <= 3 for ep in expiry_pos if int(ep) < len(d))
        top10_tagged.append(
            (r.date.strftime("%Y-%m-%d"), round(float(r.pct), 3),
             "in roll window" if in_win else "outside")
        )

    # Summary: mean |pct| on first-day-after-expiry rows vs all other rows.
    first_pct = [fa["pct"] for fa in first_after]
    others = pct.dropna().drop(labels=[int(np.searchsorted(date_arr,
                pd.Timestamp(fa["date"]).to_datetime64(), side="right")) - 1
                for fa in first_after], errors="ignore")
    mean_first = float(np.mean(np.abs(first_pct))) if first_pct else float("nan")
    mean_others = float(others.abs().mean()) if len(others) else float("nan")

    return {
        "expiries": expiries,
        "first_after": first_after,
        "top10_tagged": top10_tagged,
        "mean_first": mean_first,
        "mean_others": mean_others,
    }


def load_series(ticker):
    path = os.path.join(RAW_DIR, f"{ticker}.csv")
    df = pd.read_csv(path, index_col=0)
    # Measure the offsets actually present in the CSV before normalization.
    raw_ts = [pd.Timestamp(s) for s in df.index]
    offset_counts = Counter(int(t.utcoffset().total_seconds() / 60) for t in raw_ts)
    not_midnight = sum(1 for t in raw_ts if (t.hour, t.minute, t.second) != (0, 0, 0))
    # Normalize mixed DST offsets to UTC, then convert to the exchange tz.
    idx = pd.to_datetime(df.index, utc=True)
    idx = idx.tz_convert(EXCHANGE_TZ)
    dates = idx.tz_localize(None)
    df = df.copy()
    df.index = idx
    df["date"] = dates
    return df, offset_counts, not_midnight


def analyze(ticker):
    df, offset_counts, not_midnight = load_series(ticker)
    n_rows = len(df)
    d_min = df["date"].min()
    d_max = df["date"].max()

    dup_dates = int(df.index.duplicated().sum())

    zero_neg = {}
    for c in PRICE_COLS:
        zero_neg[c] = int((df[c] <= 0).sum())

    zv_mask = df[VOL_COL] == 0
    zero_vol = int(zv_mask.sum())
    zv_dates = df.loc[zv_mask, "date"].dt.strftime("%Y-%m-%d").tolist()

    adj_diff_mask = df["Adj Close"] != df["Close"]
    n_adj_diff = int(adj_diff_mask.sum())
    adj_diff_dates = df.loc[adj_diff_mask, "date"].dt.strftime("%Y-%m-%d").tolist()[:10]

    # Missing weekdays: Mon-Fri between first and last date with no row.
    bdate = pd.bdate_range(d_min, d_max)
    present = set(df["date"])
    missing_cls = [
        (d.strftime("%Y-%m-%d"), classify_missing(d.strftime("%Y-%m-%d")))
        for d in bdate
        if d not in present
    ]

    # Rows that EXIST on a date in the holiday scan set (incl. 2025-01-09).
    prev_vol = df[VOL_COL].shift(1)
    exist_mask = df["date"].isin(ALL_HOLIDAY_DATES)
    exist_holiday_rows = []
    for i, dt in df.loc[exist_mask, "date"].items():
        ds = dt.strftime("%Y-%m-%d")
        vol = float(df.at[i, VOL_COL])
        pv = prev_vol.at[i]
        eq = pd.notna(pv) and (float(pv) == vol)
        note = ("bar with volume: traded despite NYSE closure (to verify)"
                if ds == SPECIAL_20250109
                else "bar dated on holiday (for user verification)")
        exist_holiday_rows.append((ds, float(df.at[i, "Close"]), vol, eq, note))

    # Top 10 absolute % daily moves on Close (Close_t / Close_{t-1} - 1).
    close = df["Close"].astype(float)
    pct = close.pct_change() * 100.0
    prev = close.shift(1)
    moves = pd.DataFrame(
        {"date": df["date"], "prev": prev, "close": close, "pct": pct}
    ).dropna(subset=["pct"])
    moves = moves.assign(apct=moves["pct"].abs()).sort_values(
        "apct", ascending=False
    )
    top10 = [
        (r.date.strftime("%Y-%m-%d"), round(float(r.prev), 4),
         round(float(r.close), 4), round(float(r.pct), 3))
        for r in moves.head(10).itertuples(index=False)
    ]

    roll = roll_analysis(ticker, df)

    return {
        "ticker": ticker,
        "rows": n_rows,
        "date_min": d_min,
        "date_max": d_max,
        "offset_counts": offset_counts,
        "not_midnight": not_midnight,
        "dup_dates": dup_dates,
        "zero_neg": zero_neg,
        "zero_vol": zero_vol,
        "zv_dates": zv_dates,
        "n_adj_diff": n_adj_diff,
        "adj_diff_dates": adj_diff_dates,
        "missing_cls": missing_cls,
        "exist_holiday_rows": exist_holiday_rows,
        "top10": top10,
        "roll": roll,
    }


def analyze_bom_usd():
    """USD/MNT: Bank of Mongolia. Reads the xlsx as-is; no fill/drop/align."""
    path = os.path.join(RAW_DIR, "bom_currency-rate-USD.xlsx")
    df = pd.read_excel(path)
    df = df.rename(columns={"USD - US dollar": "rate"})
    date = pd.to_datetime(df["Date"])
    rate = df["rate"].astype(float)

    n_rows = int(len(df))
    date_min = date.min()
    date_max = date.max()
    dup_dates = int(date.duplicated().sum())

    # Every timestamp is 08:00 (date part used for the analysis).
    non_0800 = int((date.dt.hour != 8).sum())
    # Date-only series (no fill/drop/align) ordered ascending by date.
    s = pd.Series(rate.values, index=pd.DatetimeIndex(date).normalize())
    s = s[~s.index.duplicated()].sort_index()

    arg_min = s.idxmin()
    arg_max = s.idxmax()
    min_val = float(s.loc[arg_min])
    max_val = float(s.loc[arg_max])

    # Weekday-only unchanged days: value equals the previous weekday's value.
    wd = s[s.index.dayofweek < 5]
    unchanged = (wd == wd.shift(1)).dropna()
    share = float(unchanged.mean())

    # Longest run of consecutive unchanged weekdays (with dates).
    run = 0
    best_run = 0
    best_dates = []
    cur_dates = []
    for dt, v in unchanged.items():
        if v:
            run += 1
            cur_dates.append(dt)
        else:
            if run > best_run:
                best_run = run
                best_dates = cur_dates
            run = 0
            cur_dates = []
    if run > best_run:
        best_run = run
        best_dates = cur_dates

    # Top 5 absolute % daily moves (on weekdays, date-part ordering).
    moves = wd.pct_change() * 100.0
    moves = moves.dropna().abs().sort_values(ascending=False)
    top5 = [
        (dt.strftime("%Y-%m-%d"), round(float(m), 3))
        for dt, m in moves.head(5).items()
    ]

    return {
        "rows": n_rows,
        "date_min": date_min,
        "date_max": date_max,
        "non_0800": non_0800,
        "dup_dates": dup_dates,
        "min_date": arg_min.strftime("%Y-%m-%d"),
        "min_val": min_val,
        "max_date": arg_max.strftime("%Y-%m-%d"),
        "max_val": max_val,
        "unchanged_share": share,
        "longest_run": best_run,
        "longest_dates": [d.strftime("%Y-%m-%d") for d in best_dates],
        "top5": top5,
    }


def render_bom_usd(r):
    lines = []
    lines.append("## USD/MNT: Bank of Mongolia")
    lines.append("")
    lines.append("- Input: `data/raw/bom_currency-rate-USD.xlsx`, columns "
                 "`Date`, `USD - US dollar` (untouched; no fill/drop/align).")
    lines.append("- Source: https://www.mongolbank.mn/en/currency-rates "
                 "(retrieved 2026-11-20).")
    lines.append("- User spot-checked: 2021-09-01 = 2848.60 and "
                 "2026-08-31 = 3595.14 on the website.")
    lines.append("")
    lines.append("| Check | Result |")
    lines.append("|---|---|")
    lines.append(f"| Row count | {r['rows']} |")
    lines.append(f"| Date range | {r['date_min'].date()} .. {r['date_max'].date()} |")
    lines.append(f"| Duplicate dates | {r['dup_dates']} |")
    lines.append(f"| Timestamps not 08:00 | {r['non_0800']} "
                 "(date part used for all checks below) |")
    lines.append(f"| Minimum | {r['min_val']} on {r['min_date']} |")
    lines.append(f"| Maximum | {r['max_val']} on {r['max_date']} |")
    lines.append(f"| Share of unchanged days (weekdays only) | "
                 f"{r['unchanged_share']:.3f} |")
    lines.append(f"| Longest run of unchanged weekdays | {r['longest_run']} "
                 f"({r['longest_dates'][0]} .. {r['longest_dates'][-1]}) |")
    lines.append("")
    lines.append("**Top 5 absolute % daily moves (weekdays only)**")
    lines.append("")
    lines.append("| Date | Abs % move |")
    lines.append("|---|---|")
    for d, m in r["top5"]:
        lines.append(f"| {d} | {m} |")
    lines.append("")
    return lines


def render(results, bom_result):
    lines = []
    lines.append("# Stage 1 checks (part C) - integrity, weekdays, moves")
    lines.append("")
    lines.append(f"- Script: `scripts/stage1_checks.py`")
    lines.append("- Input: `data/raw/{BZ=F,HO=F,RB=F}.csv` and "
                 "`data/raw/bom_currency-rate-USD.xlsx` (untouched)")
    lines.append("")
    lines.append(f"- Script: `scripts/stage1_checks.py`")
    lines.append("- Input: `data/raw/{BZ=F,HO=F,RB=F}.csv` (untouched)")
    lines.append(f"- Output: `{OUT_REL}`")
    lines.append("")
    lines.append(f"> {CLOSE_NOTE}")
    lines.append("")
    lines.append("## Holiday list used (for user verification)")
    lines.append("")
    lines.append("Legend:")
    lines.append("- `CME holiday (for user verification)`: the dates below, except Juneteenth")
    lines.append("- `to verify`: Juneteenth dates")
    lines.append("- `US holiday, no Yahoo bar (CME status to verify)`: MLK and Presidents' Day")
    lines.append("- `unexplained`: any other missing weekday")
    lines.append("- 2025-01-09: removed from the list; it HAS a bar (see holiday-bars table)")
    lines.append("")
    lines.append("CME holidays:")
    for d in sorted(CME_HOLIDAYS - JUNETEENTH):
        lines.append(f"- {d} (CME holiday)")
    lines.append("")
    lines.append("Juneteenth (to verify):")
    for d in sorted(JUNETEENTH):
        lines.append(f"- {d} (to verify)")
    lines.append("")
    lines.append("MLK / Presidents' Day (US holiday, no Yahoo bar; CME status to verify):")
    for d in sorted(US_HOL_NO_BAR):
        lines.append(f"- {d} (US holiday, no Yahoo bar)")
    lines.append("")
    lines.append("## Per-series checks")
    lines.append("")

    for r in results:
        lines.append(f"### {r['ticker']}")
        lines.append("")
        lines.append("| Check | Result |")
        lines.append("|---|---|")
        lines.append(f"| Row count | {r['rows']} |")
        lines.append(
            f"| Date range | {r['date_min'].date()} .. {r['date_max'].date()} |"
        )
        lines.append(f"| Index timezone (measured) | see offset table below |")
        lines.append(
            f"| Conversion to plain dates | tz_convert to {EXCHANGE_TZ}, then `.date()` |"
        )
        lines.append(f"| Duplicate dates | {r['dup_dates']} |")
        lines.append("| Zero/negative prices per column | |")
        lines.append("| &nbsp;&nbsp;Open | {} |".format(r["zero_neg"]["Open"]))
        lines.append("| &nbsp;&nbsp;High | {} |".format(r["zero_neg"]["High"]))
        lines.append("| &nbsp;&nbsp;Low | {} |".format(r["zero_neg"]["Low"]))
        lines.append("| &nbsp;&nbsp;Close | {} |".format(r["zero_neg"]["Close"]))
        lines.append("| &nbsp;&nbsp;Adj Close | {} |".format(r["zero_neg"]["Adj Close"]))
        lines.append(f"| Zero-volume days | {r['zero_vol']} |")
        if r["zv_dates"]:
            lines.append(
                "| &nbsp;&nbsp;Dates | {} |".format(", ".join(r["zv_dates"]))
            )
        lines.append(f"| Rows where Adj Close != Close | {r['n_adj_diff']} |")
        if r["n_adj_diff"] > 0:
            lines.append(
                "| &nbsp;&nbsp;First dates | {} |".format(", ".join(r["adj_diff_dates"]))
            )
        lines.append("")
        lines.append("**Index timezone (measured)**")
        lines.append("")
        lines.append("| UTC offset | Rows |")
        lines.append("|---|---|")
        for mins in sorted(r["offset_counts"]):
            sign = "+" if mins >= 0 else "-"
            a = abs(mins)
            label = f"{sign}{a // 60:02d}:{a % 60:02d} (UTC{mins:+d} min)"
            lines.append(f"| {label} | {r['offset_counts'][mins]} |")
        lines.append(f"| Rows whose local time is not 00:00 | {r['not_midnight']} |")
        lines.append("")
        lines.append("**Missing weekdays**")
        lines.append("")
        if r["missing_cls"]:
            lines.append("| Missing weekday | Classification |")
            lines.append("|---|---|")
            for d, c in r["missing_cls"]:
                lines.append(f"| {d} | {c} |")
        else:
            lines.append("None.")
        lines.append("")
        lines.append("**Bars dated on a holiday date**")
        lines.append("")
        if r["exist_holiday_rows"]:
            lines.append("| Bar date | Close | Volume | Volume equals previous row | Note |")
            lines.append("|---|---|---|---|---|")
            for d, c, v, eq, note in r["exist_holiday_rows"]:
                lines.append(f"| {d} | {c} | {v} | {eq} | {note} |")
        else:
            lines.append("None.")
        lines.append("")
        lines.append("**Top 10 absolute % daily moves on Close**")
        lines.append("")
        lines.append("| Date | Prev Close | Close | % move |")
        lines.append("|---|---|---|---|")
        for d, p, c, pct in r["top10"]:
            lines.append(f"| {d} | {p} | {c} | {pct} |")
        lines.append("")
        roll = r["roll"]
        lines.append("**Roll candidates (tentative)**")
        lines.append("")
        lines.append(f"> {ROLL_NOTE}")
        lines.append("")
        lines.append("Expected expiries (monthly, 2021-09 .. 2026-08) and the "
                     "first trading day after each:")
        lines.append("")
        lines.append("| Expected expiry | First trading day after | Close % move | "
                     "Overnight gap (Open_t/Close_t-1 - 1) |")
        lines.append("|---|---|---|---|")
        for fa in roll["first_after"]:
            lines.append(f"| {fa['expiry']} | {fa['date']} | {fa['pct']} | "
                         f"{fa['gap']} |")
        lines.append("")
        lines.append("Top-10 moves tagged against the roll window (+/-3 trading "
                     "days of an expected expiry; tentative, not confirmed):")
        lines.append("")
        lines.append("| Date | % move | Roll window |")
        lines.append("|---|---|---|")
        for td, pct, tag in roll["top10_tagged"]:
            lines.append(f"| {td} | {pct} | {tag} |")
        lines.append("")
        lines.append("Summary (tentative):")
        lines.append("")
        lines.append("| Group | Mean absolute Close % move |")
        lines.append("|---|---|")
        lines.append(f"| First day after expiry | {roll['mean_first']:.4f} |")
        lines.append(f"| All other rows | {roll['mean_others']:.4f} |")
        lines.append("")

    lines += render_bom_usd(bom_result)
    lines.append("## USDMNT=X")
    lines.append("")
    lines.append("- Download call (`scripts/stage1_download.py`): `yf.Ticker(\"USDMNT=X\")"
                 ".history(start=\"2021-09-01\", end=\"2026-09-01\", auto_adjust=False,"
                 " actions=False, timeout=30)`, retried 3x.")
    lines.append("- Error: `YFPricesMissingError: $USDMNT=X: possibly delisted; no price "
                 "data found (1d 2021-09-01 -> 2026-09-01)` on all 3 attempts.")
    lines.append("- Yahoo offers only 1d/5d periods for this ticker (user-confirmed "
                 "2026-11-20), so no historical daily series is available; USDMNT is "
                 "excluded from Stage 1. Bank of Mongolia rates to be supplied separately.")
    lines.append("")

    return "\n".join(lines)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    results = [analyze(t) for t in TICKERS]
    bom = analyze_bom_usd()
    md = render(results, bom)
    with open(OUT_PATH, "w") as fh:
        fh.write(md)
    for r in results:
        counts = Counter(c for _, c in r["missing_cls"])
        print(
            "[check] {t}: missing={n} (to_verify={vfy}, cme={cme}, "
            "us_no_bar={us}, unexpl={ux}) on_holiday={oh} "
            "top1={top1date} {top1pct}%".format(
                t=r["ticker"],
                n=len(r["missing_cls"]),
                vfy=counts["to verify"],
                cme=counts["CME holiday (for user verification)"],
                us=counts["US holiday, no Yahoo bar (CME status to verify)"],
                ux=counts["unexplained"],
                oh=len(r["exist_holiday_rows"]),
                top1date=r["top10"][0][0],
                top1pct=r["top10"][0][3],
            )
        )
    print(f"[check] BOM_USD: rows={bom['rows']} range={bom['date_min'].date()}.."
          f"{bom['date_max'].date()} dup={bom['dup_dates']} not0800={bom['non_0800']} "
          f"min={bom['min_val']}@{bom['min_date']} max={bom['max_val']}@{bom['max_date']} "
          f"unchanged_share={bom['unchanged_share']:.3f} "
          f"longest_run={bom['longest_run']}")
    print(f"[check] wrote {OUT_REL}")


if __name__ == "__main__":
    main()
