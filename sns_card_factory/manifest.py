"""런별 manifest.json 관리 — 미래 UI/DB 마이그레이션 기반."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import RUNS_DIR


def create_run(query: str, depth: str = "quick") -> dict:
    """새 런 생성: 디렉토리 + manifest.json 초기화."""
    now = datetime.now()
    slug = _slugify(query)[:30]
    run_id = f"{now.strftime('%Y%m%d_%H%M%S')}_{slug}"

    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "posts").mkdir(exist_ok=True)

    manifest = {
        "run_id": run_id,
        "query": query,
        "depth": depth,
        "created_at": now.isoformat(),
        "stages": {},
        "output_paths": {},
    }
    _save(run_dir / "manifest.json", manifest)
    return manifest


def update_stage(run_id: str, stage: str, data: dict):
    """특정 스테이지 상태 업데이트."""
    manifest = load(run_id)
    if manifest is None:
        raise FileNotFoundError(f"Run {run_id} not found")
    manifest["stages"][stage] = data
    _save(_run_path(run_id) / "manifest.json", manifest)


def load(run_id: str) -> Optional[dict]:
    """manifest.json 로드."""
    path = _run_path(run_id) / "manifest.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_runs() -> list[dict]:
    """모든 런 목록 (최신순)."""
    if not RUNS_DIR.exists():
        return []
    runs = []
    for d in sorted(RUNS_DIR.iterdir(), reverse=True):
        m = d / "manifest.json"
        if m.exists():
            try:
                with open(m, "r", encoding="utf-8") as f:
                    runs.append(json.load(f))
            except Exception:
                pass
    return runs


def run_dir(run_id: str) -> Path:
    """런 디렉토리 경로."""
    return _run_path(run_id)


def post_dir(run_id: str, post_id: str) -> Path:
    """게시물별 출력 디렉토리."""
    d = _run_path(run_id) / "posts" / post_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── internal ───────────────────────────────────────────────

def _run_path(run_id: str) -> Path:
    return RUNS_DIR / run_id


def _save(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _slugify(text: str) -> str:
    import re
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s]+", "_", text).strip("_")
