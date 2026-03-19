"""Gemini Flash Image → 5장 배경 PNG 생성 (OUTPUT_DIR 파라미터화)."""

import os
import time
import base64
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

from ..config import (
    GEMINI_IMAGE_MODEL, IMAGE_ASPECT_RATIO, IMAGE_SIZE,
    MAX_RETRIES, RETRY_DELAYS,
)


def generate_slide_image(
    ref_image_path: str,
    slide_data: dict,
    output_path: str,
    aspect_ratio: str = IMAGE_ASPECT_RATIO,
    image_size: str = IMAGE_SIZE,
) -> str:
    """단일 슬라이드 이미지 생성 (재시도 포함).

    Args:
        ref_image_path: 원본 참고 이미지
        slide_data: 슬라이드 dict (role, image_prompt)
        output_path: 저장할 전체 파일 경로
        aspect_ratio, image_size: 이미지 설정

    Returns:
        생성된 이미지 파일 경로
    """
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    ref_image = Image.open(ref_image_path)

    role = slide_data.get("role", "hook")
    user_prompt = slide_data.get("image_prompt", "")
    full_prompt = (
        f"{user_prompt} "
        f"Keep the product recognizable and accurate to the reference image. "
        f"Aspect ratio {aspect_ratio}, high quality, photorealistic."
    )

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=[ref_image, full_prompt],
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
                    print(f"  [{role}] 이미지 생성 완료 → {os.path.basename(output_path)}")
                    return output_path
                elif part.text:
                    print(f"  모델 응답: {part.text[:100]}")

            last_error = RuntimeError("응답에 이미지 없음")

        except Exception as e:
            last_error = e

        if attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAYS[attempt]
            print(f"  [{role}] 재시도 {attempt+2}/{MAX_RETRIES} ({delay}초 후)...")
            time.sleep(delay)

    raise RuntimeError(f"이미지 생성 실패 ({MAX_RETRIES}회): {role}, error={last_error}")


def generate_all_slide_images(
    ref_image_path: str,
    slides: list[dict],
    output_dir: str,
    prefix: str = "card",
) -> list[dict]:
    """5장 슬라이드 이미지를 순차 생성.

    Args:
        ref_image_path: 참고 이미지 경로
        slides: 5장 슬라이드 리스트
        output_dir: 출력 디렉토리 (파라미터!)
        prefix: 파일명 접두사

    Returns:
        각 슬라이드의 {role, image_path, image_filename, success} 리스트
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for i, slide in enumerate(slides):
        role = slide.get("role", f"slide{i+1}")
        filename = f"{prefix}_{i+1}_{role}.png"
        output_path = os.path.join(output_dir, filename)

        print(f"\n[{i+1}/5] {role} 이미지 생성 중...")

        try:
            generate_slide_image(ref_image_path, slide, output_path)
            results.append({
                "role": role,
                "index": i + 1,
                "image_path": output_path,
                "image_filename": filename,
                "success": True,
            })
        except Exception as e:
            print(f"  [ERROR] {role}: {e}")
            results.append({
                "role": role,
                "index": i + 1,
                "image_path": None,
                "image_filename": None,
                "success": False,
                "error": str(e),
            })

    success_count = sum(1 for r in results if r["success"])
    print(f"\n이미지 생성 완료: {success_count}/{len(slides)} 성공")
    return results
