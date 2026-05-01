"""Loughran-McDonald financial sentiment lexicon (curated subset).

The full Loughran-McDonald master dictionary is ~80k entries; for
year-over-year *tone shift detection* a curated 200-word subset of
the most discriminative terms is sufficient and cheaper to ship.

Source: Loughran & McDonald (2011), 'When Is a Liability Not a
Liability? Textual Analysis, Dictionaries, and 10-Ks',
Journal of Finance 66(1), 35-65.

This is the canonical financial-text sentiment lexicon — used by
academic and industry researchers since 2011. Words below were
selected for high frequency in 10-K Risk Factor sections.
"""

from __future__ import annotations

# Negative-sentiment words (subset)
NEGATIVE: frozenset[str] = frozenset({
    "adverse", "adversely", "abandon", "abandoned", "abandonment",
    "breach", "breached", "breaching", "breaches",
    "claim", "claimed", "claims", "concern", "concerned", "concerns",
    "decline", "declined", "declining", "decreased", "deficiency",
    "delay", "delayed", "deny", "denied", "denying",
    "disrupt", "disrupted", "disrupting", "disruption", "disruptions",
    "doubt", "doubts", "downturn", "downturns",
    "exposure", "exposures", "fail", "failed", "failing", "fails", "failure",
    "fraud", "fraudulent", "harm", "harmed", "harmful", "harming",
    "impair", "impaired", "impairment", "impairments",
    "insufficient", "interrupt", "interrupted", "interruption",
    "litigation", "loss", "losses", "lost",
    "material", "materiality", "materially", "negative", "negatively",
    "penalty", "penalties", "problem", "problems", "regulation", "regulatory",
    "restrict", "restricted", "restriction", "restrictions",
    "risk", "risks", "risky", "shortfall", "shortfalls",
    "subject", "termination", "terminate", "terminated",
    "threat", "threats", "threatened", "threatening",
    "unable", "uncertain", "uncertainty", "uncertainties",
    "unfavorable", "unfavorably", "violation", "violations",
    "volatile", "volatility", "vulnerable", "weakness", "weaknesses",
    "weak", "worse", "worsen", "worsened",
})

# Positive-sentiment words (subset). Risk Factor sections are mostly
# negative by design, but positive terms can indicate hedging or
# offsetting language ("we believe we are well-positioned to manage").
POSITIVE: frozenset[str] = frozenset({
    "able", "achieve", "achieved", "achievement", "advantage", "advantages",
    "beneficial", "benefit", "benefits", "best",
    "confident", "confidence", "creative", "delight", "delighted",
    "effective", "effectively", "efficient", "efficiently",
    "enhance", "enhanced", "enhancement", "enhancing",
    "exceptional", "excellent", "favorable", "favorably",
    "gain", "gained", "gaining", "good", "great", "greater", "greatest",
    "growth", "improved", "improvement", "improving", "increase", "increased",
    "innovate", "innovation", "innovative", "leadership", "leading",
    "opportunity", "opportunities", "outperform", "outperformed",
    "positive", "positively", "profitable", "progress", "robust",
    "strength", "strengths", "strong", "stronger", "strongest",
    "succeed", "success", "successful", "successfully",
    "superior", "transform", "transformative", "winner", "winning",
})


def tokenize(text: str) -> list[str]:
    """Lowercase + word-tokenize. Cheap and dependency-free."""
    import re
    # Match alphabetic tokens (drop numbers, punctuation)
    return re.findall(r"[a-zA-Z]+", text.lower())


def score_sentiment(text: str) -> dict:
    """Score text via Loughran-McDonald lexicon.

    Returns:
        {
            "tokens": int,
            "negative_count": int,
            "positive_count": int,
            "negative_ratio": float,  # negatives / total tokens
            "positive_ratio": float,
            "net_sentiment": float,   # (positive - negative) / total
        }
    """
    tokens = tokenize(text)
    n_total = len(tokens)
    if n_total == 0:
        return {
            "tokens": 0,
            "negative_count": 0,
            "positive_count": 0,
            "negative_ratio": 0.0,
            "positive_ratio": 0.0,
            "net_sentiment": 0.0,
        }
    neg = sum(1 for t in tokens if t in NEGATIVE)
    pos = sum(1 for t in tokens if t in POSITIVE)
    return {
        "tokens": n_total,
        "negative_count": neg,
        "positive_count": pos,
        "negative_ratio": neg / n_total,
        "positive_ratio": pos / n_total,
        "net_sentiment": (pos - neg) / n_total,
    }
