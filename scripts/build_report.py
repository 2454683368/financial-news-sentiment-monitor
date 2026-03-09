from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    sentiment_path = PROC_DIR / f"sentiment_{today}.json"
    market_path = PROC_DIR / f"market_{today}.json"
    sentiment = json.loads(sentiment_path.read_text(encoding="utf-8"))
    market = json.loads(market_path.read_text(encoding="utf-8"))

    top_titles = [x["title"] for x in sentiment["items"][:10]]
    words = Counter()
    for t in top_titles:
        for token in [w for w in t.replace('，', ' ').replace('：', ' ').split() if len(w) >= 2]:
            words[token] += 1
    top_words = words.most_common(10)

    report = f"""# Daily Financial Sentiment Report - {today}\n\n## 1. Daily Sentiment Snapshot\n- Total news items: {sentiment['count']}\n- Daily sentiment index: {sentiment['daily_sentiment_index']}\n- Label counts: {sentiment['label_counts']}\n\n## 2. Headline Highlights\n"""
    for title in top_titles[:5]:
        report += f"- {title}\n"
    report += "\n## 3. Keyword Glimpse\n"
    for k, v in top_words[:8]:
        report += f"- {k}: {v}\n"
    report += "\n## 4. Market Data\n"
    report += f"- HS300 latest rows: {len(market['hs300'])}\n"
    report += f"- SH Index latest rows: {len(market['sh_index'])}\n"
    report += "\n## 5. Brief Comment\n"
    report += "This report is generated automatically based on daily financial news headlines, sentiment scoring, and market index updates.\n"

    report_path = REPORTS_DIR / f"{today}.md"
    latest_path = DOCS_DIR / "latest.md"
    index_path = DOCS_DIR / "index.md"
    report_path.write_text(report, encoding="utf-8")
    latest_path.write_text(report, encoding="utf-8")
    index_path.write_text(f"# Financial News Sentiment Monitor\n\nLatest report: [Daily Report {today}](./latest.md)\n", encoding="utf-8")
    print(f"report generated: {report_path}")


if __name__ == "__main__":
    main()
