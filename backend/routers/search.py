"""POST /api/search — ScrapeCreators 검색."""

import json
import os
from fastapi import APIRouter, HTTPException

from sns_card_factory.search.runner import search_and_save
from sns_card_factory.manifest import create_run, update_stage, run_dir
from backend.models import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def api_search(req: SearchRequest):
    """자연어 검색 실행. 5-90초 소요."""
    try:
        manifest = create_run(req.query, req.depth)
        run_id = manifest["run_id"]
        out = str(run_dir(run_id))

        results, md_path = search_and_save(req.query, req.depth, output_dir=out)

        # JSON 저장
        json_path = os.path.join(out, "search_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        counts = {
            "reddit": len(results.get("reddit", {}).get("items", [])),
            "tiktok": len(results.get("tiktok", {}).get("items", [])),
            "instagram": len(results.get("instagram", {}).get("items", [])),
        }
        update_stage(run_id, "search", {"status": "done", "counts": counts})

        return SearchResponse(run_id=run_id, counts=counts)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
