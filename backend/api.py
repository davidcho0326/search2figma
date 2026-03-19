"""FastAPI 앱 — SNS Card News Backend."""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가 (sns_card_factory import 가능하게)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sns_card_factory.env import load_env, ensure_utf8_console
from sns_card_factory.manifest import list_runs

ensure_utf8_console()
load_env()

app = FastAPI(
    title="SNS Card News API",
    version="0.1.0",
    description="SNS 콘텐츠 → 카드뉴스 생성 파이프라인 API",
)

# CORS — 모든 origin 허용 (교육/데모용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 라우터 등록
from backend.routers import search, runs, process, files

app.include_router(search.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(process.router, prefix="/api")
app.include_router(files.router, prefix="/api")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "runs_count": len(list_runs()),
    }
