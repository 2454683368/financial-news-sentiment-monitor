from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=None, help='Date in YYYY-MM-DD format')
    return parser.parse_args()

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    published_at: str | None = None


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return resp.text


def parse_sina_roll() -> List[NewsItem]:
    url = "https://finance.sina.com.cn/roll/"
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    items: List[NewsItem] = []
    for a in soup.select("a"):
        title = a.get_text(" ", strip=True)
        href = a.get("href")
        if not title or not href:
            continue
        if len(title) < 8:
            continue
        if "finance.sina.com.cn" not in href and not href.startswith("/"):
            continue
        if href.startswith("/"):
            href = "https://finance.sina.com.cn" + href
        items.append(NewsItem(title=title, url=href, source="sina_finance"))
    return dedup_items(items)[:80]


def parse_cs_news() -> List[NewsItem]:
    url = "https://www.cs.com.cn/xwzx/hg/"
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    items: List[NewsItem] = []
    for a in soup.select("a"):
        title = a.get_text(" ", strip=True)
        href = a.get("href")
        if not title or not href:
            continue
        if len(title) < 8:
            continue
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = "https://www.cs.com.cn" + href
        if not href.startswith("http"):
            continue
        items.append(NewsItem(title=title, url=href, source="cs_news"))
    return dedup_items(items)[:80]


def dedup_items(items: List[NewsItem]) -> List[NewsItem]:
    seen = set()
    out = []
    for item in items:
        key = item.title.strip()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def save_items(items: List[NewsItem], date_str: str = None) -> Path:
    today = date_str or datetime.now().strftime("%Y-%m-%d")
    path = RAW_DIR / f"news_{today}.json"
    payload = {
        "generated_at": datetime.now().isoformat(),
        "count": len(items),
        "items": [asdict(x) for x in items],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    args = parse_args()
    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    items: List[NewsItem] = []
    for func in (parse_sina_roll, parse_cs_news):
        try:
            items.extend(func())
        except Exception as exc:
            print(f"[WARN] {func.__name__} failed: {exc}")
    items = dedup_items(items)
    output = save_items(items, target_date)
    print(f"saved {len(items)} items to {output}")


if __name__ == "__main__":
    main()
