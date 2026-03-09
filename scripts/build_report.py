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

TOPIC_EN = {
    "宏观政策": "Macro Policy",
    "资本市场": "Capital Markets",
    "能源黄金": "Energy & Gold",
    "科技AI": "Tech & AI",
    "金融监管": "Financial Regulation",
    "国际局势": "Global Geopolitics",
    "其他": "Others",
}

KEYWORD_EN = {
    "两会": "Two Sessions",
    "货币政策": "Monetary Policy",
    "人民币汇率": "RMB FX",
    "黄金": "Gold",
    "油价": "Oil",
    "AI": "AI",
    "银行监管": "Bank Regulation",
    "中东冲突": "Middle East Conflict",
    "港股": "Hong Kong Stocks",
    "A股": "A Shares",
}


def classify_index(score: float) -> str:
    if score > 0.12:
        return "偏乐观"
    if score < -0.12:
        return "偏谨慎"
    return "中性偏平衡"


def classify_index_en(score: float) -> str:
    if score > 0.12:
        return "Optimistic"
    if score < -0.12:
        return "Cautious"
    return "Balanced / Neutral"


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


def market_linkage_comment_en(score: float, hs300_ret: float, sh_ret: float, history_len: int) -> str:
    tone = classify_index_en(score)
    suffix = "History is still short and needs more daily samples." if history_len < 5 else "A basic continuous sample is now available for further observation."
    if score > 0 and hs300_ret > 0:
        return f"Daily news sentiment is {tone}, while HS300 and SH Index rose {hs300_ret}% / {sh_ret}% respectively. News tone and market direction are broadly aligned. {suffix}"
    if score < 0 and hs300_ret < 0:
        return f"Daily news sentiment is {tone}, while HS300 and SH Index fell {abs(hs300_ret)}% / {abs(sh_ret)}% respectively. News tone and market direction are broadly aligned. {suffix}"
    return f"Daily news sentiment is {tone}, but HS300 / SH Index moved {hs300_ret}% / {sh_ret}%, suggesting a short-term divergence between news tone and market performance. {suffix}"


def build_html(today: str, score: float, tone: str, count: int, dropped: int, topics, keywords, positive_titles, negative_titles, linkage_text: str, linkage_text_en: str, hs300_ret: float, sh_ret: float, today_take_zh: str, today_take_en: str) -> str:
    topic_html_zh = ''.join([f'<li><strong>{t}</strong>: {c}</li>' for t, c in topics[:6]])
    topic_html_en = ''.join([f'<li><strong>{TOPIC_EN.get(t, t)}</strong>: {c}</li>' for t, c in topics[:6]])
    keyword_html_zh = ''.join([f'<li><strong>{k}</strong>: {c}</li>' for k, c in keywords[:8]])
    keyword_html_en = ''.join([f'<li><strong>{KEYWORD_EN.get(k, k)}</strong>: {c}</li>' for k, c in keywords[:8]])
    pos_html = ''.join([f'<li>{x}</li>' for x in positive_titles])
    neg_html = ''.join([f'<li>{x}</li>' for x in negative_titles])
    tone_en = classify_index_en(score)
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
    .toolbar {{ display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:16px; }}
    .lang-switch {{ display:flex; gap:8px; }}
    .lang-switch button {{ border:1px solid #d1d5db; background:#fff; border-radius:8px; padding:6px 12px; cursor:pointer; }}
    .lang-switch button.active {{ background:#111827; color:#fff; border-color:#111827; }}
    .badge {{ display:inline-block; padding:6px 10px; border-radius:999px; background:#dbeafe; color:#1d4ed8; font-size:14px; margin-top:8px; }}
    [data-lang] {{ display:none; }}
    [data-lang].active {{ display:block; }}
  </style>
  <script>
    function setLang(lang) {{
      localStorage.setItem('site_lang', lang);
      document.querySelectorAll('[data-lang]').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('[data-lang="' + lang + '"]').forEach(el => el.classList.add('active'));
      document.querySelectorAll('.lang-switch button').forEach(btn => btn.classList.remove('active'));
      document.getElementById('btn-' + lang).classList.add('active');
      document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
    }}
    window.addEventListener('DOMContentLoaded', () => setLang(localStorage.getItem('site_lang') || 'zh'));
  </script>
</head>
<body>
  <div class="toolbar">
    <div>
      <h1 data-lang="zh">财经新闻情绪与市场波动监测</h1>
      <h1 data-lang="en">Financial News Sentiment Monitor</h1>
      <p class="muted" data-lang="zh">一个轻量、可持续更新的财经新闻情绪与市场联动展示项目。</p>
      <p class="muted" data-lang="en">A lightweight and continuously updating project for financial news sentiment and market linkage.</p>
      <div class="badge" data-lang="zh">最近更新：{today}</div>
      <div class="badge" data-lang="en">Last updated: {today}</div>
    </div>
    <div class="lang-switch">
      <button id="btn-zh" onclick="setLang('zh')">中文</button>
      <button id="btn-en" onclick="setLang('en')">EN</button>
    </div>
  </div>

  <div class="card">
    <h2 data-lang="zh">最新快照 · {today}</h2>
    <h2 data-lang="en">Latest Snapshot · {today}</h2>
    <ul data-lang="zh">
      <li><strong>当日情绪指数</strong>: {score}</li>
      <li><strong>当日基调</strong>: {tone}</li>
      <li><strong>清洗后新闻数</strong>: {count}</li>
      <li><strong>过滤噪声数</strong>: {dropped}</li>
      <li><strong>沪深300日收益率</strong>: {hs300_ret}%</li>
      <li><strong>上证指数日收益率</strong>: {sh_ret}%</li>
    </ul>
    <ul data-lang="en">
      <li><strong>Daily sentiment index</strong>: {score}</li>
      <li><strong>Daily tone</strong>: {tone_en}</li>
      <li><strong>Cleaned news count</strong>: {count}</li>
      <li><strong>Dropped noisy items</strong>: {dropped}</li>
      <li><strong>HS300 daily return</strong>: {hs300_ret}%</li>
      <li><strong>SH Index daily return</strong>: {sh_ret}%</li>
    </ul>
    <p data-lang="zh"><a href="./latest.md">查看最新 Markdown 日报</a> · <a href="./STATUS.md">项目状态</a></p>
    <p data-lang="en"><a href="./latest.md">View latest markdown report</a> · <a href="./STATUS.md">Project status</a></p>
  </div>

  <div class="card">
    <h2 data-lang="zh">今日结论</h2>
    <h2 data-lang="en">Today's Take</h2>
    <p data-lang="zh">{today_take_zh}</p>
    <p data-lang="en">{today_take_en}</p>
    <p class="muted" data-lang="zh">项目定位：用于观察财经新闻情绪与市场联动，不直接作为交易预测信号。</p>
    <p class="muted" data-lang="en">Project scope: designed for observing news sentiment and market linkage, not as a direct trading signal.</p>
  </div>
  <div class="card">
    <h2 data-lang="zh">情绪-市场联动解释</h2>
    <h2 data-lang="en">Sentiment-Market Linkage</h2>
    <p data-lang="zh">{linkage_text}</p>
    <p data-lang="en">{linkage_text_en}</p>
  </div>

  <div class="card">
    <h2 data-lang="zh">方法说明</h2>
    <h2 data-lang="en">Methodology</h2>
    <ul data-lang="zh">
      <li>从少量相对稳定的公开财经新闻源抓取标题。</li>
      <li>通过规则过滤、去重、域名排除等方式清洗标题。</li>
      <li>情绪评分采用 SnowNLP + 财经关键词规则 的混合方案。</li>
      <li>市场联动目前比较情绪指数与沪深300 / 上证收益率。</li>
      <li>随着历史样本积累，多日联动分析会越来越有信息量。</li>
    </ul>
    <ul data-lang="en">
      <li>Headlines are collected from a small set of relatively stable public financial sources.</li>
      <li>Titles are cleaned with rule-based filtering, deduplication, and domain exclusion.</li>
      <li>Sentiment uses a hybrid score: SnowNLP + finance-specific keyword rules.</li>
      <li>Market linkage currently compares the sentiment index with HS300 and SH Index returns.</li>
      <li>Historical linkage becomes more informative as daily samples accumulate.</li>
    </ul>
  </div>

  <div class="card">
    <h2 data-lang="zh">流程</h2>
    <h2 data-lang="en">How It Works</h2>
    <ol data-lang="zh">
      <li>抓取当日财经新闻标题</li>
      <li>清洗去重低质量内容</li>
      <li>执行混合情绪打分</li>
      <li>抓取市场指数数据</li>
      <li>生成图表、报告与 GitHub Pages 页面</li>
    </ol>
    <ol data-lang="en">
      <li>Ingest daily financial headlines</li>
      <li>Clean and deduplicate low-quality items</li>
      <li>Run hybrid sentiment scoring</li>
      <li>Fetch market index data</li>
      <li>Generate charts, reports, and GitHub Pages output</li>
    </ol>
  </div>

  <div class="grid">
    <div class="card">
      <h2 data-lang="zh">主题分布</h2>
      <h2 data-lang="en">Topic Distribution</h2>
      <ul data-lang="zh">{topic_html_zh}</ul>
      <ul data-lang="en">{topic_html_en}</ul>
    </div>
    <div class="card">
      <h2 data-lang="zh">关键词信号</h2>
      <h2 data-lang="en">Keyword Signals</h2>
      <ul data-lang="zh">{keyword_html_zh}</ul>
      <ul data-lang="en">{keyword_html_en}</ul>
    </div>
  </div>

  <div class="grid">
    <div class="card"><h2>Sentiment Label Distribution</h2><img src="./assets/label_distribution.png" alt="label distribution" /></div>
    <div class="card"><h2>Topic Distribution Chart</h2><img src="./assets/topic_distribution.png" alt="topic distribution" /></div>
  </div>
  <div class="grid">
    <div class="card"><h2>Sentiment History</h2><img src="./assets/sentiment_history.png" alt="sentiment history" /><p class="muted" data-lang="zh">历史图会随着每日自动运行逐步丰富，目前仍处于样本积累早期。</p><p class="muted" data-lang="en">Historical charts will become more informative as daily runs accumulate. The sample is still at an early stage.</p></div>
    <div class="card"><h2>Sentiment vs HS300 Return History</h2><img src="./assets/sentiment_vs_hs300_history.png" alt="sentiment vs hs300 history" /><p class="muted" data-lang="zh">当前更适合作为联动观察面板，而非正式统计结论。</p><p class="muted" data-lang="en">At the current stage, this is better interpreted as an observation panel rather than a formal statistical conclusion.</p></div>
  </div>

  <div class="grid">
    <div class="card">
      <h2 data-lang="zh">数据来源</h2>
      <h2 data-lang="en">Data Sources</h2>
      <ul data-lang="zh"><li>公开财经新闻页面 / RSS 类来源</li><li>规则清洗后的标题样本</li><li>沪深300与上证指数日度数据</li></ul>
      <ul data-lang="en"><li>Public financial news pages / feed-like sources</li><li>Rule-cleaned headline samples</li><li>Daily HS300 and SH Index data</li></ul>
    </div>
    <div class="card">
      <h2 data-lang="zh">已知局限</h2>
      <h2 data-lang="en">Known Limitations</h2>
      <ul data-lang="zh"><li>仍可能存在少量边界噪声</li><li>混合情绪评分仍不是完美分类器</li><li>历史联动样本目前仍较短</li></ul>
      <ul data-lang="en"><li>Some edge-case noise may still remain</li><li>The hybrid sentiment model is improved but not perfect</li><li>Historical linkage is still early because the sample is short</li></ul>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2 data-lang="zh">正面样例</h2>
      <h2 data-lang="en">Positive Examples</h2>
      <ul>{pos_html}</ul>
    </div>
    <div class="card">
      <h2 data-lang="zh">负面样例</h2>
      <h2 data-lang="en">Negative Examples</h2>
      <ul>{neg_html}</ul>
    </div>
  </div>
</body>
</html>
"""




def latest_available_date() -> str:
    candidates = sorted(PROC_DIR.glob("sentiment_*.json"))
    if not candidates:
        raise FileNotFoundError("No sentiment_*.json files found in processed data")
    latest = candidates[-1].stem.replace("sentiment_", "")
    return latest



def build_today_take(score: float, hs300_ret: float, topic_counts: list[tuple[str, int]]) -> tuple[str, str]:
    top_topics = '、'.join([x[0] for x in topic_counts[:2]]) if topic_counts else '综合财经信息'
    top_topics_en = ', '.join([TOPIC_EN.get(x[0], x[0]) for x in topic_counts[:2]]) if topic_counts else 'general finance news'
    zh = f"今日新闻情绪整体为{classify_index(score)}，市场偏弱，关注点主要集中在{top_topics}。当前更适合作为风险情绪观察，而不是方向性预测。"
    en = f"Today's news tone is {classify_index_en(score)} with a softer market backdrop. The main attention is concentrated in {top_topics_en}. At this stage, the dashboard is more suitable for risk-sentiment observation than directional prediction."
    return zh, en

def main() -> None:
    today = latest_available_date()
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
    linkage_text_en = market_linkage_comment_en(score, hs300_ret, sh_ret, len(history))
    today_take_zh, today_take_en = build_today_take(score, hs300_ret, topic_counts)

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
        build_html(today, score, tone, sentiment['count'], clean.get('dropped_count', 0), topic_counts, keyword_counts, positive_titles, negative_titles, linkage_text, linkage_text_en, hs300_ret, sh_ret, today_take_zh, today_take_en),
        encoding='utf-8'
    )
    print(f"report generated: {report_path}")
    print(f"html landing page generated: {index_html_path}")


if __name__ == "__main__":
    main()
