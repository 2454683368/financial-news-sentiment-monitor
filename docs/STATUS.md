# Current Status

## What is working
- Daily pipeline runs end-to-end
- News ingestion -> cleaning -> sentiment -> market data -> history update -> chart generation -> report generation works
- GitHub Pages is live
- Local auto-publish script is available

## Recommended daily usage
1. Run `python scripts/run_daily.py`
2. Check generated report and charts
3. Run `python scripts/publish_github.py`

## Why generation and publishing are still separated
- Safer for debugging
- Easier to inspect outputs before pushing
- Better for early-stage MVP iteration

## Current known issues
- Some edge-case noise may still remain
- Sentiment scoring is improved but still not perfect for finance-specific headlines
- Historical linkage is still early because sample length is short

## Next planned tasks
1. Add local scheduler / cron integration
2. Improve source quality further
3. Strengthen sentiment rules and topic tagging
4. Accumulate multi-day history for better linkage analysis
