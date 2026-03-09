from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

BASE_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = BASE_DIR / "data" / "processed"
DOCS_ASSETS = BASE_DIR / "docs" / "assets"
DOCS_ASSETS.mkdir(parents=True, exist_ok=True)
HISTORY_PATH = DOCS_ASSETS / "history.json"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def setup_chinese_font() -> str:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            font_manager.fontManager.addfont(path)
            prop = font_manager.FontProperties(fname=path)
            font_name = prop.get_name()
            rcParams["font.family"] = font_name
            rcParams["axes.unicode_minus"] = False
            return font_name
    rcParams["axes.unicode_minus"] = False
    return "default"




def latest_available_date() -> str:
    candidates = sorted(PROC_DIR.glob("sentiment_*.json"))
    if not candidates:
        raise FileNotFoundError("No sentiment_*.json files found in processed data")
    return candidates[-1].stem.replace("sentiment_", "")

def load_today():
    today = latest_available_date()
    sentiment_path = PROC_DIR / f"sentiment_{today}.json"
    market_path = PROC_DIR / f"market_{today}.json"
    sentiment = json.loads(sentiment_path.read_text(encoding="utf-8"))
    market = json.loads(market_path.read_text(encoding="utf-8"))
    history = json.loads(HISTORY_PATH.read_text(encoding="utf-8")) if HISTORY_PATH.exists() else []
    return today, sentiment, market, history


def plot_label_distribution(today: str, sentiment: dict) -> str:
    labels = sentiment["label_counts"]
    order = ["positive", "neutral", "negative"]
    x = [k for k in order if k in labels]
    y = [labels[k] for k in x]
    plt.figure(figsize=(6, 4))
    plt.bar(x, y, color=["#10b981", "#9ca3af", "#ef4444"][: len(x)])
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


def plot_history_sentiment(history: list[dict]) -> str:
    dates = [x["date"] for x in history]
    scores = [x["sentiment_index"] for x in history]
    plt.figure(figsize=(8, 4.5))
    plt.plot(dates, scores, marker="o", color="#dc2626")
    plt.title("Sentiment Index History")
    plt.ylabel("Sentiment Index")
    plt.xticks(rotation=30)
    plt.tight_layout()
    path = DOCS_ASSETS / "sentiment_history.png"
    plt.savefig(path, dpi=160)
    plt.close()
    return path.name


def plot_history_market_linkage(history: list[dict]) -> str:
    dates = [x["date"] for x in history]
    sentiments = [x["sentiment_index"] for x in history]
    hs300_returns = [x["hs300_return"] for x in history]
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(dates, sentiments, marker="o", color="#dc2626")
    ax1.set_ylabel("Sentiment Index", color="#dc2626")
    ax1.tick_params(axis="y", labelcolor="#dc2626")
    ax1.tick_params(axis="x", rotation=30)
    ax2 = ax1.twinx()
    ax2.bar(dates, hs300_returns, alpha=0.3, color="#2563eb")
    ax2.set_ylabel("HS300 Return (%)", color="#2563eb")
    ax2.tick_params(axis="y", labelcolor="#2563eb")
    plt.title("Sentiment vs HS300 Return History")
    fig.tight_layout()
    path = DOCS_ASSETS / "sentiment_vs_hs300_history.png"
    plt.savefig(path, dpi=160)
    plt.close()
    return path.name


def main():
    font_name = setup_chinese_font()
    today, sentiment, market, history = load_today()
    outputs = {
        "font": font_name,
        "label_distribution": plot_label_distribution(today, sentiment),
        "topic_distribution": plot_topic_distribution(today, sentiment),
        "sentiment_history": plot_history_sentiment(history),
        "sentiment_vs_hs300_history": plot_history_market_linkage(history),
    }
    out_path = DOCS_ASSETS / "charts.json"
    out_path.write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"charts generated: {out_path}")
    print(f"font selected: {font_name}")


if __name__ == "__main__":
    main()
