"""Pydantic 스키마 — API 요청/응답 모델."""

from typing import Literal, Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    depth: Literal["quick", "default", "deep"] = "quick"


class SearchResponse(BaseModel):
    run_id: str
    counts: dict


class ProcessRequest(BaseModel):
    select: str = "auto"
    skip_images: bool = False


class PostSummary(BaseModel):
    id: str
    platform: str
    title: str
    url: str
    engagement: dict
    has_output: bool = False


class RunSummary(BaseModel):
    run_id: str
    query: str
    created_at: str
    depth: str = "quick"
    stages: dict = {}


class RunDetail(RunSummary):
    posts: list[PostSummary] = []


class CardInfo(BaseModel):
    role: str
    index: int
    image_url: str
    html_url: str


class PostDetail(BaseModel):
    id: str
    platform: str
    title: str
    url: str
    analysis: Optional[dict] = None
    content: Optional[dict] = None
    cards: list[CardInfo] = []
    gallery_url: Optional[str] = None


class ProgressEvent(BaseModel):
    phase: str
    post: Optional[str] = None
    slide: Optional[int] = None
    progress: int = 0
    message: str = ""


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    runs_count: int = 0
