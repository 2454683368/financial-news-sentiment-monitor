# Financial News Sentiment Monitor

A lightweight daily financial news sentiment and market volatility monitoring project.

## What this project does
- Collects financial news headlines daily
- Cleans and filters noisy, low-value, and duplicate items
- Builds a hybrid sentiment score for the daily news set
- Fetches market index data such as HS300 and SH Index
- Generates charts, a daily report, and a GitHub Pages landing page
- Supports local auto-publish to GitHub

## Core methodology
1. **Data ingestion**: collect headlines from a small set of relatively stable public sources
2. **Cleaning**: remove noise such as roadshows, institutional homepages, event pages, and duplicate titles
3. **Sentiment scoring**: combine SnowNLP model output with finance-specific positive/negative keyword rules
4. **Market linkage**: compare daily sentiment reading with HS300 / SH Index daily returns
5. **History accumulation**: store daily snapshots for future multi-day trend and linkage analysis

## Daily usage
```bash
source .venv/bin/activate
python scripts/run_daily.py
python scripts/publish_github.py
```

## Current project stage
This project is in the MVP-but-serious stage:
- the end-to-end daily pipeline already runs
- GitHub Pages is live
- visual charts are available
- historical data accumulation has started
- source quality and sentiment robustness are still being improved

## Repository structure
- `scripts/`: runnable daily pipeline scripts
- `data/`: raw and processed data files
- `reports/`: generated daily markdown reports
- `docs/`: GitHub Pages site content
- `docs/assets/`: chart images and historical snapshot files
- `config/`: source and settings configuration

## Why this project matters
This is not intended to be a heavy production crawler. The goal is to build a stable, explainable, and continuously updating financial-tech project that can be shown on GitHub and discussed clearly in interviews.

## Status
See `docs/STATUS.md` for the latest working status and next steps.
