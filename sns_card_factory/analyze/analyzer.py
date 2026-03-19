"""Gemini 멀티모달 콘텐츠 분석."""

import json
import os
import time
from typing import Dict, Optional

from google import genai
from google.genai import types
from PIL import Image

from ..config import (
    GEMINI_TEXT_MODEL,
    FILE_UPLOAD_POLL_INTERVAL,
    FILE_UPLOAD_MAX_WAIT,
)
from ..utils import parse_json_response

ANALYSIS_PROMPT = """당신은 소셜미디어 콘텐츠 분석 전문가입니다.
아래 콘텐츠를 분석하고 JSON으로 응답하세요.

## 원본 정보
- 플랫폼: {platform}
- 캡션: {caption}
- 해시태그: {hashtags}
- 지표: {metrics}

## 분석 항목 (모두 한국어로)

1. **core_topic**: 핵심 주제 (1문장, 카드뉴스 제목으로 쓸 수 있을 정도로 임팩트있게)
2. **key_messages**: 핵심 메시지 3-5개 (리스트, 각 1문장)
3. **visual_elements**: 영상/이미지의 주요 비주얼 요소 묘사 (리스트, 각 1문장, 영문으로)
4. **emotional_tone**: 감성 톤 (1단어: 유머/감동/정보/도발/영감/실용 등)
5. **target_audience**: 타겟 오디언스 (1문장)
6. **viral_factor**: 바이럴/인기 요소 (왜 사람들이 관심을 가지는지 1문장)
7. **card_news_angle**: 이 콘텐츠를 5장 카드뉴스로 재가공할 때의 최적 스토리 앵글 (1문장)

JSON만 출력하세요. 다른 텍스트 없이 JSON만.
"""


def _get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)


def _format_metrics(engagement: Dict) -> str:
    parts = []
    for key, label in [("views", "조회수"), ("upvotes", "Upvotes"), ("likes", "좋아요"),
                        ("comments", "댓글"), ("shares", "공유")]:
        val = engagement.get(key)
        if val:
            parts.append(f"{label}: {val}")
    return ", ".join(parts) if parts else "없음"


def analyze_video(video_path: str, caption: str, platform: str,
                  engagement: Dict, hashtags: str = "") -> Dict:
    """영상 파일을 Gemini Files API로 업로드하고 분석."""
    client = _get_client()
    print(f"  Uploading video to Gemini Files API...")

    video_file = client.files.upload(file=video_path)
    print(f"  -> Uploaded: {video_file.name} (state: {video_file.state.name})")

    elapsed = 0
    while video_file.state.name == "PROCESSING":
        time.sleep(FILE_UPLOAD_POLL_INTERVAL)
        elapsed += FILE_UPLOAD_POLL_INTERVAL
        video_file = client.files.get(name=video_file.name)
        if elapsed > FILE_UPLOAD_MAX_WAIT:
            print(f"  [WARN] File processing timeout ({FILE_UPLOAD_MAX_WAIT}s)")
            break

    if video_file.state.name == "FAILED":
        raise RuntimeError(f"Video processing failed: {video_file.state}")

    print(f"  -> Processing complete, analyzing...")

    prompt = ANALYSIS_PROMPT.format(
        platform=platform, caption=caption[:1000],
        hashtags=hashtags, metrics=_format_metrics(engagement),
    )

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=[video_file, prompt],
        config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=4096),
    )

    try:
        client.files.delete(name=video_file.name)
        print(f"  -> Cleaned up uploaded file")
    except Exception:
        pass

    return parse_json_response(response.text)


def analyze_image(image_path: str, caption: str, platform: str,
                  engagement: Dict, hashtags: str = "") -> Dict:
    """이미지 파일을 Gemini로 분석."""
    client = _get_client()
    img = Image.open(image_path)

    prompt = ANALYSIS_PROMPT.format(
        platform=platform, caption=caption[:1000],
        hashtags=hashtags, metrics=_format_metrics(engagement),
    )

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=[img, prompt],
        config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=4096),
    )

    return parse_json_response(response.text)


def analyze_text(caption: str, title: str, platform: str,
                 engagement: Dict, hashtags: str = "") -> Dict:
    """텍스트만으로 Gemini 분석."""
    client = _get_client()

    prompt = ANALYSIS_PROMPT.format(
        platform=platform,
        caption=f"제목: {title}\n\n본문: {caption[:2000]}",
        hashtags=hashtags, metrics=_format_metrics(engagement),
    )

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=4096),
    )

    return parse_json_response(response.text)


def analyze_content(download_result: Dict) -> Dict:
    """DownloadResult를 받아 적절한 분석 함수를 호출."""
    media_type = download_result["media_type"]
    platform = download_result["platform"]
    caption = download_result["caption"]
    engagement = download_result["engagement"]
    hashtags = download_result.get("hashtags", "")

    print(f"  Analyzing {media_type} content with Gemini...")

    if media_type == "video" and download_result.get("media_path"):
        analysis = analyze_video(
            download_result["media_path"], caption, platform, engagement, hashtags
        )
    elif media_type == "image" and download_result.get("media_path"):
        analysis = analyze_image(
            download_result["media_path"], caption, platform, engagement, hashtags
        )
    else:
        analysis = analyze_text(
            caption, download_result.get("title", ""), platform, engagement, hashtags
        )

    analysis["_source"] = {
        "platform": platform,
        "url": download_result["url"],
        "title": download_result.get("title", ""),
        "media_type": media_type,
    }

    return analysis
