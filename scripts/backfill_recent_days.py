from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict
from datetime import date, datetime, timedelta
from pathlib import Path

import akshare as ak
from snownlp import SnowNLP

from ingest_news import NewsItem

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROC_DIR = BASE_DIR / 'data' / 'processed'
DOCS_ASSETS = BASE_DIR / 'docs' / 'assets'
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)
DOCS_ASSETS.mkdir(parents=True, exist_ok=True)
HISTORY_PATH = DOCS_ASSETS / 'history.json'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

STOP_PATTERNS = [
    r'直播', r'视频', r'专题', r'点击查看', r'收起', r'业绩说明会', r'路演',
    r'ICP备', r'协会$', r'交易所$', r'理事会$', r'公司$', r'官网$',
    r'中国证券登记结算', r'中国上市公司协会', r'中国证券投资基金业协会',
    r'全国社保基金理事会', r'中国金融期货交易所',
    r'高质量发展大会', r'颁奖典礼', r'论坛$', r'大会$', r'金牛奖',
    r'宣传活动', r'教育活动', r'进社区', r'进校园', r'消费者权益保护', r'3·15', r'学雷锋',
    r'主题活动', r'微沙龙', r'宣讲会', r'研讨会', r'系列展播', r'网络研讨会', r'趣味互动',
    r'答卷', r'事迹', r'专访', r'观察', r'解读', r'声音', r'点题', r'作答', r'为民办实事',
    r'护航', r'守护', r'赋能', r'润', r'活水', r'温度', r'担当', r'强国建设', r'中国特色金融发展之路',
]
TIME_PREFIX = re.compile(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+')

POS_WORDS = [
    '上涨', '增长', '提振', '回暖', '改善', '突破', '利好', '走强', '创新高', '净买入', '宽松',
    '净利预增', '纳入港股通', '大力推广', '正式纳入', '分红', '上调评级', '超预期', '增持'
]
NEG_WORDS = [
    '下跌', '风险', '承压', '收缩', '违约', '下行', '贬值', '波动', '大跌', '崩盘', '冲突', '通胀担忧', '拖累', '减弱',
    '撤离', '停火', '抄袭', '致歉', '飙升', '战事', '中断', '震动', '油价飙升', '价格飙升',
    '滞胀', '通胀', '加息', '高企', '战争', '紧张局势', '袭击', '制裁', '回升至', '押注',
    '离世', '意外离世', '立案', '维权', '受损投资者', '火葬场', '供应中断', '供应收紧', '概率大幅上升'
]
STRONG_NEG = [
    '下跌', '大跌', '崩盘', '风险', '违约', '拖累', '减弱', '承压', '冲突', '飙升', '恐慌',
    '撤离', '通胀', '抄袭', '致歉', '战事', '中断', '油价飙升', '价格飙升', '滞胀', '战争',
    '紧张局势', '袭击', '制裁', '加息', '高企', '离世', '立案', '维权', '供应中断', '供应收紧'
]
STRONG_POS = [
    '增长', '提振', '改善', '突破', '创新高', '净买入', '回暖', '宽松',
    '净利预增', '纳入港股通', '大力推广', '正式纳入', '上调评级', '超预期', '增持'
]


def fetch_google_news(day: date) -> list[NewsItem]:
    next_day = day + timedelta(days=1)
    query = f'财经 OR 金融 after:{day.isoformat()} before:{next_day.isoformat()}'
    q = urllib.parse.quote(query)
    url = f'https://news.google.com/rss/search?q={q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
    req = urllib.request.Request(url, headers=HEADERS)
    xml_text = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', 'ignore')
    root = ET.fromstring(xml_text)
    items: list[NewsItem] = []
    seen = set()
    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        pub = (item.findtext('pubDate') or '').strip()
        if not title or not link:
            continue
        title = re.sub(r'\s+-\s+[^-]+$', '', title).strip()
        if title in seen:
            continue
        seen.add(title)
        items.append(NewsItem(title=title, url=link, source='google_news_rss', published_at=pub))
    return items[:100]


def normalize_title(title: str) -> str:
    title = re.sub(r'\s+', ' ', title).strip().replace('\u3000', ' ')
    title = TIME_PREFIX.sub('', title)
    return title


def is_valid_title(title: str, url: str = '') -> bool:
    if len(title) < 10:
        return False
    for pat in STOP_PATTERNS:
        if re.search(pat, title):
            return False
    bad_domains = ['roadshow', 'rs.cs.com.cn', 'beian.miit.gov.cn']
    if any(x in url for x in bad_domains):
        return False
    if title.count('：') > 2:
        return False
    finance_count = title.count('金融')
    if finance_count >= 2 and not any(k in title for k in ['市场', '股', '汇率', '利率', '通胀', '油价', '货币政策', '经济增长', 'IPO']):
        return False
    if any(k in title for k in ['活动', '宣传', '讲座', '专访', '事迹', '教育']) and not any(k in title for k in ['A股', '港股', '美股', '汇率', '油价', '通胀', '加息', '降息']):
        return False
    return True


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


def special_case_adjustment(title: str) -> float:
    bonus = 0.0
    risk_terms = ['战争', '战事', '冲突', '紧张局势', '袭击', '制裁', '滞胀', '通胀', '加息', '高企', '押注']
    oil_terms = ['油价', '原油', '汽油价格', '天然气', '能源供应']
    event_negative_terms = ['离世', '意外离世', '立案', '维权', '受损投资者', '火葬场']
    if '油价飙升' in title or '价格飙升' in title:
        bonus -= 1.2
    if any(term in title for term in risk_terms):
        bonus -= 0.8
    if any(term in title for term in event_negative_terms):
        bonus -= 1.0
    if any(term in title for term in oil_terms) and any(term in title for term in ['飙升', '升至', '涨至', '高企', '紧张局势']):
        bonus -= 0.8
    if any(term in title for term in ['供应中断', '供应收紧', '概率大幅上升']):
        bonus -= 1.0
    if '突破' in title and any(term in title for term in oil_terms):
        bonus -= 0.8
    if '上涨' in title and any(term in title for term in ['通胀', '油价', '战争']):
        bonus -= 0.6
    if '上调评级' in title and any(term in title for term in ['股价', '公司', '个股']):
        bonus += 0.4
    return bonus


def hybrid_score(title: str) -> tuple[float, float, float]:
    model_score = SnowNLP(title).sentiments
    model_centered = model_score - 0.5
    r_score = rule_score(title) + special_case_adjustment(title)
    hybrid = 0.4 * model_centered + 0.6 * (r_score / 3)
    return model_score, r_score, hybrid


def label(score: float) -> str:
    if score > 0.08:
        return 'positive'
    if score < -0.08:
        return 'negative'
    return 'neutral'


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding='utf-8')


def backfill_day(day: date, hs300_df, sh_df) -> dict:
    raw_items = fetch_google_news(day)
    raw_path = RAW_DIR / f'news_{day.isoformat()}.json'
    save_json(raw_path, {
        'generated_at': datetime.now().isoformat(),
        'count': len(raw_items),
        'items': [asdict(x) for x in raw_items],
        'backfill_source': 'google_news_rss'
    })

    seen = set()
    cleaned = []
    dropped = []
    for item in raw_items:
        title = normalize_title(item.title)
        if not is_valid_title(title, item.url):
            dropped.append({'title': title, 'url': item.url})
            continue
        if title in seen:
            continue
        seen.add(title)
        cleaned.append({'title': title, 'url': item.url, 'source': item.source, 'published_at': item.published_at})

    clean_path = PROC_DIR / f'news_clean_{day.isoformat()}.json'
    save_json(clean_path, {
        'generated_at': datetime.now().isoformat(),
        'count': len(cleaned),
        'dropped_count': len(dropped),
        'items': cleaned,
        'dropped_examples': dropped[:40],
        'backfill_source': 'google_news_rss'
    })

    results = []
    labels = Counter()
    scores = []
    for item in cleaned:
        model_score, r_score, hybrid = hybrid_score(item['title'])
        sent_label = label(hybrid)
        labels[sent_label] += 1
        scores.append(hybrid)
        results.append({**item, 'model_score': round(model_score, 4), 'rule_score': round(r_score, 4), 'hybrid_score': round(hybrid, 4), 'sentiment_label': sent_label})

    sentiment_path = PROC_DIR / f'sentiment_{day.isoformat()}.json'
    save_json(sentiment_path, {
        'generated_at': datetime.now().isoformat(),
        'count': len(results),
        'daily_sentiment_index': round(sum(scores) / len(scores), 4) if scores else 0,
        'label_counts': dict(labels),
        'items': results,
        'backfill_source': 'google_news_rss'
    })

    hs_slice = hs300_df[hs300_df['date'] <= day.isoformat()].tail(10)
    sh_slice = sh_df[sh_df['date'] <= day.isoformat()].tail(10)
    market_path = PROC_DIR / f'market_{day.isoformat()}.json'
    save_json(market_path, {
        'generated_at': datetime.now().isoformat(),
        'hs300': hs_slice.to_dict(orient='records'),
        'sh_index': sh_slice.to_dict(orient='records'),
        'backfill_source': 'akshare_historical_slice'
    })

    hs_records = hs_slice.to_dict(orient='records')
    sh_records = sh_slice.to_dict(orient='records')
    hs_ret = round((float(hs_records[-1]['close']) / float(hs_records[-2]['close']) - 1) * 100, 2) if len(hs_records) >= 2 else 0.0
    sh_ret = round((float(sh_records[-1]['close']) / float(sh_records[-2]['close']) - 1) * 100, 2) if len(sh_records) >= 2 else 0.0
    return {
        'date': day.isoformat(),
        'sentiment_index': round(sum(scores) / len(scores), 4) if scores else 0,
        'positive': labels.get('positive', 0),
        'neutral': labels.get('neutral', 0),
        'negative': labels.get('negative', 0),
        'news_count': len(results),
        'hs300_return': hs_ret,
        'sh_index_return': sh_ret,
        'backfill_source': 'google_news_rss'
    }


def main() -> None:
    today = date.today()
    start = today - timedelta(days=7)
    end = today - timedelta(days=1)
    hs300 = ak.stock_zh_index_daily(symbol='sh000300').copy()
    sh = ak.stock_zh_index_daily(symbol='sh000001').copy()
    hs300['date'] = hs300['date'].astype(str)
    sh['date'] = sh['date'].astype(str)

    history = []
    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text(encoding='utf-8'))
    history = [x for x in history if not (start.isoformat() <= x.get('date', '') <= end.isoformat())]

    summaries = []
    day = start
    while day <= end:
        entry = backfill_day(day, hs300, sh)
        history.append(entry)
        summaries.append(entry)
        print(f"backfilled {day.isoformat()}: news={entry['news_count']} sentiment={entry['sentiment_index']}")
        day += timedelta(days=1)

    history.sort(key=lambda x: x['date'])
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')
    print('history rebuilt:', HISTORY_PATH)
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
