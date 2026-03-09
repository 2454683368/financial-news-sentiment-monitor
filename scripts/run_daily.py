from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)


def run(script_name: str) -> None:
    script_path = BASE_DIR / 'scripts' / script_name
    print(f'Running {script_name} ...')
    subprocess.run(['python', str(script_path)], check=True)


def run_publish() -> None:
    print('Running publish_github.py ...')
    subprocess.run(['python', str(BASE_DIR / 'scripts' / 'publish_github.py')], check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the daily financial sentiment pipeline.')
    parser.add_argument('--publish', action='store_true', help='Publish generated outputs to GitHub after the pipeline succeeds.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_at = datetime.now()
    print(f"Daily pipeline started at {started_at.isoformat(timespec='seconds')}")
    for script in [
        'ingest_news.py',
        'clean_news.py',
        'sentiment_analysis.py',
        'fetch_market_data.py',
        'update_history.py',
        'build_charts.py',
        'build_report.py',
    ]:
        run(script)
    if args.publish:
        run_publish()
    finished_at = datetime.now()
    print(f"Daily pipeline completed at {finished_at.isoformat(timespec='seconds')}")
    print(f"Elapsed: {finished_at - started_at}")
    if not args.publish:
        print('Tip: run python scripts/run_daily.py --publish to generate and push in one step.')


if __name__ == '__main__':
    main()
