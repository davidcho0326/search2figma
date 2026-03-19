"""SSE 파이프라인 — cmd_process를 async generator로 래핑."""

import asyncio
import json
import os
from typing import AsyncGenerator

from sns_card_factory.manifest import run_dir, post_dir, load, update_stage
from sns_card_factory.select.parser import parse_search_results
from sns_card_factory.select.selector import select_by_ids, select_auto
from sns_card_factory.download.downloader import download_content
from sns_card_factory.analyze.analyzer import analyze_content
from sns_card_factory.cardnews.content_gen import generate_from_analysis, save_content_json
from sns_card_factory.cardnews.image_gen import generate_slide_image
from sns_card_factory.cardnews.html_gen import generate_all_slide_htmls, generate_gallery_html


async def process_pipeline(
    run_id: str,
    select: str = "auto",
    skip_images: bool = False,
) -> AsyncGenerator[dict, None]:
    """파이프라인 실행 + 단계별 SSE 이벤트 yield."""

    rd = str(run_dir(run_id))
    md_path = os.path.join(rd, "search_results.md")
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"Run {run_id} not found or search not completed")

    # Parse & select
    items = await asyncio.to_thread(parse_search_results, md_path)

    if select == "auto":
        selected = select_auto(items)
    else:
        selected = select_by_ids(items, select)

    if not selected:
        yield {"phase": "error", "progress": 0, "message": "No posts selected"}
        return

    post_ids = [p["id"] for p in selected]
    yield {
        "phase": "select",
        "progress": 5,
        "message": f"Selected {len(selected)} post(s): {', '.join(post_ids)}",
    }

    total_posts = len(selected)
    for idx, post in enumerate(selected):
        pid = post["id"]
        pd = str(post_dir(run_id, pid))
        base_progress = int((idx / total_posts) * 90) + 5  # 5-95 range

        # Phase: Download
        yield {
            "phase": "download",
            "post": pid,
            "progress": base_progress + 5,
            "message": f"[{pid}] Downloading {post['platform']} content...",
        }
        dl_result = await asyncio.to_thread(download_content, post, pd)

        # Phase: Analyze
        yield {
            "phase": "analyze",
            "post": pid,
            "progress": base_progress + 15,
            "message": f"[{pid}] Analyzing with Gemini...",
        }
        analysis = await asyncio.to_thread(analyze_content, dl_result)

        # Save analysis
        analysis_path = os.path.join(pd, "analysis.json")
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        yield {
            "phase": "analyze_done",
            "post": pid,
            "progress": base_progress + 25,
            "message": f"[{pid}] Core: {analysis.get('core_topic', '?')[:50]}",
        }

        # Phase: Content generation
        yield {
            "phase": "content",
            "post": pid,
            "progress": base_progress + 30,
            "message": f"[{pid}] Generating 5-slide content...",
        }
        content = await asyncio.to_thread(
            generate_from_analysis, analysis, dl_result.get("thumb_path")
        )
        content_path = os.path.join(pd, "content.json")
        save_content_json(content, content_path)

        slides = content["slides"]
        for s in slides:
            yield {
                "phase": "content_slide",
                "post": pid,
                "progress": base_progress + 35,
                "message": f"  [{s['role']}] {s.get('title', '')[:30]}",
            }

        # Phase: Image generation (per-slide)
        image_results = []
        if not skip_images:
            ref_image = dl_result.get("thumb_path") or dl_result.get("media_path")
            if ref_image:
                for i, slide in enumerate(slides):
                    role = slide.get("role", f"slide{i+1}")
                    filename = f"card_{i+1}_{role}.png"
                    output_path = os.path.join(pd, filename)

                    img_progress = base_progress + 40 + int((i / 5) * 30)
                    yield {
                        "phase": "images",
                        "post": pid,
                        "slide": i + 1,
                        "progress": img_progress,
                        "message": f"[{pid}] Generating image {i+1}/5 ({role})...",
                    }

                    try:
                        await asyncio.to_thread(
                            generate_slide_image, ref_image, slide, output_path
                        )
                        image_results.append({
                            "role": role, "index": i + 1,
                            "image_filename": filename, "success": True,
                        })
                    except Exception as e:
                        image_results.append({
                            "role": role, "index": i + 1,
                            "image_filename": filename, "success": False,
                            "error": str(e),
                        })
            else:
                image_results = [
                    {"role": s["role"], "index": i+1,
                     "image_filename": f"card_{i+1}_{s['role']}.png", "success": False}
                    for i, s in enumerate(slides)
                ]
        else:
            image_results = [
                {"role": s["role"], "index": i+1,
                 "image_filename": f"card_{i+1}_{s['role']}.png", "success": False}
                for i, s in enumerate(slides)
            ]

        # Phase: HTML generation
        yield {
            "phase": "html",
            "post": pid,
            "progress": base_progress + 75,
            "message": f"[{pid}] Generating HTML cards + gallery...",
        }
        await asyncio.to_thread(generate_all_slide_htmls, slides, image_results, pd)
        await asyncio.to_thread(generate_gallery_html, slides, image_results, pd)

        success_count = sum(1 for r in image_results if r.get("success"))
        yield {
            "phase": "done",
            "post": pid,
            "progress": base_progress + 85,
            "message": f"[{pid}] Complete — {success_count}/5 images, 5 HTMLs",
        }

    # Update manifest
    update_stage(run_id, "process", {
        "status": "done",
        "selected": post_ids,
    })

    yield {
        "phase": "all_done",
        "progress": 100,
        "message": f"All {total_posts} post(s) processed successfully",
    }
