from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"
ASSETS_DIR = DOCS_DIR / "assets"
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


def calc_return(series: list[dict]) -> float:
    if len(series) < 2:
        return 0.0
    prev_close = float(series[-2]["close"])
    latest_close = float(series[-1]["close"])
    return round((latest_close / prev_close - 1) * 100, 2)


def market_linkage_comment(score: float, hs300_ret: float, sh_ret: float, history_len: int) -> str:
    tone = classify_index(score)
    suffix = "当前历史样本较短，后续需继续积累。" if history_len < 5 else "当前已具备基础连续样本，可继续观察趋势稳定性。"
    if score > 0 and hs300_ret > 0:
        return f"当日新闻情绪为{tone}，沪深300与上证指数分别上涨 {hs300_ret}% / {sh_ret}%，情绪与市场方向大体一致。{suffix}"
    if score < 0 and hs300_ret < 0:
        return f"当日新闻情绪为{tone}，沪深300与上证指数分别下跌 {abs(hs300_ret)}% / {abs(sh_ret)}%，情绪与市场方向大体一致。{suffix}"
    return f"当日新闻情绪为{tone}，但沪深300 / 上证指数涨跌幅分别为 {hs300_ret}% / {sh_ret}%，说明新闻情绪与市场表现存在一定背离。{suffix}"


def build_html(today: str, score: float, tone: str, count: int, dropped: int, topics, keywords, positive_titles, negative_titles, linkage_text: str, hs300_ret: float, sh_ret: float) -> str:
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
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px auto; max-width: 980px; padding: 0 16px; line-height: 1.6; color: #1f2937; background: #f9fafb; }}
    h1, h2 {{ color: #111827; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; margin: 16px 0; background: #fff; }}
    .muted {{ color: #6b7280; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    img {{ width: 100%; border-radius: 10px; border: 1px solid #e5e7eb; background: #fff; }}
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
      <li><strong>HS300 daily return</strong>: {hs300_ret}%</li>
      <li><strong>SH Index daily return</strong>: {sh_ret}%</li>
    </ul>
    <p><a href="./latest.md">View latest markdown report</a> · <a href="./STATUS.md">Project status</a></p>
  </div>
  <div class="card">
    <h2>Sentiment-Market Linkage</h2>
    <p>{linkage_text}</p>
  </div>
  <div class="card">
    <h2>Methodology</h2>
    <ul>
      <li>News is collected from a small set of relatively stable public financial sources.</li>
      <li>Titles are cleaned with rule-based filtering, deduplication, and source-domain exclusion.</li>
      <li>Sentiment uses a hybrid score: SnowNLP model signal + finance-specific keyword rules.</li>
      <li>Market linkage currently compares daily sentiment with HS300 and SH Index returns.</li>
      <li>Historical linkage will become more informative as daily samples accumulate.</li>
    </ul>
  </div>
  <div class="card">
    <h2>How It Works</h2>
    <ol>
      <li>Ingest daily financial headlines</li>
      <li>Clean and deduplicate low-quality items</li>
      <li>Run hybrid sentiment scoring</li>
      <li>Fetch market index data</li>
      <li>Generate report, charts, and GitHub Pages output</li>
    </ol>
  </div>
  <div class="grid">
    <div class="card"><h2>Topic Distribution</h2><ul>{topic_html}</ul></div>
    <div class="card"><h2>Keyword Signals</h2><ul>{keyword_html}</ul></div>
  </div>
  <div class="grid">
    <div class="card"><h2>Sentiment Label Distribution</h2><img src="./assets/label_distribution.png" alt="label distribution" /></div>
    <div class="card"><h2>Topic Distribution Chart</h2><img src="./assets/topic_distribution.png" alt="topic distribution" /></div>
  </div>
  <div class="grid">
    <div class="card"><h2>Sentiment History</h2><img src="./assets/sentiment_history.png" alt="sentiment history" /></div>
    <div class="card"><h2>Sentiment vs HS300 Return History</h2><img src="./assets/sentiment_vs_hs300_history.png" alt="sentiment vs hs300 history" /></div>
  </div>
  <div class="grid">
    <div class="card"><h2>Data Sources</h2><ul><li>Public financial news pages / feeds</li><li>Rule-based cleaned headline set</li><li>Daily HS300 and SH Index market data</li></ul></div>
    <div class="card"><h2>Known Limitations</h2><ul><li>Some edge-case noise may still remain</li><li>Sentiment scoring is hybrid but not perfect</li><li>Historical linkage is still early because samples are short</li></ul></div>
  </div>
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
    history_path = ASSETS_DIR / "history.json"
    sentiment = json.loads(sentiment_path.read_text(encoding="utf-8"))
    market = json.loads(market_path.read_text(encoding="utf-8"))
    clean = json.loads(clean_path.read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []

    titles = [x["title"] for x in sentiment["items"]]
    negative_titles = [x["title"] for x in sentiment["items"] if x["sentiment_label"] == "negative"][:5]
    positive_titles = [x["title"] for x in sentiment["items"] if x["sentiment_label"] == "positive"][:5]
    topic_counts = detect_topics(titles)
    keyword_counts = detect_keywords(titles)
    score = sentiment['daily_sentiment_index']
    tone = classify_index(score)
    hs300_ret = calc_return(market['hs300'])
    sh_ret = calc_return(market['sh_index'])
    linkage_text = market_linkage_comment(score, hs300_ret, sh_ret, len(history))

    report = f"""# Daily Financial Sentiment Report - {today}\n\n## 1. Daily Sentiment Snapshot\n- Total cleaned news items: {sentiment['count']}\n- Dropped noisy items: {clean.get('dropped_count', 0)}\n- Daily sentiment index: {score}\n- Daily tone: {tone}\n- Label counts: {sentiment['label_counts']}\n- HS300 daily return: {hs300_ret}%\n- SH Index daily return: {sh_ret}%\n\n## 2. Sentiment-Market Linkage\n- {linkage_text}\n\n## 3. Topic Distribution\n"""
    for topic, count in topic_counts[:6]:
        report += f"- {topic}: {count}\n"
    report += "\n## 4. Keyword Signals\n"
    for key, count in keyword_counts[:8]:
        report += f"- {key}: {count}\n"
    report += "\n## 5. Positive Headline Examples\n"
    for title in positive_titles:
        report += f"- {title}\n"
    report += "\n## 6. Negative Headline Examples\n"
    for title in negative_titles:
        report += f"- {title}\n"
    report += "\n## 7. Market Data\n"
    report += f"- HS300 latest rows: {len(market['hs300'])}\n"
    report += f"- SH Index latest rows: {len(market['sh_index'])}\n"
    report += f"- History length: {len(history)}\n"
    report += "\n## 8. Visual Assets\n"
    report += "- label_distribution.png\n- topic_distribution.png\n- sentiment_history.png\n- sentiment_vs_hs300_history.png\n"
    report += "\n## 9. Brief Comment\n"
    report += f"Today's sentiment reading is {tone}. Key topics are concentrated in {', '.join([x[0] for x in topic_counts[:3]]) if topic_counts else 'general finance news'}. {linkage_text}\n"

    report_path = REPORTS_DIR / f"{today}.md"
    latest_path = DOCS_DIR / "latest.md"
    index_md_path = DOCS_DIR / "index.md"
    index_html_path = DOCS_DIR / "index.html"
    report_path.write_text(report, encoding="utf-8")
    latest_path.write_text(report, encoding="utf-8")
    index_md_path.write_text(
        f"# Financial News Sentiment Monitor\n\nLatest report: [Daily Report {today}](./latest.md)\n\n- Latest sentiment tone: {tone}\n- Cleaned news count: {sentiment['count']}\n- Dropped noisy items: {clean.get('dropped_count', 0)}\n- HS300 daily return: {hs300_ret}%\n- SH Index daily return: {sh_ret}%\n- History length: {len(history)}\n- Visual assets: label distribution / topic distribution / sentiment history / sentiment vs HS300 history\n\nThis page is updated automatically.\n",
        encoding="utf-8",
    )
    index_html_path.write_text(
        build_html(today, score, tone, sentiment['count'], clean.get('dropped_count', 0), topic_counts, keyword_counts, positive_titles, negative_titles, linkage_text, hs300_ret, sh_ret),
        encoding='utf-8'
    )
    print(f"report generated: {report_path}")
    print(f"html landing page generated: {index_html_path}")


if __name__ == "__main__":
    main()
