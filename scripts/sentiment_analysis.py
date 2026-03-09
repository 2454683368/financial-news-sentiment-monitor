from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from snownlp import SnowNLP

BASE_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = BASE_DIR / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

POS_WORDS = [
    "上涨", "增长", "提振", "回暖", "改善", "突破", "利好", "走强", "创新高", "净买入", "宽松",
    "净利预增", "纳入港股通", "大力推广", "正式纳入", "分红"
]
NEG_WORDS = [
    "下跌", "风险", "承压", "收缩", "违约", "下行", "贬值", "波动", "大跌", "崩盘", "冲突", "通胀担忧", "拖累", "减弱",
    "撤离", "停火", "抄袭", "致歉", "飙升", "战事", "中断", "震动"
]

STRONG_NEG = [
    "下跌", "大跌", "崩盘", "风险", "违约", "拖累", "减弱", "承压", "冲突", "飙升", "恐慌",
    "撤离", "通胀", "抄袭", "致歉", "战事", "中断"
]
STRONG_POS = [
    "增长", "提振", "改善", "突破", "创新高", "净买入", "回暖", "宽松",
    "净利预增", "纳入港股通", "大力推广", "正式纳入"
]


def rule_score(title: str) -> float:
    score = 0.0
    for w in POS_WORDS:
        if w in title:
            score += 1.0
    for w in NEG_WORDS:
        if w in title:
            score -= 1.0
    for w in STRONG_NEG:
        if w in title:
            score -= 0.6
    for w in STRONG_POS:
        if w in title:
            score += 0.4
    return score


def hybrid_score(title: str) -> float:
    model_score = SnowNLP(title).sentiments
    model_centered = model_score - 0.5
    r_score = rule_score(title)
    hybrid = 0.4 * model_centered + 0.6 * (r_score / 3)
    return model_score, r_score, hybrid


def label(score: float) -> str:
    if score > 0.08:
        return "positive"
    if score < -0.08:
        return "negative"
    return "neutral"


def latest_available_date() -> str:
    candidates = sorted(PROC_DIR.glob("news_clean_*.json"))
    if not candidates:
        raise FileNotFoundError("No news_clean_*.json files found in processed data")
    return candidates[-1].stem.replace("news_clean_", "")


def main() -> None:
    today = latest_available_date()
    in_path = PROC_DIR / f"news_clean_{today}.json"
    if not in_path.exists():
        raise FileNotFoundError(in_path)
    data = json.loads(in_path.read_text(encoding="utf-8"))
    results = []
    labels = Counter()
    hybrid_scores = []
    for item in data["items"]:
        title = item["title"]
        model_score, r_score, hybrid = hybrid_score(title)
        sent_label = label(hybrid)
        labels[sent_label] += 1
        hybrid_scores.append(hybrid)
        results.append({
            **item,
            "model_score": round(model_score, 4),
            "rule_score": round(r_score, 4),
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
