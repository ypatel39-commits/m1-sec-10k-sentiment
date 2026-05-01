"""Extract Item 1A 'Risk Factors' sections from 10-K HTML.

10-K filings are typically a single very long HTML document. The
Risk Factors section starts at ``Item 1A.`` and ends at ``Item 1B.``
(or ``Item 2.`` if 1B is omitted).

This regex-based extractor errs toward including too much rather
than too little; downstream sentiment scoring is tolerant of noise.
"""

from __future__ import annotations

import logging
import re
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

log = logging.getLogger(__name__)

# Matches "Item 1A" then captures everything up to "Item 1B" or "Item 2"
# Case-insensitive, dot-all to span newlines, non-greedy.
ITEM_1A_RE = re.compile(
    r"item\s*1a[\.:\s]*risk\s*factors(.*?)(?=item\s*1b|item\s*2)",
    re.IGNORECASE | re.DOTALL,
)


def html_to_text(path: Path) -> str:
    """Strip HTML tags from a 10-K, normalize whitespace."""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "lxml")
    # Remove script / style / table-of-contents anchors
    for el in soup(["script", "style"]):
        el.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_risk_factors(text: str) -> str:
    """Pull out the Risk Factors section. Empty string if not found.

    10-K filings repeat 'Item 1A. Risk Factors' twice — once in the
    table of contents, once as the actual section header. The TOC
    occurrence captures little or no text; the real section captures
    multiple kilobytes. Strategy: find ALL matches, return the longest.
    """
    matches = list(ITEM_1A_RE.finditer(text))
    if not matches:
        return ""
    # Pick the match with the largest captured group (the real section)
    best = max(matches, key=lambda m: len(m.group(1)))
    section = best.group(1).strip()
    section = re.sub(r"\s+", " ", section)
    return section


def extract_from_path(html_path: Path) -> str:
    """Convenience: HTML file -> Risk Factors text."""
    return extract_risk_factors(html_to_text(html_path))
