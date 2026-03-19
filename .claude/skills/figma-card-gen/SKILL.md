---
name: figma-card-gen
description: Gemini 이미지 베리에이션 + SNS 카드 생성 → Figma 자동 삽입
user-invocable: true
trigger-keywords:
  - 카드 생성
  - figma 카드
  - SNS 카드
  - 캐릭터 베리에이션
  - 카드 만들어
  - figma card
---

# Figma SNS 카드 생성기

> 캐릭터 이미지 베리에이션(Gemini) + 카드 콘텐츠 제어 → HTML 렌더링 → Figma 자동 삽입 파이프라인

## 절대 규칙

1. **프로젝트 경로**: `C:/python/venv/sns_card_news_for_theplay/` 에서 작업
2. **이미지 생성 모델**: `gemini-3.1-flash-image-preview` (최신 모델, 변경 금지)
3. **API 키**: `.env`의 `GOOGLE_API_KEY` 사용 (하드코딩 금지)
4. **카드 크기**: 1080×1350px (인스타그램 세로 포스트 규격, 변경 금지)
5. **폰트**: Pretendard (CDN import)
6. **Figma 파일**: 사용자가 fileKey를 지정하지 않으면 기본값 `inuxM4oZWXoyPY9kqqUpPl` 사용
7. **이미지 추출 방식**: `part.inline_data.data` → `BytesIO` → `PIL.Image` (as_image() 사용 금지)

## 워크플로우

### Phase 1: 사용자 입력 수집

사용자에게 다음을 순서대로 질문한다. 이미 제공된 정보는 스킵.

#### Q1. 카드 타입 선택
```
어떤 카드를 만들까요?

1. 🖼️ 캐릭터 카드 — 배경 이미지 + 하단 텍스트
2. 📝 텍스트 카드 — 단색 배경 + 제목/본문
3. 🎨 커스텀 — 직접 지정
```

#### Q2. 캐릭터 카드인 경우 → 이미지 베리에이션 설정
```
캐릭터 이미지를 어떻게 할까요?

1. 기존 캐릭터에서 표정/분위기 변형 (레퍼런스 이미지 필요)
2. 새 이미지 직접 제공 (경로 지정)
3. 기존 생성된 이미지 재사용
```

#### Q3. 카드 콘텐츠 입력

**캐릭터 카드:**
- `logo`: 좌상단 로고 텍스트 (기본: "In10T")
- `highlight_text`: 하이라이트 텍스트 (노란색, 첫 줄)
- `body_lines`: 본문 텍스트 (여러 줄, 배열)
- `bg_color`: 배경 색상 (기본: #7B5EA7)

**텍스트 카드:**
- `tag`: 상단 태그 pill 텍스트
- `title`: 대제목
- `body_lines`: 본문 텍스트 (여러 줄)
- `bold_keywords`: 볼드 처리할 키워드 목록
- `bg_color`: 배경 색상 (기본: #FFD03C)
- `footer_text`: 하단 바 텍스트 (기본: "경험을 디자인하다")

#### Q4. Figma 삽입 여부
```
Figma에 바로 넣을까요?
1. 네, 기본 파일에 추가
2. 네, 다른 Figma 파일에 추가 (URL 입력)
3. 아니요, HTML만 생성
```

### Phase 2: 이미지 베리에이션 생성 (캐릭터 카드만)

```python
import sys, os
sys.path.insert(0, "C:/python/venv/sns_card_news_for_theplay")

from sns_card_factory.env import load_env
load_env()

from sns_card_factory.cardnews.card_generator import generate_character_variation

output_dir = "C:/python/venv/sns_card_news_for_theplay/data/card_output"
output_path = os.path.join(output_dir, "<output_filename>.png")

image_path = generate_character_variation(
    ref_image_path="<레퍼런스_이미지_경로>",
    variation_prompt="<사용자_변형_프롬프트>",
    output_path=output_path,
)
```

**프롬프트 작성 규칙:**
- 영문 프롬프트 사용 (Gemini 이미지 생성 품질 향상)
- 유지할 요소를 먼저 명시: "Keep the EXACT same character design, colors, composition..."
- 변경할 요소를 구체적으로: "Only change the facial expression to..."
- 배경/스타일 보존 강조: "Maintain the [color] background and overall scene layout"

### Phase 3: HTML 카드 생성

`card_generator` 모듈의 HTML 생성 함수 사용:

**캐릭터 카드:**
```python
from sns_card_factory.cardnews.card_generator import generate_character_card_html

html_path = generate_character_card_html(
    image_filename="<생성된_이미지_파일명>.png",
    highlight_text="앱 캐릭터의 감정이 실제 행동을 바꿀 수 있을까요?",
    body_lines=["듀오가 슬퍼하면 왠지 미안해지고", "알림을 무시하면 괜히 죄책감이 들어요."],
    output_path=os.path.join(output_dir, "card_output.html"),
    logo="In10T",
    bg_color="#7B5EA7",
)
```

**텍스트 카드:**
```python
from sns_card_factory.cardnews.card_generator import generate_text_card_html

html_path = generate_text_card_html(
    title="테스트 제목",
    body_lines=["첫 번째 줄", "", "세 번째 줄은 볼드 포함"],
    output_path=os.path.join(output_dir, "card_text.html"),
    bold_keywords=["볼드"],
    bg_color="#FFD03C",
)
```

### Phase 4: Figma 삽입

1. 로컬 서버 확인/시작 (port 8889)
2. `generate_figma_design(outputMode="existingFile", fileKey="<fileKey>")` 호출 → captureId
3. 브라우저 오픈: `start "" "http://localhost:8889/<filename>.html#figmacapture=<id>&...&figmadelay=2000"`
4. 폴링 (5초 간격) → completed
5. Figma URL 오픈

### Phase 5: 결과 보고

```markdown
| 항목 | 내용 |
|------|------|
| 카드 타입 | 캐릭터/텍스트 |
| 이미지 | {생성된 이미지 파일명} |
| HTML | {HTML 파일명} |
| Figma | {Figma URL with node-id} |
```

## 에러 핸들링

| 상황 | 대응 |
|------|------|
| Gemini API 실패 | 에러 메시지 출력 + API 키 확인 안내 |
| 이미지 생성 없음 (텍스트만 반환) | `response_modalities`에 `"IMAGE"` 포함 확인 후 재시도 |
| HTTP 서버 포트 충돌 | 다른 포트 시도 |
| Figma 캡처 pending 10회 초과 | 스크립트 인젝션, 서버 상태 점검 안내 |

## 사용법

```
/figma-card-gen
/figma-card-gen 울고 있는 캐릭터로 카드 만들어줘
/figma-card-gen 텍스트 카드 새로 만들고 싶어
```

## 핵심 파일

```
sns_card_news_for_theplay/
├── sns_card_factory/
│   ├── config.py              ← 모델명, 디자인 토큰
│   ├── env.py                 ← .env 로딩
│   ├── utils.py               ← hex_to_rgba 등
│   └── cardnews/
│       ├── image_gen.py       ← Gemini Image 생성 (재시도 로직)
│       └── html_gen.py        ← HTML 템플릿
```

## 버전

- v2.0 (2026-03-19): sns_card_factory 모듈 기반으로 마이그레이션
- v1.0 (2026-03-18): 초기 버전 — figma_mcp_test 기반
