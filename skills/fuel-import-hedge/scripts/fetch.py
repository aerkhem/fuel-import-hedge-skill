"""Fetch daily OHLCV data for hedge workflow tickers via yfinance.

Part A of the fuel-import-hedge skill. Downloads daily bars with
auto_adjust=False (raw, unadjusted), writes each ticker's CSV in the same
format as data/raw/*.csv, and emits fetch_meta.json plus fetch_checks.md.

--end is INCLUSIVE: yfinance receives end + 1 day (upper-exclusive API),
and that fact is recorded in the metadata so downstream consumers know the
range semantics.

Network use: yfinance downloads only. Existing files are never overwritten
unless --overwrite is passed.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

# yfinance adjustment mode: raw/unadjusted prices matching data/raw/*.csv.
ADJUST = False


def parse_args(argv=None):
    """Return parsed CLI arguments for the fetch entry point."""
    p = argparse.ArgumentParser(
        description="Fetch daily OHLCV data (auto_adjust=False) for tickers.")
    p.add_argument("--tickers", nargs="+", required=True,
                   help="Yahoo tickers, e.g. BZ=F RB=F")
    p.add_argument("--start", required=True,
                   help="Inclusive start date, YYYY-MM-DD")
    p.add_argument("--end", required=True,
                   help="Inclusive end date, YYYY-MM-DD")
    p.add_argument("--out-raw", required=True,
                   help="Output directory for CSVs, fetch_meta.json, "
                        "fetch_checks.md")
    p.add_argument("--overwrite", action="store_true",
                   help="Overwrite existing CSV files")
    return p.parse_args(argv)


def download_ticker(ticker, start, end, out_raw, overwrite):
    """Download one ticker; returns data so main() can save it.

    Returns the downloaded DataFrame and its destination path; main() writes
    the CSV untouched. Raises SystemExit with a clear, non-traceback message
    if the ticker returns no rows (e.g. a symbol Yahoo has no history for,
    like USDMNT=X).
    """
    csv_path = os.path.join(out_raw, ticker + ".csv")
    if os.path.exists(csv_path) and not overwrite:
        sys.exit("fetch.py: %s already exists; pass --overwrite to replace "
                 "it." % csv_path)

    # yfinance end is upper-exclusive; make --end inclusive by passing +1 day.
    end_excl = (pd.to_datetime(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    df = yf.Ticker(ticker).history(start=start, end=end_excl,
                                   auto_adjust=ADJUST, actions=False,
                                   timeout=30)
    if df is None or df.empty:
        sys.exit("fetch.py: no data returned for ticker %r between %s and %s. "
                 "Yahoo has no history for it (e.g. USDMNT=X). Supply another "
                 "source/ticker." % (ticker, start, end))
    return df, csv_path


def _date_set(df):
    return set(df.index.strftime("%Y-%m-%d"))


def _checks(df, start, end):
    """Return a dict of built-in quality checks for one ticker frame."""
    dates = _date_set(df)
    bdays = pd.bdate_range(start=start, end=end)
    bdays = {d.strftime("%Y-%m-%d") for d in bdays}
    price_cols = [c for c in ("Open", "High", "Low", "Close", "Adj Close")
                  if c in df.columns]
    return {
        "row_count": int(len(df)),
        "date_min": df.index.min().strftime("%Y-%m-%d"),
        "date_max": df.index.max().strftime("%Y-%m-%d"),
        "duplicate_dates": int(df.index.duplicated().sum()),
        "nonpositive_prices": int((df[price_cols] <= 0).any(axis=1).sum()),
        "zero_volume_days": int((df["Volume"] == 0).sum()),
        "missing_weekdays": len(bdays - dates),
    }


def main(argv=None):
    args = parse_args(argv)
    os.makedirs(args.out_raw, exist_ok=True)

    frames, checks, rows = {}, {}, {}
    for ticker in args.tickers:
        df, path = download_ticker(ticker, args.start, args.end,
                                   args.out_raw, args.overwrite)
        df.to_csv(path)
        frames[ticker] = df
        checks[ticker] = _checks(df, args.start, args.end)
        rows[ticker] = int(len(df))

    date_sets = {t: _date_set(df) for t, df in frames.items()}
    all_same = all(s == next(iter(date_sets.values())) for s in date_sets.values())

    meta = {
        "tickers": args.tickers,
        "start": args.start,
        "end": args.end,
        "end_is_inclusive": True,
        "adjust": "auto_adjust=False",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "yfinance": yf.__version__,
        "pandas": pd.__version__,
        "row_counts": rows,
        "files": [os.path.relpath(os.path.join(args.out_raw, t + ".csv"),
                                  args.out_raw) for t in args.tickers],
    }
    with open(os.path.join(args.out_raw, "fetch_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    lines = ["# fetch_checks", ""]
    for t in args.tickers:
        c = checks[t]
        lines += ["## %s" % t,
                  "- rows: %d, range: %s .. %s" % (c["row_count"], c["date_min"], c["date_max"]),
                  "- duplicate dates: %d" % c["duplicate_dates"],
                  "- non-positive prices: %d" % c["nonpositive_prices"],
                  "- zero-volume days: %d" % c["zero_volume_days"],
                  "- missing weekdays: %d" % c["missing_weekdays"], ""]
    lines.append("- all tickers share the same dates: %s" % all_same)
    with open(os.path.join(args.out_raw, "fetch_checks.md"), "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
