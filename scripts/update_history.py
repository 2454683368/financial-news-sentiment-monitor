from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = BASE_DIR / "data" / "processed"
DOCS_ASSETS = BASE_DIR / "docs" / "assets"
DOCS_ASSETS.mkdir(parents=True, exist_ok=True)
HISTORY_PATH = DOCS_ASSETS / "history.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    sentiment = load_json(PROC_DIR / f"sentiment_{today}.json")
    market = load_json(PROC_DIR / f"market_{today}.json")

    hs300 = market.get("hs300", [])
    sh_index = market.get("sh_index", [])
    hs300_ret = 0.0
    sh_ret = 0.0
    if len(hs300) >= 2:
        hs300_ret = round((float(hs300[-1]["close"]) / float(hs300[-2]["close"]) - 1) * 100, 2)
    if len(sh_index) >= 2:
        sh_ret = round((float(sh_index[-1]["close"]) / float(sh_index[-2]["close"]) - 1) * 100, 2)

    entry = {
        "date": today,
        "sentiment_index": sentiment["daily_sentiment_index"],
        "positive": sentiment["label_counts"].get("positive", 0),
        "neutral": sentiment["label_counts"].get("neutral", 0),
        "negative": sentiment["label_counts"].get("negative", 0),
        "news_count": sentiment["count"],
        "hs300_return": hs300_ret,
        "sh_index_return": sh_ret,
    }

    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    else:
        history = []

    history = [x for x in history if x.get("date") != today]
    history.append(entry)
    history.sort(key=lambda x: x["date"])

    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"history updated: {HISTORY_PATH}")


if __name__ == "__main__":
    main()
