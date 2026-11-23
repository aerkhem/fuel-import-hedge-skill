#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stage 1 (download): fetch daily data for BZ=F, HO=F, RB=F, USDMNT=X
from Yahoo Finance via yfinance.

Scope: data assembly only. No modelling, no invoice conversion.
Boundaries honoured: network used only for these yfinance downloads;
no installs/upgrades; README.md, assumptions.md, requirements.txt untouched.

Behaviour:
- Downloads daily bars 2021-09-01 .. 2026-08-31 (yfinance end date is
  exclusive, so end="2026-09-01" is passed).
- auto_adjust=False is set explicitly.
- Each raw download is saved untouched to data/raw/{ticker}.csv.
- Metadata (tickers, dates, adjustment settings, yfinance version,
  retrieval time, index timezone, expiry-info probe) is saved to
  data/raw/_download_meta.json.
- If a download fails or a required column/value is missing, the script
  stops with a clear message (no guessing, no filling).
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yfinance as yf

# Deterministic exception behaviour: let history() raise on missing data
# (yfinance 1.8.0: raise_errors kwarg is deprecated in favour of this config).
yf.config.debug.hide_exceptions = False

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(REPO, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

TICKERS = ["BZ=F", "HO=F", "RB=F", "USDMNT=X"]
START = "2021-09-01"
END = "2026-09-01"          # yfinance end date is exclusive -> last bar 2026-08-31
AUTO_ADJUST = False
MAX_ATTEMPTS = 3
RETRY_WAIT_S = 10

REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

meta = {
    "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "yfinance_version": yf.__version__,
    "pandas_version": pd.__version__,
    "numpy_version": np.__version__,
    "start": START,
    "end": END,
    "auto_adjust": AUTO_ADJUST,
    "note_end_exclusive": "yfinance end date is exclusive; end=2026-09-01 requested",
    "tickers": {},
}

failures = []

for ticker in TICKERS:
    print(f"[download] {ticker} ...", flush=True)
    attempts = []
    df = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            tk = yf.Ticker(ticker)
            df = tk.history(
                start=START,
                end=END,
                auto_adjust=AUTO_ADJUST,
                actions=False,
                timeout=30,
            )
            n = 0 if df is None else len(df)
            attempts.append(f"attempt {attempt}: ok, rows={n}")
            if df is not None and not df.empty:
                break
        except Exception as exc:  # noqa: BLE001 - we want to capture and report
            attempts.append(f"attempt {attempt}: {type(exc).__name__}: {exc}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_WAIT_S)

    if df is None or df.empty:
        failures.append(ticker)
        meta["tickers"][ticker] = {
            "status": "FAILED",
            "error": attempts,
            "saved_as": None,
        }
        print(f"[download] {ticker}: FAILED after {MAX_ATTEMPTS} attempts", flush=True)
        for a in attempts:
            print("  " + a, flush=True)
        continue

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        failures.append(ticker)
        meta["tickers"][ticker] = {
            "status": "FAILED",
            "error": f"missing columns: {missing}",
            "saved_as": None,
        }
        print(f"[download] {ticker}: FAILED, missing columns {missing}", flush=True)
        continue

    out_path = os.path.join(RAW_DIR, f"{ticker}.csv")
    df.to_csv(out_path)  # untouched download, index written as returned by yfinance

    # Probe: what expiry information does yfinance actually return for this
    # ticker? We record presence/absence only; we never use it as a historical
    # expiry schedule for 2021-2026 (yfinance does not provide one).
    hist_meta = {"attempts": attempts}
    try:
        hm = tk.get_history_metadata()
        hist_meta["metadata_keys_total"] = len(hm)
        expiry_keys = sorted(
            k for k in hm.keys() if "xpir" in k.lower() or "expiration" in k.lower()
        )
        hist_meta["expiry_related_keys"] = expiry_keys
        hist_meta["expiry_related_values"] = {
            k: str(hm[k]) for k in expiry_keys
        }
    except Exception as exc:  # noqa: BLE001
        hist_meta["metadata_error"] = f"{type(exc).__name__}: {exc}"
    try:
        opts = tk.options
        hist_meta["options_expirations"] = list(opts) if opts else []
    except Exception as exc:  # noqa: BLE001
        hist_meta["options_error"] = f"{type(exc).__name__}: {exc}"

    meta["tickers"][ticker] = {
        "status": "OK",
        "rows": int(len(df)),
        "columns": list(df.columns),
        "index_tz": str(df.index.tz),
        "index_min": str(df.index.min()),
        "index_max": str(df.index.max()),
        "history_metadata_probe": hist_meta,
        "saved_as": out_path,
    }
    print(f"  rows={len(df)}, tz={df.index.tz}, saved={out_path}", flush=True)

meta_path = os.path.join(RAW_DIR, "_download_meta.json")
with open(meta_path, "w") as fh:
    json.dump(meta, fh, indent=2, default=str)
print("[download] meta -> " + meta_path)
if failures:
    print(f"[download] FAILED tickers: {failures}", flush=True)
    print("[download] stopping: a required download is missing; not proceeding.", flush=True)
    sys.exit(1)
print("[download] done")
