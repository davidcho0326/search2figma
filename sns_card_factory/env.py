"""통합 .env 로딩 — UTF-8 인코딩, 3-location priority."""

import os
from pathlib import Path
from typing import Dict


def load_env_file(path: Path) -> Dict[str, str]:
    """Parse a single .env file (UTF-8) and return key-value pairs."""
    env: Dict[str, str] = {}
    if not path or not path.exists():
        return env
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip()
                    if value and value[0] in ('"', "'") and value[-1] == value[0]:
                        value = value[1:-1]
                    if key and value:
                        env[key] = value
    except Exception:
        pass
    return env


def load_env() -> Dict[str, str]:
    """Load API keys from .env files (priority: project > last30days > global).

    Returns the merged dict and also sets os.environ (setdefault).
    """
    from .config import PROJECT_ROOT

    env_locations = [
        Path.home() / ".config" / "last30days" / ".env",   # global
        Path("c:/python/venv") / ".env",                     # venv root
        Path("c:/python/venv/last30days") / ".env",         # last30days
        PROJECT_ROOT / ".env",                               # project (highest)
    ]

    merged: Dict[str, str] = {}
    for loc in env_locations:
        merged.update(load_env_file(loc))

    for key, value in merged.items():
        os.environ.setdefault(key, value)

    return merged


def ensure_utf8_console():
    """Windows 콘솔 UTF-8 강제 설정 — 프로젝트 진입점에서 1회 호출."""
    import sys
    import io
    if sys.platform == "win32":
        for stream_name in ("stdout", "stderr"):
            stream = getattr(sys, stream_name)
            if hasattr(stream, "buffer"):
                setattr(sys, stream_name,
                        io.TextIOWrapper(stream.buffer, encoding="utf-8",
                                         errors="replace", line_buffering=True))
