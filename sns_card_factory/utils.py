"""공통 유틸리티 — 여러 모듈에서 중복되던 헬퍼를 한 곳에 모음."""

import json
import re
import sys


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """'#FFD03C' → 'rgba(255, 208, 60, 1.0)'"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def fmt_number(n) -> str:
    """숫자를 읽기 쉬운 형태로: 1234567 → '1.2M', 45000 → '45.0K'"""
    try:
        n = int(n)
    except (ValueError, TypeError):
        return str(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def safe_print(text: str, end: str = "\n"):
    """UnicodeEncodeError 방지 출력."""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode("utf-8", errors="replace").decode("utf-8"), end=end)


def parse_json_response(text: str) -> dict:
    """Gemini 응답에서 JSON 추출 (```json 블록 등 처리)."""
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = cleaned.strip()

    # Try to find JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(cleaned[start:end])
        except json.JSONDecodeError:
            pass

    # Fallback: try the whole string
    return json.loads(cleaned)
