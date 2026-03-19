"""GET /api/runs/{run_id}/posts/{post_id}/images/{filename} — 정적 파일 서빙."""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from sns_card_factory.manifest import run_dir

router = APIRouter()


@router.get("/runs/{run_id}/posts/{post_id}/images/{filename}")
def api_serve_file(run_id: str, post_id: str, filename: str):
    """생성된 이미지/HTML 파일 서빙."""
    rd = str(run_dir(run_id))
    file_path = os.path.join(rd, "posts", post_id, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    # Content-type 추론
    if filename.endswith(".png"):
        media_type = "image/png"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif filename.endswith(".html"):
        media_type = "text/html"
    elif filename.endswith(".json"):
        media_type = "application/json"
    elif filename.endswith(".mp4"):
        media_type = "video/mp4"
    else:
        media_type = "application/octet-stream"

    return FileResponse(file_path, media_type=media_type)
