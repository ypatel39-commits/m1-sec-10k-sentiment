"""Streamlit dashboard for SEC 10-K Risk Factor sentiment.

Run locally:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from m1_sec_10k_sentiment.pipeline import DEFAULT_CACHE, analyze_many, tone_shift

st.set_page_config(
    page_title="SEC 10-K Sentiment Analyzer",
    page_icon="📈",
    layout="wide",
)

st.title("📈 SEC 10-K Risk Factor Sentiment Analyzer")
st.caption(
    "Loughran-McDonald financial-text sentiment scoring on Item 1A 'Risk Factors' "
    "from S&P 500 10-K filings. Built by Yash Patel for ASU W. P. Carey portfolio."
)

with st.sidebar:
    st.header("Settings")
    default_tickers = "AAPL,MSFT,GOOGL,AMZN,META,TSLA,NVDA,JPM,BAC"
    raw = st.text_area(
        "Tickers (comma-separated)",
        value=default_tickers,
        help="S&P 500 ticker symbols",
    )
    limit = st.slider("10-K filings per ticker", 1, 10, 5)
    run = st.button("Run analysis", type="primary")

if run:
    tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
    with st.spinner(f"Fetching + scoring 10-Ks for {len(tickers)} tickers..."):
        df = analyze_many(tickers, Path(DEFAULT_CACHE), limit=limit)
    if df.empty:
        st.error("No filings found. Check your ticker symbols.")
        st.stop()

    df = tone_shift(df)

    st.success(f"Analyzed {len(df)} filings across {df['ticker'].nunique()} companies.")

    tab1, tab2, tab3 = st.tabs(["Time Series", "YoY Tone Shifts", "Raw Data"])

    with tab1:
        st.subheader("Negative-sentiment ratio over time")
        fig1 = px.line(
            df, x="fy_end", y="negative_ratio",
            color="ticker", markers=True,
            labels={"fy_end": "Fiscal Year End", "negative_ratio": "Negative Word Ratio"},
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Net sentiment (positive - negative) / total tokens")
        fig2 = px.line(
            df, x="fy_end", y="net_sentiment",
            color="ticker", markers=True,
            labels={"fy_end": "Fiscal Year End", "net_sentiment": "Net Sentiment"},
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Year-over-year tone deterioration")
        st.caption(
            "Positive YoY delta = MORE negative this year than last year (deteriorating tone)."
        )
        if df["negative_yoy_delta"].notna().any():
            fig3 = px.bar(
                df.dropna(subset=["negative_yoy_delta"]),
                x="fy_end", y="negative_yoy_delta",
                color="ticker", barmode="group",
                labels={"negative_yoy_delta": "Δ Negative Ratio (YoY)"},
            )
            st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.subheader("Raw scores per filing")
        cols = ["ticker", "company", "fy_end", "tokens", "negative_count",
                "positive_count", "negative_ratio", "positive_ratio", "net_sentiment"]
        st.dataframe(df[cols].round(5), use_container_width=True)

else:
    st.info("Configure tickers in the sidebar and click 'Run analysis'.")
