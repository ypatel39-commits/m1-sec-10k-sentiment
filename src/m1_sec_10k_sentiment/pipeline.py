"""End-to-end pipeline: ticker -> 10-K filings -> Risk Factors -> sentiment scores.

Produces a tidy DataFrame suitable for time-series analysis or
plotting in the Streamlit dashboard.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pandas as pd

from .edgar import Filing, fetch_filing_text, list_10k_filings
from .extract import extract_from_path
from .lexicon import score_sentiment

log = logging.getLogger(__name__)

DEFAULT_CACHE = Path.home() / ".sec10k-cache"


def analyze_ticker(
    ticker: str,
    cache_dir: Path = DEFAULT_CACHE,
    *,
    limit: int = 5,
) -> pd.DataFrame:
    """Full pipeline for one ticker: returns DataFrame of yearly sentiment."""
    filings = list_10k_filings(ticker, limit=limit)
    rows: list[dict] = []
    for f in filings:
        try:
            html_path = fetch_filing_text(f, cache_dir)
            risk_text = extract_from_path(html_path)
            scores = score_sentiment(risk_text)
            rows.append(
                {
                    "ticker": f.ticker,
                    "company": f.company_name,
                    "fy_end": f.fy_end,
                    "filed_date": f.filed_date,
                    "accession": f.accession,
                    "risk_section_chars": len(risk_text),
                    **scores,
                }
            )
        except Exception as e:
            log.warning("failed %s %s: %s", f.ticker, f.fy_end, e)
    df = pd.DataFrame(rows)
    if not df.empty:
        df["fy_end"] = pd.to_datetime(df["fy_end"])
        df = df.sort_values("fy_end").reset_index(drop=True)
    return df


def analyze_many(
    tickers: Iterable[str],
    cache_dir: Path = DEFAULT_CACHE,
    *,
    limit: int = 5,
) -> pd.DataFrame:
    """Pipeline across many tickers; results concatenated."""
    frames = []
    for t in tickers:
        try:
            df = analyze_ticker(t, cache_dir, limit=limit)
            if not df.empty:
                frames.append(df)
        except Exception as e:
            log.warning("ticker %s skipped: %s", t, e)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def tone_shift(df: pd.DataFrame) -> pd.DataFrame:
    """Compute year-over-year tone shift per ticker.

    Adds columns: ``negative_yoy_delta``, ``net_sentiment_yoy_delta``.
    """
    if df.empty:
        return df
    df = df.sort_values(["ticker", "fy_end"]).copy()
    df["negative_yoy_delta"] = df.groupby("ticker")["negative_ratio"].diff()
    df["net_sentiment_yoy_delta"] = df.groupby("ticker")["net_sentiment"].diff()
    return df
