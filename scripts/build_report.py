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

TOPIC_RULES = {
    "宏观政策": ["两会", "政府工作报告", "货币政策", "财政", "PPI", "CPI", "经济"],
    "资本市场": ["A股", "港股", "ETF", "股市", "IPO", "净买入", "回购"],
    "能源黄金": ["油价", "原油", "黄金", "燃油", "天然气"],
    "科技AI": ["AI", "人工智能", "OpenClaw", "英伟达", "机器人"],
    "金融监管": ["监管", "银行", "保险", "合规", "最高法", "最高检"],
    "国际局势": ["伊朗", "中东", "美国", "欧洲", "特朗普", "冲突"],
}


def classify_index(score: float) -> str:
    if score > 0.12:
        return "偏乐观"
    if score < -0.12:
        return "偏谨慎"
    return "中性偏平衡"


def detect_topics(titles: list[str]) -> list[tuple[str, int]]:
    counter = Counter()
    for title in titles:
        for topic, keywords in TOPIC_RULES.items():
            if any(k in title for k in keywords):
                counter[topic] += 1
    return counter.most_common()


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    sentiment_path = PROC_DIR / f"sentiment_{today}.json"
    market_path = PROC_DIR / f"market_{today}.json"
    clean_path = PROC_DIR / f"news_clean_{today}.json"
    sentiment = json.loads(sentiment_path.read_text(encoding="utf-8"))
    market = json.loads(market_path.read_text(encoding="utf-8"))
    clean = json.loads(clean_path.read_text(encoding="utf-8"))

    titles = [x["title"] for x in sentiment["items"]]
    negative_titles = [x["title"] for x in sentiment["items"] if x["sentiment_label"] == "negative"][:5]
    positive_titles = [x["title"] for x in sentiment["items"] if x["sentiment_label"] == "positive"][:5]
    topic_counts = detect_topics(titles)
    score = sentiment['daily_sentiment_index']
    tone = classify_index(score)

    report = f"""# Daily Financial Sentiment Report - {today}\n\n## 1. Daily Sentiment Snapshot\n- Total cleaned news items: {sentiment['count']}\n- Dropped noisy items: {clean.get('dropped_count', 0)}\n- Daily sentiment index: {score}\n- Daily tone: {tone}\n- Label counts: {sentiment['label_counts']}\n\n## 2. Topic Distribution\n"""
    for topic, count in topic_counts[:6]:
        report += f"- {topic}: {count}\n"
    report += "\n## 3. Positive Headline Examples\n"
    for title in positive_titles:
        report += f"- {title}\n"
    report += "\n## 4. Negative Headline Examples\n"
    for title in negative_titles:
        report += f"- {title}\n"
    report += "\n## 5. Market Data\n"
    report += f"- HS300 latest rows: {len(market['hs300'])}\n"
    report += f"- SH Index latest rows: {len(market['sh_index'])}\n"
    report += "\n## 6. Brief Comment\n"
    report += f"Today's sentiment reading is {tone}. Key topics are concentrated in {', '.join([x[0] for x in topic_counts[:3]]) if topic_counts else 'general finance news'}. This auto-generated report is based on cleaned financial headlines, hybrid sentiment scoring, and market index updates.\n"

    report_path = REPORTS_DIR / f"{today}.md"
    latest_path = DOCS_DIR / "latest.md"
    index_path = DOCS_DIR / "index.md"
    report_path.write_text(report, encoding="utf-8")
    latest_path.write_text(report, encoding="utf-8")
    index_path.write_text(
        f"# Financial News Sentiment Monitor\n\nLatest report: [Daily Report {today}](./latest.md)\n\n- Latest sentiment tone: {tone}\n- Cleaned news count: {sentiment['count']}\n- Dropped noisy items: {clean.get('dropped_count', 0)}\n\nThis page is updated automatically.\n",
        encoding="utf-8",
    )
    print(f"report generated: {report_path}")


if __name__ == "__main__":
    main()
