"""Test the Risk Factors regex extractor."""

from __future__ import annotations

from m1_sec_10k_sentiment.extract import extract_risk_factors


def test_extract_finds_section() -> None:
    text = (
        "ITEM 1. BUSINESS We sell widgets. "
        "ITEM 1A. RISK FACTORS We face significant competition and operational risk. "
        "ITEM 1B. UNRESOLVED STAFF COMMENTS None."
    )
    out = extract_risk_factors(text)
    assert "competition" in out.lower()
    assert "operational risk" in out.lower()
    # Should NOT include the next section
    assert "unresolved staff comments" not in out.lower()


def test_extract_handles_item_2_terminator() -> None:
    """Some 10-Ks omit Item 1B; section then ends at Item 2."""
    text = (
        "Item 1A. Risk Factors The market is volatile and uncertain. "
        "Item 2. Properties Our HQ is in Tempe, AZ."
    )
    out = extract_risk_factors(text)
    assert "volatile" in out.lower()
    assert "properties" not in out.lower()


def test_extract_returns_empty_when_no_section() -> None:
    text = "Item 1. Business overview only. Item 7. MD&A."
    assert extract_risk_factors(text) == ""


def test_extract_case_insensitive() -> None:
    text = "ITEM 1a. risk FACTORS many risks here. item 2. other."
    out = extract_risk_factors(text)
    assert "many risks here" in out.lower()
