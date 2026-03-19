"""Figma MCP 캡처 — 개별 카드 HTML을 Figma 프레임으로 삽입.

로컬 서버를 띄우고, 각 카드 HTML을 Figma capture script가 포함된 URL로 열어
Figma MCP가 자동 캡처하도록 합니다.

NOTE: 이 모듈은 CLI에서 직접 호출됩니다. 실제 Figma MCP 호출은
Claude Code의 Figma MCP 도구를 통해 수행되므로, 이 스크립트는
서버 기동 + 브라우저 열기만 담당합니다.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

from ..config import DEFAULT_PORT, DEFAULT_FIGMA_FILE_KEY


def capture_cards_to_figma(
    post_dir: str,
    port: int = DEFAULT_PORT,
    file_key: str = DEFAULT_FIGMA_FILE_KEY,
    card_prefix: str = "card",
) -> dict:
    """카드 HTML 파일들을 Figma에 캡처하기 위한 서버 기동 + URL 출력.

    Args:
        post_dir: 카드 파일이 있는 디렉토리
        port: 로컬 서버 포트
        file_key: Figma 파일 키
        card_prefix: 카드 HTML 파일 접두사

    Returns:
        {
            "server_pid": int,
            "card_urls": [...],
            "gallery_url": str,
            "figma_file_key": str,
            "instructions": str,
        }
    """
    post_path = Path(post_dir)

    # Find card HTML files
    card_htmls = sorted(post_path.glob(f"{card_prefix}_*.html"))
    card_htmls = [f for f in card_htmls if "gallery" not in f.name]

    if not card_htmls:
        raise FileNotFoundError(f"No card HTML files found in {post_dir}")

    # Start local server in background
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=str(post_path),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)  # Wait for server to start

    print(f"\n[Figma Capture] Server started on http://localhost:{port} (PID: {server_proc.pid})")
    print(f"[Figma Capture] Figma File: {file_key}")
    print(f"[Figma Capture] Cards: {len(card_htmls)}장\n")

    # Build URLs
    base_url = f"http://localhost:{port}"
    card_urls = []
    for html_file in card_htmls:
        url = f"{base_url}/{html_file.name}"
        card_urls.append(url)
        print(f"  {html_file.name} → {url}")

    gallery_url = f"{base_url}/card_gallery.html"
    print(f"\n  Gallery → {gallery_url}")

    # Open gallery in browser for manual Figma capture
    print(f"\n[Figma Capture] Opening gallery in browser...")
    if sys.platform == "win32":
        os.system(f'start "" "{gallery_url}"')
    elif sys.platform == "darwin":
        os.system(f'open "{gallery_url}"')
    else:
        os.system(f'xdg-open "{gallery_url}"')

    result = {
        "server_pid": server_proc.pid,
        "server_proc": server_proc,
        "card_urls": card_urls,
        "gallery_url": gallery_url,
        "figma_file_key": file_key,
        "card_count": len(card_htmls),
        "port": port,
    }

    print(f"\n[Figma Capture] 서버가 실행 중입니다.")
    print(f"[Figma Capture] Claude Code에서 Figma MCP로 캡처하거나,")
    print(f"[Figma Capture] 브라우저의 캡처 툴바를 사용하세요.")
    print(f"[Figma Capture] 완료 후 Ctrl+C로 서버를 종료하세요.\n")

    return result


def stop_server(server_proc: subprocess.Popen):
    """서버 프로세스 종료."""
    try:
        server_proc.terminate()
        server_proc.wait(timeout=5)
        print("[Figma Capture] Server stopped.")
    except Exception:
        server_proc.kill()
