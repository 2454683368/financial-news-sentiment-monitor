from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

STOP_PATTERNS = [
    r"直播", r"视频", r"专题", r"点击查看", r"收起", r"业绩说明会", r"路演",
    r"ICP备", r"协会$", r"交易所$", r"理事会$", r"公司$", r"官网$",
    r"中国证券登记结算", r"中国上市公司协会", r"中国证券投资基金业协会",
    r"全国社保基金理事会", r"中国金融期货交易所",
    r"高质量发展大会", r"颁奖典礼", r"论坛$", r"大会$", r"金牛奖",
]

TIME_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+")


def normalize_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    title = title.replace("\u3000", " ")
    title = TIME_PREFIX.sub("", title)
    return title


def is_valid_title(title: str, url: str = "") -> bool:
    if len(title) < 10:
        return False
    for pat in STOP_PATTERNS:
        if re.search(pat, title):
            return False
    bad_domains = ["roadshow", "rs.cs.com.cn", "beian.miit.gov.cn"]
    if any(x in url for x in bad_domains):
        return False
    if title.count("：") > 2:
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
    dropped = []
    for item in data["items"]:
        title = normalize_title(item["title"])
        url = item.get("url", "")
        if not is_valid_title(title, url):
            dropped.append({"title": title, "url": url})
            continue
        if title in seen:
            continue
        seen.add(title)
        item["title"] = title
        cleaned.append(item)
    out = {
        "generated_at": datetime.now().isoformat(),
        "count": len(cleaned),
        "dropped_count": len(dropped),
        "items": cleaned,
        "dropped_examples": dropped[:40],
    }
    out_path = PROC_DIR / f"news_clean_{today}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {len(cleaned)} items to {out_path}; dropped={len(dropped)}")


if __name__ == "__main__":
    main()
