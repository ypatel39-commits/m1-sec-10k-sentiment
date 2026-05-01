"""SEC EDGAR full-text 10-K fetcher.

EDGAR is free and requires only a polite User-Agent header that
identifies the requester (per SEC guidance). No API key needed.

Reference: https://www.sec.gov/os/accessing-edgar-data
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests

log = logging.getLogger(__name__)

USER_AGENT = "Yash Patel Finance Portfolio yashpatel06050@gmail.com"
TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:0>10}.json"
FILING_BASE = "https://www.sec.gov/Archives/edgar/data"

REQUEST_DELAY = 0.15  # seconds between requests (SEC asks for <10 req/sec)


@dataclass(frozen=True, slots=True)
class Filing:
    """One 10-K filing."""

    ticker: str
    cik: str
    company_name: str
    accession: str
    filed_date: str
    primary_doc: str        # URL to the .htm filing
    fy_end: str             # period of report (YYYY-MM-DD)


_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def _polite_get(url: str) -> requests.Response:
    """Rate-limited GET with the SEC-required User-Agent."""
    time.sleep(REQUEST_DELAY)
    resp = _session.get(url, timeout=30)
    resp.raise_for_status()
    return resp


def ticker_to_cik(ticker: str) -> str:
    """Resolve a ticker symbol to its 10-digit zero-padded CIK."""
    resp = _polite_get(TICKER_CIK_URL)
    mapping = resp.json()
    ticker_upper = ticker.upper()
    for entry in mapping.values():
        if entry.get("ticker", "").upper() == ticker_upper:
            return f"{entry['cik_str']:0>10}"
    raise ValueError(f"ticker not found in EDGAR: {ticker}")


def list_10k_filings(ticker: str, *, limit: int = 5) -> list[Filing]:
    """List the most recent ``limit`` 10-K filings for a ticker."""
    cik = ticker_to_cik(ticker)
    url = SUBMISSIONS_URL.format(cik=cik)
    resp = _polite_get(url)
    sub = resp.json()
    name = sub.get("name", ticker)

    recent = sub.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    filed_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])

    filings: list[Filing] = []
    for form, acc, doc, filed, report in zip(
        forms, accessions, primary_docs, filed_dates, report_dates
    ):
        if form != "10-K":
            continue
        acc_clean = acc.replace("-", "")
        url = f"{FILING_BASE}/{int(cik)}/{acc_clean}/{doc}"
        filings.append(
            Filing(
                ticker=ticker.upper(),
                cik=cik,
                company_name=name,
                accession=acc,
                filed_date=filed,
                primary_doc=url,
                fy_end=report,
            )
        )
        if len(filings) >= limit:
            break
    log.info("Found %d 10-K filings for %s", len(filings), ticker)
    return filings


def fetch_filing_text(filing: Filing, cache_dir: Path) -> Path:
    """Download a 10-K filing's primary document, caching to disk."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{filing.ticker}_{filing.fy_end}_{filing.accession}.html"
    dest = cache_dir / fname
    if dest.exists() and dest.stat().st_size > 1000:
        log.debug("cache hit %s", dest.name)
        return dest

    log.info("Fetching %s", filing.primary_doc)
    resp = _polite_get(filing.primary_doc)
    dest.write_bytes(resp.content)
    return dest


def fetch_many(tickers: Iterable[str], cache_dir: Path, *, limit: int = 5) -> list[Filing]:
    """Convenience: list + fetch in one call. Returns Filing objects whose primary_doc has been cached."""
    out: list[Filing] = []
    for t in tickers:
        try:
            for f in list_10k_filings(t, limit=limit):
                fetch_filing_text(f, cache_dir)
                out.append(f)
        except Exception as e:
            log.warning("skipping %s: %s", t, e)
    return out
