---
name: figma-carousel-gen
description: 인스타그램 캐러셀 카드뉴스 5장 자동 생성 → Figma 삽입
user-invocable: true
trigger-keywords:
  - 캐러셀 만들어
  - 카드뉴스 생성
  - carousel
  - 캐러셀 생성
  - 5장 카드
  - figma carousel
---

# 인스타그램 캐러셀 카드뉴스 자동 생성기

> 하나의 제품/오브젝트 이미지 + 주제를 입력하면, 5장의 스토리텔링 캐러셀 카드를 자동 생성하여 Figma에 삽입

## 절대 규칙

1. **프로젝트 경로**: `C:/python/venv/sns_card_news_for_theplay/` 에서 작업
2. **이미지 생성 모델**: `sns_card_factory.config.GEMINI_IMAGE_MODEL` (현재: `gemini-3.1-flash-image-preview`)
3. **텍스트 생성 모델**: `sns_card_factory.config.GEMINI_TEXT_MODEL` (현재: `gemini-3.1-pro-preview`)
4. **API 키**: `.env`의 `GOOGLE_API_KEY` 사용 (하드코딩 금지)
5. **카드 크기**: 1080×1350px (인스타그램 세로 포스트 규격)
6. **Figma 파일**: 사용자가 fileKey를 지정하지 않으면 기본값 `sns_card_factory.config.DEFAULT_FIGMA_FILE_KEY` 사용
7. **이미지 추출**: `part.inline_data.data` → `BytesIO` → `PIL.Image` (as_image() 사용 금지)

## 5-Slide Storytelling Framework

| Slide | 역할 | 이미지 스타일 | 텍스트 레이아웃 |
|-------|------|-------------|--------------|
| 1 | **Hook** (질문) | 극적/시네마틱 장면 | 상단 질문 + 중앙 강조어(회전 가능) + 하단 후킹 |
| 2 | **Problem** (문제) | 사실적 사용 장면 | In10T 로고 + 상단 질문 + 하단 인사이트 |
| 3 | **Concept** (개념) | 제품 진열/패턴 | 상단 키워드(노란) + 부제(흰) + 하단 결론 |
| 4 | **Explain** (해설) | 인포그래픽/다이어그램 | 상단 제목 + 손글씨 주석 |
| 5 | **Conclusion** (결론) | 감성적 연출 | 상단 마무리 메시지 |

## 워크플로우

### Phase 1: 사용자 입력 수집

사용자에게 다음을 순서대로 질문한다. 이미 제공된 정보는 스킵.

#### Q1. 주제 입력
```
캐러셀 카드뉴스의 주제를 알려주세요.
예: "하인즈 케첩 디자인 혁신", "에어팟 프로 2 리뷰"
```

#### Q2. 제품/오브젝트 이미지
```
메인 이미지를 선택해주세요:
1. 파일 경로 직접 입력
2. 프로젝트 내 기존 PNG 파일 사용
3. Figma 에셋 URL 제공
```

#### Q3. Figma 삽입 여부
```
Figma에 바로 넣을까요?
1. 네, 기본 파일에 추가
2. 네, 다른 Figma 파일에 추가 (URL 입력)
3. 아니요, HTML만 생성
```

### Phase 2: 파이프라인 실행

`sns_card_factory` 모듈을 사용하여 실행:

```python
import sys
sys.path.insert(0, "C:/python/venv/sns_card_news_for_theplay")

from sns_card_factory.env import load_env
from sns_card_factory.cardnews.content_gen import generate_from_topic, save_content_json
from sns_card_factory.cardnews.image_gen import generate_all_slide_images
from sns_card_factory.cardnews.html_gen import generate_all_slide_htmls, generate_gallery_html
from sns_card_factory.config import DEFAULT_PORT, DEFAULT_FIGMA_FILE_KEY

load_env()

# output_dir 설정 (프로젝트 내 data/runs/ 또는 지정 경로)
output_dir = "C:/python/venv/sns_card_news_for_theplay/data/carousel_output"
```

**단계:**
1. **콘텐츠 생성**: `generate_from_topic(topic, image_path)` → 5장 JSON
2. **이미지 생성**: `generate_all_slide_images(image_path, slides, output_dir)` → 5장 PNG
3. **HTML 생성**: `generate_all_slide_htmls(slides, image_results, output_dir)` + `generate_gallery_html(slides, image_results, output_dir)` → 갤러리

### Phase 3: Figma 삽입

1. 로컬 서버 시작 (port 8889, output 폴더 서빙)
2. `generate_figma_design(outputMode="existingFile", fileKey="<key>")` → captureId
3. 브라우저 오픈: `http://localhost:8889/card_gallery.html#figmacapture=<id>&...`
4. 폴링 → 완료 확인
5. Figma URL 오픈

### Phase 4: 결과 보고

```markdown
## 캐러셀 생성 결과

| Slide | 역할 | 이미지 | HTML |
|-------|------|--------|------|
| 1 | Hook | card_1_hook.png | card_1_hook.html |
| 2 | Problem | card_2_problem.png | card_2_problem.html |
| 3 | Concept | card_3_concept.png | card_3_concept.html |
| 4 | Explain | card_4_explain.png | card_4_explain.html |
| 5 | Conclusion | card_5_conclusion.png | card_5_conclusion.html |

갤러리: card_gallery.html
Figma: {URL}
```

## 고급 옵션

- **콘텐츠만 재생성**: `--skip-images` 플래그로 기존 이미지 재사용
- **기존 JSON 사용**: content.json을 직접 편집 후 이미지+HTML만 재생성
- **개별 슬라이드 수정**: 각 HTML 파일을 직접 편집 가능

## 디자인 시스템

- **폰트**: Pretendard (ExtraBold/Black/Medium/SemiBold) + Ownglyph_wiseelist (손글씨)
- **컬러**: 텍스트 흰색, 강조어 `#FFD03C`, 텍스트 쉐도우 `rgba(0,0,0,0.5)`
- **이미지 처리**: radial/linear gradient overlay로 텍스트 가독성 확보
- **크기**: 1080×1350px (인스타 세로)

## 에러 핸들링

| 상황 | 대응 |
|------|------|
| Gemini API 실패 | 에러 메시지 출력 + API 키 확인 안내 |
| 이미지 생성 일부 실패 | 성공한 슬라이드만으로 갤러리 생성 |
| HTTP 서버 포트 충돌 | 다른 포트 시도 |
| Figma 캡처 타임아웃 | 서버 상태 점검 안내 |

## 사용법

```
/figma-carousel-gen
/figma-carousel-gen 하인즈 케첩 디자인 혁신
캐러셀 만들어줘 - 에어팟 프로 2 리뷰
```

## 핵심 파일

```
sns_card_news_for_theplay/
├── sns_card_factory/
│   ├── config.py                 ← 모델명, 디자인 토큰, Figma 키
│   ├── env.py                    ← .env 로딩
│   ├── utils.py                  ← hex_to_rgba 등
│   └── cardnews/
│       ├── content_gen.py        ← Gemini Text → 5장 콘텐츠 JSON
│       ├── image_gen.py          ← Gemini Image × 5 → 이미지 베리에이션
│       └── html_gen.py           ← 5가지 레이아웃 템플릿 + HTML + 갤러리
```

## 버전

- v2.0 (2026-03-19): sns_card_factory 모듈 기반으로 마이그레이션, output_dir 파라미터화
- v1.0 (2026-03-18): 초기 버전 — figma_mcp_test 기반
