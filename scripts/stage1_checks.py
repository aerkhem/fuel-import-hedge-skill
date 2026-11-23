#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stage 1 (checks, part B): basic integrity + missing weekdays for
BZ=F, HO=F, RB=F. Writes outputs/stage1_checks.md.

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

# CME (NYMEX energy) holiday dates within the data window.
# Hard-coded, exact; the whole list is labelled "for user verification".
JUNETEENTH = {
    "2022-06-20", "2023-06-19", "2024-06-19", "2025-06-19", "2026-06-19",
}
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
    # Special (national day of mourning)
    "2025-01-09",
}

HOLIDAY_DATES = {pd.Timestamp(s).normalize() for s in CME_HOLIDAYS}


def classify_missing(date_str):
    if date_str == "2025-01-09" or date_str in JUNETEENTH:
        return "to verify"
    if date_str in CME_HOLIDAYS:
        return "CME holiday (for user verification)"
    return "unexplained"


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

    # Rows that EXIST on a date in the holiday list (incl. 2025-01-09).
    exist_mask = df["date"].isin(HOLIDAY_DATES)
    exist_holiday = df.loc[exist_mask, ["date", "Close"]]
    exist_holiday_rows = [
        (r.date.strftime("%Y-%m-%d"), float(r.Close))
        for r in exist_holiday.itertuples(index=False)
    ]

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
    }


def render(results):
    lines = []
    lines.append("# Stage 1 checks (part B) - integrity + missing weekdays")
    lines.append("")
    lines.append(f"- Script: `scripts/stage1_checks.py`")
    lines.append("- Input: `data/raw/{BZ=F,HO=F,RB=F}.csv` (untouched)")
    lines.append(f"- Output: `{OUT_REL}`")
    lines.append("")
    lines.append(f"> {CLOSE_NOTE}")
    lines.append("")
    lines.append("## CME holiday list used (for user verification)")
    lines.append("")
    lines.append("Legend:")
    lines.append("- `to verify`: 2025-01-09 (national day of mourning) and Juneteenth dates")
    lines.append("- `CME holiday (for user verification)`: all other dates in the list")
    lines.append("- `unexplained`: any other missing weekday")
    lines.append("")
    for d in sorted(CME_HOLIDAYS):
        tag = "to verify" if (d == "2025-01-09" or d in JUNETEENTH) else "CME holiday"
        lines.append(f"- {d} ({tag})")
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
        lines.append("**Bars dated on a CME holiday date**")
        lines.append("")
        if r["exist_holiday_rows"]:
            lines.append("| Bar date | Close |")
            lines.append("|---|---|")
            for d, c in r["exist_holiday_rows"]:
                lines.append(f"| {d} | {c} |")
        else:
            lines.append("None.")
        lines.append("")

    return "\n".join(lines)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    results = [analyze(t) for t in TICKERS]
    md = render(results)
    with open(OUT_PATH, "w") as fh:
        fh.write(md)
    for r in results:
        counts = Counter(c for _, c in r["missing_cls"])
        print(
            "[check] {t}: missing={n} (to_verify={vfy}, cme={cme}, "
            "unexpl={ux}) on_holiday={oh} zero_vol={zv}".format(
                t=r["ticker"],
                n=len(r["missing_cls"]),
                vfy=counts["to verify"],
                cme=counts["CME holiday (for user verification)"],
                ux=counts["unexplained"],
                oh=len(r["exist_holiday_rows"]),
                zv=r["zero_vol"],
            )
        )
    print(f"[check] wrote {OUT_REL}")


if __name__ == "__main__":
    main()
