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
    "宏观政策": ["两会", "政府工作报告", "货币政策", "财政", "PPI", "CPI", "经济", "稳汇率"],
    "资本市场": ["A股", "港股", "ETF", "股市", "IPO", "净买入", "回购", "涨停", "下跌"],
    "能源黄金": ["油价", "原油", "黄金", "燃油", "天然气", "WTI"],
    "科技AI": ["AI", "人工智能", "OpenClaw", "英伟达", "机器人", "算力", "大模型"],
    "金融监管": ["监管", "银行", "保险", "合规", "最高法", "最高检", "证券犯罪"],
    "国际局势": ["伊朗", "中东", "美国", "欧洲", "特朗普", "冲突", "北约"],
}

KEYWORD_RULES = {
    "两会": ["两会", "政府工作报告"],
    "货币政策": ["货币政策", "宽松", "利率"],
    "人民币汇率": ["汇率", "人民币"],
    "黄金": ["黄金", "金价"],
    "油价": ["油价", "原油", "WTI"],
    "AI": ["AI", "人工智能", "OpenClaw", "英伟达"],
    "银行监管": ["银行", "监管", "合规", "保险"],
    "中东冲突": ["伊朗", "中东", "冲突"],
    "港股": ["港股"],
    "A股": ["A股"],
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
        matched = False
        for topic, keywords in TOPIC_RULES.items():
            if any(k in title for k in keywords):
                counter[topic] += 1
                matched = True
        if not matched:
            counter["其他"] += 1
    return counter.most_common()


def detect_keywords(titles: list[str]) -> list[tuple[str, int]]:
    counter = Counter()
    for title in titles:
        for key, rules in KEYWORD_RULES.items():
            if any(r in title for r in rules):
                counter[key] += 1
    return counter.most_common()


def build_html(today: str, score: float, tone: str, count: int, dropped: int, topics, keywords, positive_titles, negative_titles) -> str:
    topic_html = ''.join([f'<li><strong>{t}</strong>: {c}</li>' for t, c in topics[:6]])
    keyword_html = ''.join([f'<li><strong>{k}</strong>: {c}</li>' for k, c in keywords[:8]])
    pos_html = ''.join([f'<li>{x}</li>' for x in positive_titles])
    neg_html = ''.join([f'<li>{x}</li>' for x in negative_titles])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Financial News Sentiment Monitor</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px auto; max-width: 980px; padding: 0 16px; line-height: 1.6; color: #1f2937; }}
    h1, h2 {{ color: #111827; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; margin: 16px 0; background: #fff; }}
    .muted {{ color: #6b7280; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    img {{ width: 100%; border-radius: 10px; border: 1px solid #e5e7eb; background: #fff; }}
    body {{ background: #f9fafb; }}
  </style>
</head>
<body>
  <h1>Financial News Sentiment Monitor</h1>
  <p class="muted">A lightweight daily financial news sentiment and market volatility monitoring project.</p>
  <div class="card">
    <h2>Latest Snapshot · {today}</h2>
    <ul>
      <li><strong>Daily sentiment index</strong>: {score}</li>
      <li><strong>Daily tone</strong>: {tone}</li>
      <li><strong>Cleaned news count</strong>: {count}</li>
      <li><strong>Dropped noisy items</strong>: {dropped}</li>
    </ul>
    <p><a href="./latest.md">View latest markdown report</a> · <a href="./STATUS.md">Project status</a></p>
  </div>
  <div class="grid">
    <div class="card"><h2>Topic Distribution</h2><ul>{topic_html}</ul></div>
    <div class="card"><h2>Keyword Signals</h2><ul>{keyword_html}</ul></div>
  </div>
  <div class="grid">
    <div class="card"><h2>Sentiment Label Distribution</h2><img src="./assets/label_distribution.png" alt="label distribution" /></div>
    <div class="card"><h2>Topic Distribution Chart</h2><img src="./assets/topic_distribution.png" alt="topic distribution" /></div>
  </div>
  <div class="card"><h2>Sentiment vs HS300</h2><img src="./assets/sentiment_vs_hs300.png" alt="sentiment vs hs300" /></div>
  <div class="grid">
    <div class="card"><h2>Positive Examples</h2><ul>{pos_html}</ul></div>
    <div class="card"><h2>Negative Examples</h2><ul>{neg_html}</ul></div>
  </div>
</body>
</html>
"""


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
    keyword_counts = detect_keywords(titles)
    score = sentiment['daily_sentiment_index']
    tone = classify_index(score)

    report = f"""# Daily Financial Sentiment Report - {today}\n\n## 1. Daily Sentiment Snapshot\n- Total cleaned news items: {sentiment['count']}\n- Dropped noisy items: {clean.get('dropped_count', 0)}\n- Daily sentiment index: {score}\n- Daily tone: {tone}\n- Label counts: {sentiment['label_counts']}\n\n## 2. Topic Distribution\n"""
    for topic, count in topic_counts[:6]:
        report += f"- {topic}: {count}\n"
    report += "\n## 3. Keyword Signals\n"
    for key, count in keyword_counts[:8]:
        report += f"- {key}: {count}\n"
    report += "\n## 4. Positive Headline Examples\n"
    for title in positive_titles:
        report += f"- {title}\n"
    report += "\n## 5. Negative Headline Examples\n"
    for title in negative_titles:
        report += f"- {title}\n"
    report += "\n## 6. Market Data\n"
    report += f"- HS300 latest rows: {len(market['hs300'])}\n"
    report += f"- SH Index latest rows: {len(market['sh_index'])}\n"
    report += "\n## 7. Visual Assets\n"
    report += "- label_distribution.png\n- topic_distribution.png\n- sentiment_vs_hs300.png\n"
    report += "\n## 8. Brief Comment\n"
    report += f"Today's sentiment reading is {tone}. Key topics are concentrated in {', '.join([x[0] for x in topic_counts[:3]]) if topic_counts else 'general finance news'}. This auto-generated report is based on cleaned financial headlines, hybrid sentiment scoring, market index updates, and simple visualization.\n"

    report_path = REPORTS_DIR / f"{today}.md"
    latest_path = DOCS_DIR / "latest.md"
    index_md_path = DOCS_DIR / "index.md"
    index_html_path = DOCS_DIR / "index.html"
    report_path.write_text(report, encoding="utf-8")
    latest_path.write_text(report, encoding="utf-8")
    index_md_path.write_text(
        f"# Financial News Sentiment Monitor\n\nLatest report: [Daily Report {today}](./latest.md)\n\n- Latest sentiment tone: {tone}\n- Cleaned news count: {sentiment['count']}\n- Dropped noisy items: {clean.get('dropped_count', 0)}\n- Visual assets: label distribution / topic distribution / sentiment vs HS300\n\nThis page is updated automatically.\n",
        encoding="utf-8",
    )
    index_html_path.write_text(
        build_html(today, score, tone, sentiment['count'], clean.get('dropped_count', 0), topic_counts, keyword_counts, positive_titles, negative_titles),
        encoding='utf-8'
    )
    print(f"report generated: {report_path}")
    print(f"html landing page generated: {index_html_path}")


if __name__ == "__main__":
    main()
