"""Unit tests for the Loughran-McDonald sentiment scorer."""

from __future__ import annotations

from m1_sec_10k_sentiment.lexicon import (
    NEGATIVE,
    POSITIVE,
    score_sentiment,
    tokenize,
)


def test_tokenize_lowercases() -> None:
    assert tokenize("Hello World!") == ["hello", "world"]
    assert tokenize("Risk-FACTORS") == ["risk", "factors"]


def test_tokenize_drops_numbers() -> None:
    assert tokenize("revenue 1000 declined 50%") == ["revenue", "declined"]


def test_score_empty() -> None:
    s = score_sentiment("")
    assert s["tokens"] == 0
    assert s["negative_count"] == 0
    assert s["net_sentiment"] == 0.0


def test_score_positive_text() -> None:
    text = "We achieved strong growth and superior performance"
    s = score_sentiment(text)
    assert s["positive_count"] >= 3  # achieved, strong, growth, superior
    assert s["net_sentiment"] > 0


def test_score_negative_text() -> None:
    text = (
        "There is significant risk and uncertainty about adverse litigation "
        "that could result in losses, breach, and impairment"
    )
    s = score_sentiment(text)
    assert s["negative_count"] >= 5
    assert s["net_sentiment"] < 0


def test_lexicon_disjoint() -> None:
    """No word should be in both POSITIVE and NEGATIVE sets."""
    overlap = NEGATIVE & POSITIVE
    assert overlap == set(), f"Lexicon overlap: {overlap}"


def test_score_ratios_sum_correctly() -> None:
    text = "Strong growth despite material risk and adverse litigation losses"
    s = score_sentiment(text)
    expected_net = (s["positive_count"] - s["negative_count"]) / s["tokens"]
    assert abs(s["net_sentiment"] - expected_net) < 1e-9
