"""POST /api/process/{run_id} — SSE 진행률 스트리밍."""

import asyncio
import json
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models import ProcessRequest
from backend.services.pipeline import process_pipeline

router = APIRouter()


@router.post("/process/{run_id}")
async def api_process(run_id: str, req: ProcessRequest):
    """파이프라인 실행 + SSE 진행률 스트리밍."""

    async def event_stream():
        try:
            async for event in process_pipeline(run_id, req.select, req.skip_images):
                data = json.dumps(event, ensure_ascii=False)
                yield f"data: {data}\n\n"
        except FileNotFoundError as e:
            yield f"data: {json.dumps({'phase': 'error', 'message': str(e)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'phase': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
