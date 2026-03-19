"""5종 역할별 HTML 카드 생성 + gallery (OUTPUT_DIR 파라미터화)."""

import os
from ..utils import hex_to_rgba
from ..config import (
    CARD_WIDTH, CARD_HEIGHT, FONT_FAMILY, FONT_HANDWRITING,
    COLOR_ACCENT, COLOR_WHITE, COLOR_DARK_BG, TEXT_SHADOW,
)

COMMON_HEAD = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width={CARD_WIDTH}">
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@font-face {{
  font-family: 'Ownglyph_wiseelist';
  src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/2405-2@1.0/Ownglyph_wiseelist-Rg.woff2') format('woff2');
  font-weight: normal;
  font-display: swap;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; overflow: hidden; font-family: {FONT_FAMILY}; }}
div {{ word-break: keep-all; overflow-wrap: break-word; }}
</style>
<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>
</head>"""


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _highlight_in_text(text: str, highlight_word: str) -> str:
    if not highlight_word or highlight_word not in text:
        return _escape(text)
    parts = text.split(highlight_word, 1)
    return f"{_escape(parts[0])}<span class='hl'>{_escape(highlight_word)}</span>{_escape(parts[1])}"


def generate_hook_html(slide: dict, image_filename: str) -> str:
    title = slide.get("title", "")
    highlight = slide.get("highlight_word", "")
    rotation = slide.get("highlight_rotation", 0)
    bottom = slide.get("bottom_text", "")

    return f"""{COMMON_HEAD}
<body>
<div style="position: relative; width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; background: #000; overflow: hidden;">
  <img src="{image_filename}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; mix-blend-mode: multiply;" />
  <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(ellipse at center, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.7) 100%);"></div>
  <div style="position: absolute; top: 120px; left: 80px; right: 80px; font-weight: 400; font-size: 91px; line-height: 1.15; color: {COLOR_WHITE}; text-align: center; text-shadow: {TEXT_SHADOW};">{_escape(title)}</div>
  <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) {f'rotate({rotation}deg)' if rotation else ''}; font-weight: 900; font-size: 153px; color: {COLOR_ACCENT}; text-shadow: 3px 3px 12px rgba(0,0,0,0.6);">{_escape(highlight)}</div>
  <div style="position: absolute; bottom: 100px; left: 80px; right: 80px; font-weight: 500; font-size: 45px; color: {COLOR_ACCENT}; text-align: center; text-shadow: {TEXT_SHADOW};">{_escape(bottom)}</div>
</div>
</body></html>"""


def generate_problem_html(slide: dict, image_filename: str) -> str:
    title = slide.get("title", "")
    highlight = slide.get("highlight_word", "")
    bottom = slide.get("bottom_text", "")

    return f"""{COMMON_HEAD}
<body>
<div style="position: relative; width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; background: #000; overflow: hidden;">
  <img src="{image_filename}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" />
  <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.6) 60%, rgba(0,0,0,0.85) 100%);"></div>
  <div style="position: absolute; top: 76px; left: 80px; font-weight: 900; font-size: 50px; color: {COLOR_ACCENT}; letter-spacing: -1px; z-index: 2;">In10T</div>
  <div style="position: absolute; top: 200px; left: 80px; right: 80px; font-weight: 500; font-size: 68px; line-height: 1.25; color: {COLOR_WHITE}; text-shadow: {TEXT_SHADOW};">{_highlight_in_text(title, highlight)}</div>
  <div style="position: absolute; bottom: 100px; left: 80px; right: 80px; font-weight: 500; font-size: 45px; line-height: 1.5; color: {COLOR_WHITE}; text-shadow: {TEXT_SHADOW};">{_escape(bottom)}</div>
</div>
<style>.hl {{ font-weight: 900; color: {COLOR_ACCENT}; }}</style>
</body></html>"""


def generate_concept_html(slide: dict, image_filename: str) -> str:
    title = slide.get("title", "")
    subtitle = slide.get("subtitle", "")
    bottom = slide.get("bottom_text", "")

    return f"""{COMMON_HEAD}
<body>
<div style="position: relative; width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; background: #000; overflow: hidden;">
  <img src="{image_filename}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" />
  <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.88) 60%, rgba(0,0,0,0.95) 100%);"></div>
  <div style="position: absolute; top: 180px; left: 80px; right: 80px; font-weight: 800; font-size: 86px; color: {COLOR_ACCENT}; text-align: center; text-shadow: {TEXT_SHADOW};">{_escape(title)}</div>
  <div style="position: absolute; top: 310px; left: 80px; right: 80px; font-weight: 800; font-size: 62px; color: {COLOR_WHITE}; text-align: center; text-shadow: {TEXT_SHADOW};">{_escape(subtitle)}</div>
  <div style="position: absolute; bottom: 100px; left: 80px; right: 80px; font-weight: 600; font-size: 45px; line-height: 1.5; color: {COLOR_WHITE}; text-align: center; text-shadow: {TEXT_SHADOW};">{_escape(bottom)}</div>
</div>
</body></html>"""


def generate_explain_html(slide: dict, image_filename: str) -> str:
    title = slide.get("title", "")
    highlight = slide.get("highlight_word", "")
    annotation = slide.get("annotation_text", "")

    return f"""{COMMON_HEAD}
<body>
<div style="position: relative; width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; background: {COLOR_DARK_BG}; overflow: hidden;">
  <img src="{image_filename}" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); max-width: 85%; max-height: 65%; object-fit: contain;" />
  <div style="position: absolute; top: 100px; left: 80px; right: 80px; font-weight: 800; font-size: 86px; color: {COLOR_WHITE}; text-align: center; text-shadow: {TEXT_SHADOW};">{_highlight_in_text(title, highlight)}</div>
  <div style="position: absolute; bottom: 120px; left: 80px; right: 80px; font-family: {FONT_HANDWRITING}; font-size: 63px; color: {COLOR_WHITE}; text-align: center; text-shadow: {TEXT_SHADOW}; opacity: 0.9;">{_escape(annotation)}</div>
</div>
<style>.hl {{ color: {COLOR_ACCENT}; }}</style>
</body></html>"""


def generate_conclusion_html(slide: dict, image_filename: str) -> str:
    title = slide.get("title", "")
    highlight = slide.get("highlight_word", "")
    bottom = slide.get("bottom_text", "")

    return f"""{COMMON_HEAD}
<body>
<div style="position: relative; width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; background: #000; overflow: hidden;">
  <img src="{image_filename}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" />
  <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.6) 100%);"></div>
  <div style="position: absolute; top: 140px; left: 80px; right: 80px; font-weight: 800; font-size: 62px; line-height: 1.35; color: {COLOR_WHITE}; text-align: center; text-shadow: {TEXT_SHADOW};">{_highlight_in_text(title, highlight)}</div>
  {"" if not bottom else f'<div style="position: absolute; bottom: 100px; left: 80px; right: 80px; font-weight: 500; font-size: 45px; color: {COLOR_WHITE}; text-align: center; text-shadow: {TEXT_SHADOW};">{_escape(bottom)}</div>'}
</div>
<style>.hl {{ color: {COLOR_ACCENT}; font-weight: 800; }}</style>
</body></html>"""


ROLE_GENERATORS = {
    "hook": generate_hook_html,
    "problem": generate_problem_html,
    "concept": generate_concept_html,
    "explain": generate_explain_html,
    "conclusion": generate_conclusion_html,
}


def generate_slide_html(slide_data: dict, image_filename: str) -> str:
    """슬라이드 역할에 맞는 HTML 생성."""
    role = slide_data.get("role", "hook")
    generator = ROLE_GENERATORS.get(role, generate_hook_html)
    return generator(slide_data, image_filename)


def generate_all_slide_htmls(
    slides: list[dict],
    image_results: list[dict],
    output_dir: str,
    prefix: str = "card",
) -> list[str]:
    """5장 슬라이드 HTML 파일 생성."""
    os.makedirs(output_dir, exist_ok=True)
    html_paths = []

    for i, (slide, img_result) in enumerate(zip(slides, image_results)):
        role = slide.get("role", f"slide{i+1}")
        image_filename = img_result.get("image_filename", f"{prefix}_{i+1}_{role}.png")

        html_content = generate_slide_html(slide, image_filename)
        output_filename = f"{prefix}_{i+1}_{role}.html"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"  [{role}] HTML 생성 완료 → {output_filename}")
        html_paths.append(output_path)

    return html_paths


def generate_gallery_html(
    slides: list[dict],
    image_results: list[dict],
    output_dir: str,
    output_filename: str = "card_gallery.html",
) -> str:
    """5장 가로 배치 갤러리 HTML (Figma 캡처용)."""
    role_labels = {
        "hook": "1. Hook", "problem": "2. Problem",
        "concept": "3. Concept", "explain": "4. Explain",
        "conclusion": "5. Conclusion",
    }

    cards_html = ""
    for i, (slide, img_result) in enumerate(zip(slides, image_results)):
        role = slide.get("role", f"slide{i+1}")
        image_filename = img_result.get("image_filename", "")
        label = role_labels.get(role, f"Slide {i+1}")
        title = _escape(slide.get("title", ""))
        bottom = _escape(slide.get("bottom_text", ""))

        cards_html += f"""
    <div style="flex-shrink: 0; text-align: center;">
      <div style="font-weight: 700; font-size: 28px; color: #fff; margin-bottom: 16px; font-family: 'Pretendard', sans-serif;">{label}</div>
      <div style="position: relative; width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; border: 2px solid rgba(255,255,255,0.15); border-radius: 12px; overflow: hidden; background: #000;">
        <img src="{image_filename}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" />
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.7) 100%);"></div>
        <div style="position: absolute; top: 100px; left: 60px; right: 60px; font-weight: 800; font-size: 56px; color: {COLOR_ACCENT}; text-align: center; text-shadow: {TEXT_SHADOW};">{title}</div>
        <div style="position: absolute; bottom: 80px; left: 60px; right: 60px; font-weight: 500; font-size: 36px; color: {COLOR_WHITE}; text-align: center; text-shadow: {TEXT_SHADOW};">{bottom}</div>
      </div>
    </div>"""

    total_width = (CARD_WIDTH + 40) * 5 + 80
    gallery_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width={total_width}">
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #1a1a2e; width: {total_width}px; }}
</style>
<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>
</head>
<body>
<div style="display: flex; gap: 40px; padding: 40px; width: {total_width}px; align-items: flex-start;">
{cards_html}
</div>
</body></html>"""

    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(gallery_html)

    print(f"\n[갤러리 HTML 생성 완료] {output_path}")
    return output_path
