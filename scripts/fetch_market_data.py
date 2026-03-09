from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import akshare as ak

BASE_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = BASE_DIR / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    hs300 = ak.stock_zh_index_daily(symbol="sh000300").tail(10)
    sh = ak.stock_zh_index_daily(symbol="sh000001").tail(10)
    payload = {
        "generated_at": datetime.now().isoformat(),
        "hs300": hs300.to_dict(orient="records"),
        "sh_index": sh.to_dict(orient="records"),
    }
    out_path = PROC_DIR / f"market_{today}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"saved market data to {out_path}")


if __name__ == "__main__":
    main()
