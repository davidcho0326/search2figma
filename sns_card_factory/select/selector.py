"""게시물 선택 — ID 기반 필터링 + 테이블 출력."""

import re
from typing import List, Dict

from ..utils import safe_print


def print_items_table(items: List[Dict]):
    """게시물 목록을 테이블로 출력."""
    safe_print(f"\n{'ID':<6} {'플랫폼':<12} {'제목 (50자)':<52} {'주요 지표'}")
    safe_print("-" * 110)
    for item in items:
        raw_title = item["title"].encode("ascii", errors="ignore").decode("ascii")
        title = raw_title[:50] + ("..." if len(raw_title) > 50 else "")
        eng = item["engagement"]

        metrics = []
        if eng.get("views"):
            metrics.append(f"조회 {eng['views']}")
        if eng.get("upvotes"):
            metrics.append(f"UP {eng['upvotes']}")
        if eng.get("likes"):
            metrics.append(f"좋아요 {eng['likes']}")
        if eng.get("comments"):
            metrics.append(f"댓글 {eng['comments']}")

        metric_str = " | ".join(metrics) if metrics else "-"
        safe_print(f"{item['id']:<6} {item['platform']:<12} {title:<52} {metric_str}")

    print()


def select_by_ids(items: List[Dict], id_string: str) -> List[Dict]:
    """ID 문자열로 게시물 필터링. 예: 'TK1,IG3' 또는 'TK1 IG3'"""
    ids = [x.strip().upper() for x in re.split(r"[,\s]+", id_string) if x.strip()]
    item_map = {item["id"].upper(): item for item in items}
    selected = []
    for id_ in ids:
        if id_ in item_map:
            selected.append(item_map[id_])
        else:
            print(f"  [WARN] ID '{id_}' not found, skipping")
    return selected


def select_auto(items: List[Dict], n: int = 3) -> List[Dict]:
    """Relevance score 기준 상위 N건 자동 선택."""
    def _score(item):
        try:
            rel = item["engagement"].get("relevance", "0")
            return float(rel.replace("**", "").strip())
        except (ValueError, AttributeError):
            return 0.0
    return sorted(items, key=_score, reverse=True)[:n]
