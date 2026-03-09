# Current Status

## What is working
- Daily pipeline runs end-to-end
- News ingestion -> cleaning -> sentiment -> market data -> history update -> chart generation -> report generation works
- GitHub Pages is live
- Local auto-publish script is available
- OpenClaw daily scheduled execution has been configured (08:00 Asia/Shanghai)

## Recommended daily usage
1. Run `python scripts/run_daily.py --publish`
2. Or use `./scripts/run_daily_job.sh` for a one-shot scheduled entry
3. Check `logs/` when you need to debug failures

## Current automation design
- Generation and publishing can now run in one step
- A dedicated shell entry is available for scheduled execution
- Logs are kept locally for easier troubleshooting
- You can still run generation only when debugging specific pipeline stages

## Current known issues
- Some edge-case noise may still remain
- Sentiment scoring is improved but still not perfect for finance-specific headlines
- Historical linkage is still early because sample length is short

## Next planned tasks
1. Add local scheduler / cron integration
2. Improve source quality further
3. Strengthen sentiment rules and topic tagging
4. Accumulate multi-day history for better linkage analysis
