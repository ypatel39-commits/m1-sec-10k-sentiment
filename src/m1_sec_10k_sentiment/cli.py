"""CLI: analyze 10-K sentiment for one or more tickers."""

from __future__ import annotations

import logging
from pathlib import Path

import click
import pandas as pd

from .pipeline import DEFAULT_CACHE, analyze_many, tone_shift


@click.command()
@click.option("-t", "--ticker", "tickers", multiple=True, required=True,
              help="One or more ticker symbols (-t AAPL -t MSFT)")
@click.option("--limit", default=5, show_default=True,
              help="Number of recent 10-K filings per ticker")
@click.option("--cache", default=str(DEFAULT_CACHE), show_default=True,
              help="Where to cache filings on disk")
@click.option("--output", default=None, help="Write result CSV (default: stdout)")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging")
def main(tickers, limit, cache, output, verbose):
    """Run the full SEC 10-K sentiment pipeline."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    df = analyze_many(tickers, Path(cache), limit=limit)
    if df.empty:
        click.echo("No filings found.", err=True)
        return

    df = tone_shift(df)

    cols = ["ticker", "fy_end", "tokens", "negative_ratio",
            "net_sentiment", "negative_yoy_delta", "net_sentiment_yoy_delta"]
    numeric_cols = ["negative_ratio", "net_sentiment",
                    "negative_yoy_delta", "net_sentiment_yoy_delta"]
    show = df[cols].copy()
    show[numeric_cols] = show[numeric_cols].round(5)

    if output:
        df.to_csv(output, index=False)
        click.echo(f"Wrote {len(df)} rows to {output}", err=True)
    else:
        with pd.option_context("display.max_rows", None):
            click.echo(show.to_string(index=False))


if __name__ == "__main__":
    main()
