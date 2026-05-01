# Deploy Guide — M1 SEC 10-K Sentiment Analyzer

Deploy this Streamlit dashboard to **Streamlit Community Cloud** (free tier) in
~5–10 minutes. The hosted app fetches 10-K filings from SEC EDGAR live and
scores them with the Loughran-McDonald financial lexicon.

---

## 1. Prerequisites

- GitHub account with this repo pushed to `main` (already true).
- Streamlit Community Cloud account: <https://share.streamlit.io/>
  - Sign in with the same GitHub account so Streamlit can read this repo.

## 2. Quick Deploy (5 minutes)

1. Go to <https://share.streamlit.io/> and click **New app**.
2. Select repository: `ypatel39-commits/m1-sec-10k-sentiment`.
3. Branch: `main`.
4. Main file path: `app.py`.
5. *(Optional)* Custom URL slug, e.g. `yash-sec-10k-sentiment`.
6. Click **Deploy**. First build takes ~3–5 minutes (installing
   pandas, lxml, plotly, streamlit, etc.).
7. Once it boots, the sidebar lets users paste tickers and click
   **Run analysis**. The app pulls 10-Ks live from SEC EDGAR.

## 3. Files Streamlit Cloud reads

| File                         | Why                                                           |
| ---------------------------- | ------------------------------------------------------------- |
| `requirements.txt`           | Pip install list. Streamlit Cloud does **not** read           |
|                              | `pyproject.toml`, so this mirrors the deps and adds `-e .`    |
|                              | to install the `src/m1_sec_10k_sentiment` package itself.     |
| `.streamlit/config.toml`     | Theme (ASU maroon), server flags, telemetry off.              |
| `app.py`                     | Entrypoint — already in repo root.                            |

## 4. Environment variables

**None required.** The app calls SEC EDGAR which is public + free.

If you want to set a polite SEC `User-Agent` (recommended by SEC, but the
codebase already sets one inside `pipeline.py`), no env var is needed.

If you later add API keys (e.g. for an enriched data source), set them in
**App settings → Secrets** — Streamlit exposes them via `st.secrets["KEY"]`.

## 5. Free-tier limits + expected resource usage

Streamlit Community Cloud free tier (as of 2026):

| Resource          | Limit                                       | This app's usage                |
| ----------------- | ------------------------------------------- | ------------------------------- |
| RAM               | ~1 GB per app                               | ~200–400 MB (pandas + plotly)   |
| CPU               | Shared, ~1 vCPU                             | Spike during 10-K fetch+parse   |
| Storage           | Ephemeral, cleared on reboot                | Cache dir under `data/cache/`,  |
|                   |                                             | rebuilt on demand.              |
| Apps per account  | Unlimited (3 public, more on request)       | 1                               |
| Sleep             | Idle apps sleep after ~7 days of no traffic | Wakes on visit (~30s cold start)|
| Bandwidth         | Fair use                                    | Light — text + small plots      |

**Watchouts:**
- First click on **Run analysis** with 10 tickers × 10 filings ≈ 100 SEC requests
  at ~150 ms apart = ~15 s wall time. Stay under the SEC rate limit.
- Filesystem is **ephemeral**. The local `data/cache/` directory will rebuild
  every cold start. That's fine; just slower for the first user after a sleep.

## 6. Troubleshooting

- **`ModuleNotFoundError: m1_sec_10k_sentiment`** → confirm `-e .` is the last
  line of `requirements.txt`. That's what installs the `src/` package.
- **Build fails on `lxml`** → Streamlit Cloud images ship build tools; usually
  resolves by retrying. If not, pin `lxml==5.2.2`.
- **App stuck at "Please wait..."** → check the **Manage app → Logs** panel.
  Most common cause: SEC EDGAR returning 429 (rate limited). Lower the
  ticker count or filings-per-ticker slider.

## 7. Updating the deployed app

Push to `main`. Streamlit Cloud auto-redeploys within ~1 minute.

```bash
git add .
git commit -m "tweak: ..."
git push origin main
```

---

Author: Yash Patel · ASU W. P. Carey portfolio · Project M1.
