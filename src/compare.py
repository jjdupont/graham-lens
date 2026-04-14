import json
import pandas as pd
from pathlib import Path
from logger import get_logger

log = get_logger(__name__)

OUTPUTS_DIR = Path("outputs")

def load_signals() -> pd.DataFrame:
    records = []
    for f in sorted(OUTPUTS_DIR.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        records.append({
            "company": d["company"],
            "year": d["year"],
            "graham_score_llm": d["graham_score_llm"],
            "confidence": d["confidence"],
            "leverage": d["financial_health"]["leverage"],
            "liquidity": d["financial_health"]["liquidity"],
            "stability": d["earnings_quality"]["stability"],
            "trend": d["earnings_quality"]["trend"],
            "moat_signals": ", ".join(d["moat_signals"]) or "—",
            "red_flags": ", ".join(d["red_flags"]) or "—",
        })
    if not records:
        log.warning("No scorecard files found in outputs/")
        return pd.DataFrame()
    return pd.DataFrame(records).sort_values("graham_score_llm", ascending=False).reset_index(drop=True)


def print_ranking(df: pd.DataFrame) -> None:
    if df.empty:
        log.warning("No data to display.")
        return
    print("\n--- GrahamLens Ranking ---\n")
    for _, row in df.iterrows():
        print(f"\n=== {row['company']} ({row['year']}) — score: {row['graham_score_llm']}/100, conf: {row['confidence']:.0%} ===")
        print(f"\n--- OVERALL: \nleveage: {row['leverage']}; liquidity: {row['liquidity']}; earnings: {row['stability']} {row['trend']}")
        print(f"\n--- MOAT: \n{row['moat_signals'] or '—'}")
        print(f"\n--- FLAGS: \n{row['red_flags'] or '—'}")
        print()
