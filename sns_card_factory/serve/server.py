"""로컬 HTTP 서버 — Figma MCP 캡처용."""

import os
import subprocess
import sys
from ..config import DEFAULT_PORT


def start_server(directory: str, port: int = DEFAULT_PORT):
    """포그라운드에서 로컬 서버 시작."""
    print(f"\nServing {directory} on http://localhost:{port}")
    print("Ctrl+C to stop\n")
    os.chdir(directory)
    subprocess.run([sys.executable, "-m", "http.server", str(port)])


def start_server_background(directory: str, port: int = DEFAULT_PORT) -> subprocess.Popen:
    """백그라운드에서 로컬 서버 시작."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Server started on http://localhost:{port} (PID: {proc.pid})")
    return proc
