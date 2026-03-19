"""3-platform 병렬 검색 오케스트레이터."""

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from . import reddit, tiktok, instagram
from .markdown import build_markdown
from ..env import load_env
from ..utils import safe_print


def search(query: str, depth: str = "quick") -> dict:
    """Reddit/TikTok/Instagram 검색 실행.

    Returns:
        {
            "query": str,
            "depth": str,
            "elapsed": float,
            "reddit": {...},
            "tiktok": {...},
            "instagram": {...},
        }
    """
    load_env()
    token = os.environ.get("SCRAPECREATORS_API_KEY", "")
    if not token:
        raise ValueError("SCRAPECREATORS_API_KEY not set. Check .env file.")

    safe_print(f"API Key: {token[:8]}...{token[-4:]}")
    safe_print(f"Query: {query}")
    safe_print(f"Depth: {depth}\n")

    now = datetime.now(tz=timezone.utc)
    to_date = now.strftime("%Y-%m-%d")
    from_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    safe_print(f"Date range: {from_date} ~ {to_date}\n")

    start = time.time()
    results = {"query": query, "depth": depth}

    # Reddit
    safe_print("[1/3] Reddit 검색 중...")
    try:
        r = reddit.search_and_enrich(query, from_date, to_date, depth=depth, token=token)
        safe_print(f"  -> {len(r.get('items', []))}건")
        results["reddit"] = r
    except Exception as e:
        safe_print(f"  -> ERROR: {e}")
        results["reddit"] = {"items": [], "error": str(e)}

    # TikTok
    safe_print("[2/3] TikTok 검색 중...")
    try:
        t = tiktok.search_and_enrich(query, from_date, to_date, depth=depth, token=token)
        safe_print(f"  -> {len(t.get('items', []))}건")
        results["tiktok"] = t
    except Exception as e:
        safe_print(f"  -> ERROR: {e}")
        results["tiktok"] = {"items": [], "error": str(e)}

    # Instagram
    safe_print("[3/3] Instagram 검색 중...")
    try:
        ig = instagram.search_and_enrich(query, from_date, to_date, depth=depth, token=token)
        safe_print(f"  -> {len(ig.get('items', []))}건")
        results["instagram"] = ig
    except Exception as e:
        safe_print(f"  -> ERROR: {e}")
        results["instagram"] = {"items": [], "error": str(e)}

    results["elapsed"] = time.time() - start
    safe_print(f"\n총 소요 시간: {results['elapsed']:.1f}초")
    return results


def search_and_save(query: str, depth: str = "quick",
                    output_dir: Optional[str] = None) -> tuple[dict, str]:
    """검색 실행 + MD 파일 저장. Returns (results, md_path)."""
    from pathlib import Path

    results = search(query, depth)

    md = build_markdown(
        query,
        results["reddit"],
        results["tiktok"],
        results["instagram"],
        depth,
        results["elapsed"],
    )

    if output_dir:
        out = Path(output_dir)
    else:
        from ..config import RUNS_DIR
        out = RUNS_DIR
    out.mkdir(parents=True, exist_ok=True)

    md_path = str(out / "search_results.md")
    Path(md_path).write_text(md, encoding="utf-8")
    safe_print(f"\n결과 저장: {md_path}")

    return results, md_path
