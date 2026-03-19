"""GET /api/runs — 런 목록 및 상세."""

import json
import os
from fastapi import APIRouter, HTTPException

from sns_card_factory.manifest import list_runs, load, run_dir, post_dir
from sns_card_factory.select.parser import parse_search_results
from backend.models import RunSummary, RunDetail, PostSummary, PostDetail, CardInfo

router = APIRouter()


@router.get("/runs", response_model=list[RunSummary])
def api_list_runs():
    """모든 런 목록."""
    runs = list_runs()
    return [
        RunSummary(
            run_id=r["run_id"],
            query=r.get("query", ""),
            created_at=r.get("created_at", ""),
            depth=r.get("depth", "quick"),
            stages=r.get("stages", {}),
        )
        for r in runs
    ]


@router.get("/runs/{run_id}", response_model=RunDetail)
def api_run_detail(run_id: str):
    """런 상세 — 게시물 목록 포함."""
    manifest = load(run_id)
    if not manifest:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    rd = str(run_dir(run_id))
    md_path = os.path.join(rd, "search_results.md")

    posts = []
    if os.path.exists(md_path):
        items = parse_search_results(md_path)
        for item in items:
            pid = item["id"]
            pd = os.path.join(rd, "posts", pid)
            has_output = os.path.exists(os.path.join(pd, "content.json"))
            posts.append(PostSummary(
                id=pid,
                platform=item["platform"],
                title=item.get("title", "")[:100],
                url=item.get("url", ""),
                engagement=item.get("engagement", {}),
                has_output=has_output,
            ))

    return RunDetail(
        run_id=manifest["run_id"],
        query=manifest.get("query", ""),
        created_at=manifest.get("created_at", ""),
        depth=manifest.get("depth", "quick"),
        stages=manifest.get("stages", {}),
        posts=posts,
    )


@router.get("/runs/{run_id}/posts/{post_id}", response_model=PostDetail)
def api_post_detail(run_id: str, post_id: str):
    """게시물 상세 — 분석 결과 + 카드 목록."""
    manifest = load(run_id)
    if not manifest:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    rd = str(run_dir(run_id))
    pd = os.path.join(rd, "posts", post_id)
    if not os.path.exists(pd):
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    # Parse original post info
    md_path = os.path.join(rd, "search_results.md")
    post_info = {"id": post_id, "platform": "unknown", "title": "", "url": ""}
    if os.path.exists(md_path):
        items = parse_search_results(md_path)
        for item in items:
            if item["id"] == post_id:
                post_info = item
                break

    # Load analysis
    analysis = None
    analysis_path = os.path.join(pd, "analysis.json")
    if os.path.exists(analysis_path):
        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)

    # Load content
    content = None
    content_path = os.path.join(pd, "content.json")
    if os.path.exists(content_path):
        with open(content_path, "r", encoding="utf-8") as f:
            content = json.load(f)

    # Build card list
    cards = []
    roles = ["hook", "problem", "concept", "explain", "conclusion"]
    for i, role in enumerate(roles, 1):
        img_file = f"card_{i}_{role}.png"
        html_file = f"card_{i}_{role}.html"
        if os.path.exists(os.path.join(pd, img_file)):
            cards.append(CardInfo(
                role=role,
                index=i,
                image_url=f"/api/runs/{run_id}/posts/{post_id}/images/{img_file}",
                html_url=f"/api/runs/{run_id}/posts/{post_id}/images/{html_file}",
            ))

    gallery_url = None
    if os.path.exists(os.path.join(pd, "card_gallery.html")):
        gallery_url = f"/api/runs/{run_id}/posts/{post_id}/images/card_gallery.html"

    return PostDetail(
        id=post_id,
        platform=post_info.get("platform", "unknown"),
        title=post_info.get("title", "")[:100],
        url=post_info.get("url", ""),
        analysis=analysis,
        content=content,
        cards=cards,
        gallery_url=gallery_url,
    )
