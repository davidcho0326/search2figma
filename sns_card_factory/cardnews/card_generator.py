"""단일 SNS 카드 생성 — 캐릭터 카드 / 텍스트 카드 HTML + 이미지 베리에이션.

migrated from figma_mcp_test/card_generator.py
"""

import os
import base64
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image

from ..config import GEMINI_IMAGE_MODEL, IMAGE_ASPECT_RATIO, IMAGE_SIZE, MAX_RETRIES, RETRY_DELAYS
from ..utils import hex_to_rgba

import time


def generate_character_variation(
    ref_image_path: str,
    variation_prompt: str,
    output_path: str,
    aspect_ratio: str = IMAGE_ASPECT_RATIO,
    image_size: str = IMAGE_SIZE,
) -> str:
    """Gemini Flash Image로 캐릭터 베리에이션 생성.

    Args:
        ref_image_path: 레퍼런스 이미지 경로
        variation_prompt: 변형 프롬프트 (영문 권장)
        output_path: 저장할 전체 파일 경로
        aspect_ratio, image_size: 이미지 설정

    Returns:
        생성된 이미지 파일 경로
    """
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    ref_image = Image.open(ref_image_path)

    print(f"  레퍼런스 이미지: {ref_image.size}")
    print("  Gemini Flash Image 베리에이션 생성 중...")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=[ref_image, variation_prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=image_size,
                    ),
                ),
            )

            for part in response.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    if isinstance(image_bytes, str):
                        image_bytes = base64.b64decode(image_bytes)
                    img = Image.open(BytesIO(image_bytes))
                    img.save(output_path)
                    print(f"  이미지 저장: {os.path.basename(output_path)} ({img.size})")
                    return output_path
                elif part.text:
                    print(f"  모델 응답: {part.text[:100]}")

            last_error = RuntimeError("응답에 이미지 없음")

        except Exception as e:
            last_error = e

        if attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAYS[attempt]
            print(f"  재시도 {attempt+2}/{MAX_RETRIES} ({delay}초 후)...")
            time.sleep(delay)

    raise RuntimeError(f"이미지 생성 실패 ({MAX_RETRIES}회): {last_error}")


def generate_character_card_html(
    image_filename: str,
    highlight_text: str,
    body_lines: list[str],
    output_path: str,
    logo: str = "In10T",
    bg_color: str = "#7B5EA7",
) -> str:
    """캐릭터 카드 HTML 생성 (분석3 스타일).

    Args:
        image_filename: 배경 이미지 파일명 (같은 디렉토리 기준)
        highlight_text: 노란색 하이라이트 텍스트
        body_lines: 본문 텍스트 리스트
        output_path: HTML 저장 경로
        logo: 좌상단 로고 (기본: In10T)
        bg_color: 배경 색상 (기본: #7B5EA7)

    Returns:
        생성된 HTML 파일 경로
    """
    body_html = "\n    ".join(f"<p>{line}</p>" for line in body_lines)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080">
<style>
  @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: 1080px; height: 1350px; overflow: hidden; font-family: 'Pretendard', sans-serif; }}
  .card {{ position: relative; width: 1080px; height: 1350px; background: {bg_color}; overflow: hidden; }}
  .bg-character {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }}
  .overlay {{ position: absolute; bottom: 0; left: 0; width: 100%; height: 500px;
    background: linear-gradient(to bottom, {hex_to_rgba(bg_color, 0)} 0%, {hex_to_rgba(bg_color, 0.85)} 40%, {hex_to_rgba(bg_color, 1)} 70%); }}
  .logo {{ position: absolute; top: 76px; left: 127px; font-weight: 900; font-size: 50px; color: #FFD03C; letter-spacing: -1px; z-index: 2; }}
  .body-text {{ position: absolute; bottom: 90px; left: 119px; width: 942px; font-weight: 600; font-size: 36px; line-height: 63px; color: #fff; z-index: 2; }}
  .body-text .highlight {{ color: #FFD03C; }}
  .arrow-btn {{ position: absolute; bottom: 81px; right: 84px; width: 50px; height: 50px; background: #FFD03C; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 2; }}
  .arrow-btn svg {{ margin-left: 2px; }}
</style>
<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>
</head>
<body>
<div class="card">
  <img class="bg-character" src="{image_filename}" alt="Character" />
  <div class="overlay"></div>
  <div class="logo">{logo}</div>
  <div class="body-text">
    <p class="highlight">{highlight_text}</p>
    {body_html}
  </div>
  <div class="arrow-btn">
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M7 4L13 10L7 16" stroke="#000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  캐릭터 카드 HTML: {os.path.basename(output_path)}")
    return output_path


def generate_text_card_html(
    title: str,
    body_lines: list[str],
    output_path: str,
    tag: str = "저장하고 꺼내보기",
    bold_keywords: list[str] = None,
    bg_color: str = "#FFD03C",
    text_color: str = "#000",
    footer_text: str = "경험을 디자인하다",
) -> str:
    """텍스트 카드 HTML 생성 (2046 스타일).

    Args:
        title: 대제목
        body_lines: 본문 텍스트 리스트 (빈 문자열 = spacer)
        output_path: HTML 저장 경로
        tag: 상단 태그 pill 텍스트
        bold_keywords: 볼드 처리할 키워드 목록
        bg_color: 배경 색상 (기본: #FFD03C)
        text_color: 텍스트 색상
        footer_text: 하단 바 텍스트

    Returns:
        생성된 HTML 파일 경로
    """
    bold_keywords = bold_keywords or []

    def apply_bold(line: str) -> str:
        for kw in bold_keywords:
            line = line.replace(kw, f'<span class="bold">{kw}</span>')
        return line

    body_parts = []
    for line in body_lines:
        if line.strip() == "":
            body_parts.append('<div class="spacer"></div>')
        else:
            body_parts.append(f"<p>{apply_bold(line)}</p>")
    body_html = "\n    ".join(body_parts)

    footer_bg = "#000"
    footer_fg = bg_color

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080">
<style>
  @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: 1080px; height: 1350px; overflow: hidden; font-family: 'Pretendard', sans-serif; }}
  .card {{ position: relative; width: 1080px; height: 1350px; background: {bg_color}; }}
  .tag {{ position: absolute; top: 126px; left: 50%; transform: translateX(-50%); background: {footer_bg}; color: {footer_fg}; font-weight: 800; font-size: 35px; padding: 8px 17px; line-height: 1.92; white-space: nowrap; }}
  .title {{ position: absolute; top: 226px; left: 114px; width: 853px; font-weight: 800; font-size: 100px; line-height: 0.93; color: {text_color}; text-align: center; }}
  .body-text {{ position: absolute; top: 459px; left: 154px; width: 771px; font-weight: 500; font-size: 44px; line-height: 1.34; color: {text_color}; }}
  .body-text .bold {{ font-weight: 900; }}
  .body-text .spacer {{ height: 59px; }}
  .footer {{ position: absolute; bottom: 0; left: 0; width: 1080px; height: 119px; background: {footer_bg}; display: flex; align-items: center; justify-content: space-between; padding: 0 44px 0 80px; }}
  .footer-text {{ font-weight: 600; font-size: 37px; color: {footer_fg}; line-height: 1.31; }}
  .footer-arrow {{ width: 40px; height: 43px; display: flex; align-items: center; justify-content: center; }}
</style>
<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>
</head>
<body>
<div class="card">
  <div class="tag">{tag}</div>
  <div class="title">{title}</div>
  <div class="body-text">
    {body_html}
  </div>
  <div class="footer">
    <span class="footer-text">{footer_text}</span>
    <div class="footer-arrow">
      <svg width="40" height="43" viewBox="0 0 40 43" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 8L20 21.5L8 35" stroke="{footer_fg}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M22 8L34 21.5L22 35" stroke="{footer_fg}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
  </div>
</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  텍스트 카드 HTML: {os.path.basename(output_path)}")
    return output_path
