# Current Status

## What is working
- Daily pipeline runs end-to-end
- News ingestion -> cleaning -> sentiment -> market data -> report generation works
- Results are pushed to GitHub

## Current known issues
- Some non-news informational pages are still mixed into the dataset
- Sentiment scoring is improved but still not perfect for finance-specific headlines
- Topic extraction is currently rule-based and still simple

## Next planned tasks
1. Further tighten source filtering
2. Add stronger topic labeling and keyword extraction
3. Improve GitHub Pages presentation
4. Add automated publish step
