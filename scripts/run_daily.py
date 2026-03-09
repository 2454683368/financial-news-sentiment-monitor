from __future__ import annotations

import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def run(script_name: str) -> None:
    script_path = BASE_DIR / 'scripts' / script_name
    print(f'Running {script_name} ...')
    subprocess.run(['python', str(script_path)], check=True)


def main() -> None:
    for script in [
        'ingest_news.py',
        'clean_news.py',
        'sentiment_analysis.py',
        'fetch_market_data.py',
        'update_history.py',
        'build_report.py',
    ]:
        run(script)
    print('Daily pipeline completed.')


if __name__ == '__main__':
    main()
