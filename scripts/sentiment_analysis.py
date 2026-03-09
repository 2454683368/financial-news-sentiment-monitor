from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from snownlp import SnowNLP

BASE_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = BASE_DIR / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

POS_WORDS = ["上涨", "增长", "提振", "回暖", "改善", "突破", "利好", "走强"]
NEG_WORDS = ["下跌", "风险", "承压", "收缩", "违约", "下行", "贬值", "波动"]


def rule_score(title: str) -> float:
    score = 0
    for w in POS_WORDS:
        if w in title:
            score += 1
    for w in NEG_WORDS:
        if w in title:
            score -= 1
    return score


def label(score: float) -> str:
    if score > 0.1:
        return "positive"
    if score < -0.1:
        return "negative"
    return "neutral"


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    in_path = PROC_DIR / f"news_clean_{today}.json"
    if not in_path.exists():
        raise FileNotFoundError(in_path)
    data = json.loads(in_path.read_text(encoding="utf-8"))
    results = []
    labels = Counter()
    hybrid_scores = []
    for item in data["items"]:
        title = item["title"]
        model_score = SnowNLP(title).sentiments  # 0~1
        model_centered = model_score - 0.5
        r_score = rule_score(title)
        hybrid = model_centered + 0.1 * r_score
        sent_label = label(hybrid)
        labels[sent_label] += 1
        hybrid_scores.append(hybrid)
        results.append({
            **item,
            "model_score": round(model_score, 4),
            "rule_score": r_score,
            "hybrid_score": round(hybrid, 4),
            "sentiment_label": sent_label,
        })
    avg_score = sum(hybrid_scores) / len(hybrid_scores) if hybrid_scores else 0
    out = {
        "generated_at": datetime.now().isoformat(),
        "count": len(results),
        "daily_sentiment_index": round(avg_score, 4),
        "label_counts": dict(labels),
        "items": results,
    }
    out_path = PROC_DIR / f"sentiment_{today}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved sentiment result to {out_path}")


if __name__ == "__main__":
    main()
