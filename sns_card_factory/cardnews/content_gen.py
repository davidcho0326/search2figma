"""슬라이드 콘텐츠 JSON 생성 — 2모드 (analysis 기반 / topic 기반)."""

import json
import os
from typing import Dict, Optional

from google import genai
from google.genai import types
from PIL import Image

from ..config import GEMINI_TEXT_MODEL
from ..utils import parse_json_response

SYSTEM_PROMPT = """당신은 인스타그램 캐러셀 카드뉴스 콘텐츠 전문가입니다.
주어진 콘텐츠 분석 결과를 바탕으로 5장의 스토리텔링 캐러셀 콘텐츠를 생성합니다.

## 5-Slide Storytelling Framework

1. **hook** (질문/주의 끌기): 청중의 호기심을 자극하는 질문이나 반전 요소
2. **problem** (문제 제기): 일상적 불편함이나 궁금증을 사실적으로 묘사
3. **concept** (핵심 개념): 해답의 키워드를 강렬하게 제시
4. **explain** (해설): 원리나 메커니즘을 인포그래픽 스타일로 설명
5. **conclusion** (결론): 감성적 마무리와 브랜드/주제 호감 표현

## 출력 규칙

- 모든 텍스트는 한국어 (캐주얼 반말체, 인스타그램 톤)
- 각 슬라이드의 image_prompt는 영문으로 작성 (이미지 생성 AI용)
- highlight_word는 노란색(#FFD03C)으로 강조될 1-2단어
- 각 텍스트는 짧고 임팩트 있게 (한 줄 최대 15자 내외)

## JSON 출력 형식

```json
{
  "topic": "주제명",
  "slides": [
    {
      "role": "hook",
      "title": "상단 질문 텍스트 (1-2줄)",
      "highlight_word": "강조 키워드",
      "highlight_rotation": 0,
      "bottom_text": "하단 후킹 텍스트",
      "image_prompt": "English prompt for image generation...",
      "overlay_type": "radial_gradient"
    },
    {
      "role": "problem",
      "title": "상단 질문/문제 텍스트",
      "highlight_word": "강조 키워드",
      "highlight_rotation": 0,
      "bottom_text": "하단 인사이트 텍스트",
      "image_prompt": "English prompt...",
      "overlay_type": "gradient"
    },
    {
      "role": "concept",
      "title": "키워드 (1단어)",
      "subtitle": "부제 (짧은 설명)",
      "highlight_word": "키워드와 동일",
      "highlight_rotation": 0,
      "bottom_text": "하단 결론 텍스트",
      "image_prompt": "English prompt...",
      "overlay_type": "strong_gradient"
    },
    {
      "role": "explain",
      "title": "상단 제목 (2-3단어)",
      "highlight_word": "강조 키워드",
      "highlight_rotation": 0,
      "annotation_text": "손글씨 스타일 주석 텍스트",
      "image_prompt": "English prompt...",
      "overlay_type": "solid_dark"
    },
    {
      "role": "conclusion",
      "title": "마무리 감성 메시지 (1-2줄)",
      "highlight_word": "감성 키워드",
      "highlight_rotation": 0,
      "bottom_text": "",
      "image_prompt": "English prompt...",
      "overlay_type": "light_gradient"
    }
  ]
}
```
"""

ADAPTER_PROMPT = """## 원본 소셜미디어 콘텐츠 분석

- **핵심 주제**: {core_topic}
- **핵심 메시지**: {key_messages}
- **비주얼 요소**: {visual_elements}
- **감성 톤**: {emotional_tone}
- **타겟 오디언스**: {target_audience}
- **바이럴 요소**: {viral_factor}
- **카드뉴스 앵글**: {card_news_angle}
- **원본 플랫폼**: {platform}

## 요청

위 분석 결과를 바탕으로 5장 인스타그램 캐러셀 카드뉴스 콘텐츠를 생성해주세요.

규칙:
1. 원본 콘텐츠의 핵심 메시지를 살리되, 카드뉴스에 맞게 재구성
2. 각 슬라이드의 image_prompt에는 분석된 비주얼 요소를 활용하여 구체적으로 묘사
3. hook에서 호기심을 확실히 끌고, conclusion에서 감성적으로 마무리
4. 텍스트는 한국어 캐주얼 반말체, image_prompt는 영문
5. highlight_word는 각 슬라이드에서 가장 임팩트있는 1-2단어

JSON만 출력하세요."""

_REQUIRED_FIELDS = {
    "hook": ["title", "highlight_word", "bottom_text", "image_prompt"],
    "problem": ["title", "highlight_word", "bottom_text", "image_prompt"],
    "concept": ["title", "subtitle", "highlight_word", "bottom_text", "image_prompt"],
    "explain": ["title", "highlight_word", "annotation_text", "image_prompt"],
    "conclusion": ["title", "highlight_word", "image_prompt"],
}


def _validate_content(content: Dict) -> Dict:
    """carousel_content.json 스키마 검증 및 보정."""
    if "topic" not in content:
        content["topic"] = "SNS 콘텐츠"

    slides = content.get("slides", [])
    if len(slides) != 5:
        raise ValueError(f"Expected 5 slides, got {len(slides)}")

    expected_roles = ["hook", "problem", "concept", "explain", "conclusion"]
    for i, slide in enumerate(slides):
        if slide.get("role") != expected_roles[i]:
            slide["role"] = expected_roles[i]

        role = slide["role"]
        for field in _REQUIRED_FIELDS.get(role, []):
            if not slide.get(field):
                slide[field] = role if field != "image_prompt" else f"Scene related to {role}"

    return content


def _get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)


def generate_from_analysis(analysis: Dict, thumb_path: Optional[str] = None) -> Dict:
    """분석 결과 → 5장 슬라이드 JSON (SNS 파이프라인 모드)."""
    client = _get_client()

    prompt = ADAPTER_PROMPT.format(
        core_topic=analysis.get("core_topic", ""),
        key_messages="\n".join(f"  - {m}" for m in analysis.get("key_messages", [])),
        visual_elements="\n".join(f"  - {v}" for v in analysis.get("visual_elements", [])),
        emotional_tone=analysis.get("emotional_tone", ""),
        target_audience=analysis.get("target_audience", ""),
        viral_factor=analysis.get("viral_factor", ""),
        card_news_angle=analysis.get("card_news_angle", ""),
        platform=analysis.get("_source", {}).get("platform", "unknown"),
    )

    contents = []
    if thumb_path and os.path.exists(thumb_path):
        contents.append(Image.open(thumb_path))
    contents.append(prompt)

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.8,
            max_output_tokens=4096,
        ),
    )

    content = parse_json_response(response.text)
    if not content.get("topic"):
        content["topic"] = analysis.get("core_topic", "SNS 콘텐츠")

    return _validate_content(content)


def generate_from_topic(topic: str, image_path: Optional[str] = None) -> Dict:
    """주제 직접 입력 → 5장 슬라이드 JSON (독립 모드)."""
    client = _get_client()

    user_prompt = f"주제: {topic}\n\n위 주제로 5장 인스타그램 캐러셀 카드뉴스를 만들어주세요. JSON만 출력."

    contents = []
    if image_path and os.path.exists(image_path):
        contents.append(Image.open(image_path))
    contents.append(user_prompt)

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.8,
            max_output_tokens=4096,
        ),
    )

    content = parse_json_response(response.text)
    if not content.get("topic"):
        content["topic"] = topic

    return _validate_content(content)


def save_content_json(content: Dict, output_path: str) -> str:
    """콘텐츠 JSON을 파일로 저장."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print(f"  -> Content JSON saved: {output_path}")
    return output_path
