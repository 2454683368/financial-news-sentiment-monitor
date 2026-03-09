from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

STOP_PATTERNS = [r"直播", r"视频", r"专题", r"点击查看", r"收起"]


def normalize_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    title = title.replace("\u3000", " ")
    return title


def is_valid_title(title: str) -> bool:
    if len(title) < 8:
        return False
    for pat in STOP_PATTERNS:
        if re.search(pat, title):
            return False
    return True


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    raw_path = RAW_DIR / f"news_{today}.json"
    if not raw_path.exists():
        raise FileNotFoundError(raw_path)
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    seen = set()
    cleaned = []
    for item in data["items"]:
        title = normalize_title(item["title"])
        if not is_valid_title(title):
            continue
        if title in seen:
            continue
        seen.add(title)
        item["title"] = title
        cleaned.append(item)
    out = {
        "generated_at": datetime.now().isoformat(),
        "count": len(cleaned),
        "items": cleaned,
    }
    out_path = PROC_DIR / f"news_clean_{today}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {len(cleaned)} items to {out_path}")


if __name__ == "__main__":
    main()
