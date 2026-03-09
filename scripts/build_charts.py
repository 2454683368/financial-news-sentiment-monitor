from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = BASE_DIR / "data" / "processed"
DOCS_ASSETS = BASE_DIR / "docs" / "assets"
DOCS_ASSETS.mkdir(parents=True, exist_ok=True)


def load_today():
    today = datetime.now().strftime("%Y-%m-%d")
    sentiment_path = PROC_DIR / f"sentiment_{today}.json"
    market_path = PROC_DIR / f"market_{today}.json"
    sentiment = json.loads(sentiment_path.read_text(encoding="utf-8"))
    market = json.loads(market_path.read_text(encoding="utf-8"))
    return today, sentiment, market


def plot_label_distribution(today: str, sentiment: dict) -> str:
    labels = sentiment["label_counts"]
    x = list(labels.keys())
    y = [labels[k] for k in x]
    plt.figure(figsize=(6, 4))
    plt.bar(x, y, color=["#ef4444", "#10b981", "#9ca3af"])
    plt.title(f"Sentiment Label Distribution - {today}")
    plt.ylabel("Count")
    plt.tight_layout()
    path = DOCS_ASSETS / "label_distribution.png"
    plt.savefig(path, dpi=160)
    plt.close()
    return path.name


def plot_topic_distribution(today: str, sentiment: dict) -> str:
    topic_rules = {
        "宏观政策": ["两会", "政府工作报告", "货币政策", "财政", "PPI", "CPI", "经济", "稳汇率"],
        "资本市场": ["A股", "港股", "ETF", "股市", "IPO", "净买入", "回购", "涨停", "下跌"],
        "能源黄金": ["油价", "原油", "黄金", "燃油", "天然气", "WTI"],
        "科技AI": ["AI", "人工智能", "OpenClaw", "英伟达", "机器人", "算力", "大模型"],
        "金融监管": ["监管", "银行", "保险", "合规", "最高法", "最高检", "证券犯罪"],
        "国际局势": ["伊朗", "中东", "美国", "欧洲", "特朗普", "冲突", "北约"],
    }
    counts = {k: 0 for k in topic_rules}
    for item in sentiment["items"]:
        title = item["title"]
        for topic, kws in topic_rules.items():
            if any(k in title for k in kws):
                counts[topic] += 1
                break
    xs = list(counts.keys())
    ys = [counts[k] for k in xs]
    plt.figure(figsize=(8, 4.5))
    plt.barh(xs, ys, color="#3b82f6")
    plt.title(f"Topic Distribution - {today}")
    plt.xlabel("Count")
    plt.tight_layout()
    path = DOCS_ASSETS / "topic_distribution.png"
    plt.savefig(path, dpi=160)
    plt.close()
    return path.name


def plot_sentiment_vs_market(today: str, sentiment: dict, market: dict) -> str:
    hs300 = market.get("hs300", [])
    if not hs300:
        raise ValueError("hs300 data missing")
    dates = [row.get("date", "") for row in hs300][-10:]
    closes = [float(row.get("close", 0)) for row in hs300][-10:]
    sentiment_series = [sentiment["daily_sentiment_index"] for _ in dates]
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(dates, closes, color="#2563eb", marker="o", label="HS300 Close")
    ax1.set_ylabel("HS300 Close", color="#2563eb")
    ax1.tick_params(axis="y", labelcolor="#2563eb")
    ax1.tick_params(axis="x", rotation=30)
    ax2 = ax1.twinx()
    ax2.plot(dates, sentiment_series, color="#dc2626", linestyle="--", label="Sentiment Index")
    ax2.set_ylabel("Sentiment Index", color="#dc2626")
    ax2.tick_params(axis="y", labelcolor="#dc2626")
    plt.title(f"Sentiment vs HS300 - {today}")
    fig.tight_layout()
    path = DOCS_ASSETS / "sentiment_vs_hs300.png"
    plt.savefig(path, dpi=160)
    plt.close()
    return path.name


def main():
    today, sentiment, market = load_today()
    outputs = {
        "label_distribution": plot_label_distribution(today, sentiment),
        "topic_distribution": plot_topic_distribution(today, sentiment),
        "sentiment_vs_hs300": plot_sentiment_vs_market(today, sentiment, market),
    }
    out_path = DOCS_ASSETS / "charts.json"
    out_path.write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"charts generated: {out_path}")


if __name__ == "__main__":
    main()
