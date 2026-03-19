#!/usr/bin/env python3
"""SNS Card News for ThePlay — CLI 진입점.

Usage:
    python cli.py search "검색어" [--depth quick|default|deep]
    python cli.py list <run_id>
    python cli.py process <run_id> --select IG1,IG8
    python cli.py serve <run_id> --post IG1 [--port 8889]
    python cli.py run "검색어" [--select auto|TK1,IG2] [--depth quick]
    python cli.py runs
"""

import argparse
import json
import sys
import os

# UTF-8 콘솔 설정 + .env 로딩 (Windows)
from sns_card_factory.env import ensure_utf8_console, load_env
ensure_utf8_console()
load_env()


def cmd_search(args):
    """Stage 1: ScrapeCreators 검색."""
    from sns_card_factory.search.runner import search_and_save
    from sns_card_factory.manifest import create_run, update_stage, run_dir

    manifest = create_run(args.query, args.depth)
    run_id = manifest["run_id"]
    out = str(run_dir(run_id))

    print(f"Run ID: {run_id}")
    print(f"Output: {out}\n")

    results, md_path = search_and_save(args.query, args.depth, output_dir=out)

    # Save structured JSON too
    json_path = os.path.join(out, "search_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    counts = {
        "reddit": len(results.get("reddit", {}).get("items", [])),
        "tiktok": len(results.get("tiktok", {}).get("items", [])),
        "instagram": len(results.get("instagram", {}).get("items", [])),
    }
    update_stage(run_id, "search", {"status": "done", "counts": counts})

    print(f"\nRun ID: {run_id}")
    print(f"다음 단계: python cli.py list {run_id}")


def cmd_list(args):
    """Stage 2: 검색 결과 목록 표시."""
    from sns_card_factory.select.parser import parse_search_results
    from sns_card_factory.select.selector import print_items_table
    from sns_card_factory.manifest import run_dir

    md_path = os.path.join(str(run_dir(args.run_id)), "search_results.md")
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found")
        sys.exit(1)

    items = parse_search_results(md_path)
    print_items_table(items)
    print(f"Total: {len(items)} items")
    print(f"\n다음 단계: python cli.py process {args.run_id} --select IG1,IG2")


def cmd_process(args):
    """Stage 3-5: 다운로드 → 분석 → 카드뉴스 생성."""
    from sns_card_factory.select.parser import parse_search_results
    from sns_card_factory.select.selector import select_by_ids, select_auto, print_items_table
    from sns_card_factory.download.downloader import download_content
    from sns_card_factory.analyze.analyzer import analyze_content
    from sns_card_factory.cardnews.content_gen import generate_from_analysis, save_content_json
    from sns_card_factory.cardnews.image_gen import generate_all_slide_images
    from sns_card_factory.cardnews.html_gen import generate_all_slide_htmls, generate_gallery_html
    from sns_card_factory.manifest import run_dir, post_dir, update_stage

    rd = str(run_dir(args.run_id))
    md_path = os.path.join(rd, "search_results.md")
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found. Run 'search' first.")
        sys.exit(1)

    items = parse_search_results(md_path)
    print_items_table(items)

    # Select posts
    if args.select == "auto":
        selected = select_auto(items)
    else:
        selected = select_by_ids(items, args.select)

    if not selected:
        print("No posts selected.")
        sys.exit(1)

    print(f"Selected {len(selected)} post(s): {', '.join(p['id'] for p in selected)}\n")

    for post in selected:
        pid = post["id"]
        pd = str(post_dir(args.run_id, pid))

        print(f"\n{'='*60}")
        print(f"Processing: {pid} ({post['platform']}) - {post['title'][:50]}")
        print(f"URL: {post['url']}")
        print(f"Output: {pd}")
        print(f"{'='*60}")

        # Phase 2: Download
        print(f"\n[Phase 2] Downloading content...")
        dl_result = download_content(post, pd)

        # Phase 3: Analyze
        print(f"\n[Phase 3] Analyzing with Gemini...")
        analysis = analyze_content(dl_result)
        analysis_path = os.path.join(pd, "analysis.json")
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"  -> Analysis saved: {analysis_path}")

        print(f"\n  Core Topic: {analysis.get('core_topic', '?')}")
        print(f"  Tone: {analysis.get('emotional_tone', '?')}")
        print(f"  Angle: {analysis.get('card_news_angle', '?')}")

        # Phase 4: Generate carousel content
        print(f"\n[Phase 4] Generating carousel content (5 slides)...")
        content = generate_from_analysis(analysis, dl_result.get("thumb_path"))
        content_path = os.path.join(pd, "content.json")
        save_content_json(content, content_path)

        slides = content["slides"]
        for s in slides:
            print(f"  [{s['role']}] {s.get('title', '')}")

        # Phase 5: Generate images
        if not args.skip_images:
            print(f"\n[Phase 5] Generating 5 card images...")
            ref_image = dl_result.get("thumb_path") or dl_result.get("media_path")
            if ref_image:
                image_results = generate_all_slide_images(ref_image, slides, pd)
            else:
                print("  [WARN] No reference image, skipping image generation")
                image_results = [
                    {"role": s["role"], "index": i+1, "image_filename": f"card_{i+1}_{s['role']}.png", "success": False}
                    for i, s in enumerate(slides)
                ]
        else:
            print(f"\n[Phase 5] Skipping image generation (--skip-images)")
            image_results = [
                {"role": s["role"], "index": i+1, "image_filename": f"card_{i+1}_{s['role']}.png", "success": False}
                for i, s in enumerate(slides)
            ]

        # Phase 6: Generate HTML
        print(f"\n[Phase 6] Generating 5 card HTMLs + gallery...")
        generate_all_slide_htmls(slides, image_results, pd)
        generate_gallery_html(slides, image_results, pd)

        success_count = sum(1 for r in image_results if r.get("success"))
        print(f"\n{'='*60}")
        print(f"DONE: {pid}")
        print(f"  Images: {success_count}/5 generated")
        print(f"  HTMLs: 5 cards")
        print(f"  Gallery: {os.path.join(pd, 'card_gallery.html')}")
        print(f"  Output: {pd}")
        print(f"{'='*60}")

    update_stage(args.run_id, "process", {
        "status": "done",
        "selected": [p["id"] for p in selected],
    })

    print(f"\n다음 단계: python cli.py serve {args.run_id} --post {selected[0]['id']}")


def cmd_serve(args):
    """Stage 6: 로컬 서버 기동 (Figma 캡처용)."""
    from sns_card_factory.serve.server import start_server
    from sns_card_factory.manifest import post_dir

    pd = str(post_dir(args.run_id, args.post))
    if not os.path.exists(pd):
        print(f"Error: {pd} not found")
        sys.exit(1)

    start_server(pd, args.port)


def cmd_run(args):
    """원스텝 전체 실행: search → select → process."""
    # Reuse search
    args_search = argparse.Namespace(query=args.query, depth=args.depth)
    cmd_search(args_search)

    # Get the latest run_id
    from sns_card_factory.manifest import list_runs
    runs = list_runs()
    if not runs:
        print("Error: No runs found")
        sys.exit(1)

    run_id = runs[0]["run_id"]

    # Process
    args_process = argparse.Namespace(
        run_id=run_id,
        select=args.select,
        skip_images=args.skip_images,
    )
    cmd_process(args_process)


def cmd_capture(args):
    """Stage 7: Figma MCP 캡처 — 카드 HTML → Figma 프레임."""
    from sns_card_factory.serve.figma_capture import capture_cards_to_figma, stop_server
    from sns_card_factory.manifest import post_dir

    pd = str(post_dir(args.run_id, args.post))
    if not os.path.exists(pd):
        print(f"Error: {pd} not found")
        sys.exit(1)

    result = capture_cards_to_figma(
        post_dir=pd,
        port=args.port,
        file_key=args.file_key,
    )

    # Keep server alive until Ctrl+C
    try:
        result["server_proc"].wait()
    except KeyboardInterrupt:
        stop_server(result["server_proc"])


def cmd_runs(args):
    """모든 런 목록."""
    from sns_card_factory.manifest import list_runs

    runs = list_runs()
    if not runs:
        print("No runs found.")
        return

    print(f"\n{'Run ID':<40} {'Query':<30} {'Created'}")
    print("-" * 90)
    for r in runs:
        print(f"{r['run_id']:<40} {r['query'][:28]:<30} {r.get('created_at', '?')[:19]}")
    print(f"\nTotal: {len(runs)} run(s)")


def main():
    parser = argparse.ArgumentParser(description="SNS Card News for ThePlay")
    sub = parser.add_subparsers(dest="command")

    # search
    p_search = sub.add_parser("search", help="ScrapeCreators 검색")
    p_search.add_argument("query", help="검색어")
    p_search.add_argument("--depth", default="quick", choices=["quick", "default", "deep"])

    # list
    p_list = sub.add_parser("list", help="검색 결과 목록")
    p_list.add_argument("run_id", help="Run ID")

    # process
    p_proc = sub.add_parser("process", help="다운로드+분석+카드뉴스")
    p_proc.add_argument("run_id", help="Run ID")
    p_proc.add_argument("--select", required=True, help="ID (IG1,TK2) 또는 auto")
    p_proc.add_argument("--skip-images", action="store_true")

    # serve
    p_serve = sub.add_parser("serve", help="로컬 서버 기동")
    p_serve.add_argument("run_id", help="Run ID")
    p_serve.add_argument("--post", required=True, help="Post ID (IG1)")
    p_serve.add_argument("--port", type=int, default=8889)

    # capture (Figma)
    p_cap = sub.add_parser("capture", help="Figma MCP 캡처")
    p_cap.add_argument("run_id", help="Run ID")
    p_cap.add_argument("--post", required=True, help="Post ID (IG1)")
    p_cap.add_argument("--port", type=int, default=8889)
    p_cap.add_argument("--file-key", default="inuxM4oZWXoyPY9kqqUpPl", help="Figma file key")

    # run (end-to-end)
    p_run = sub.add_parser("run", help="전체 파이프라인")
    p_run.add_argument("query", help="검색어")
    p_run.add_argument("--select", default="auto")
    p_run.add_argument("--depth", default="quick", choices=["quick", "default", "deep"])
    p_run.add_argument("--skip-images", action="store_true")

    # runs
    sub.add_parser("runs", help="런 목록")

    args = parser.parse_args()

    commands = {
        "search": cmd_search,
        "list": cmd_list,
        "process": cmd_process,
        "serve": cmd_serve,
        "capture": cmd_capture,
        "run": cmd_run,
        "runs": cmd_runs,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
