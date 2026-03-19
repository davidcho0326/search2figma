# Figma SNS 카드 생성 스킬 — 설치 가이드

다른 프로젝트에서 이 스킬을 사용하기 위한 세팅 안내입니다.

---

## 스킬 개요

| 스킬 | 슬래시 커맨드 | 기능 |
|------|-------------|------|
| **figma-card-gen** | `/figma-card-gen` | 단일 SNS 카드 생성 (캐릭터 카드 / 텍스트 카드) |
| **figma-carousel-gen** | `/figma-carousel-gen` | 5장 캐러셀 카드뉴스 자동 생성 (Hook→Problem→Concept→Explain→Conclusion) |

두 스킬 모두 **Gemini 이미지 생성 + HTML 렌더링 + Figma MCP 자동 삽입** 파이프라인입니다.

---

## 1. 사전 요구사항

### Python 패키지

```bash
pip install google-genai Pillow python-dotenv
```

| 패키지 | 최소 버전 | 용도 |
|--------|----------|------|
| `google-genai` | 1.56+ | Gemini API (이미지/텍스트 생성) |
| `Pillow` | 10.0+ | 이미지 처리 |
| `python-dotenv` | 1.0+ | .env 파일 로드 |

### API 키

프로젝트 루트에 `.env` 파일 생성:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> Google AI Studio(https://aistudio.google.com/)에서 API 키를 발급받으세요.
> Gemini 3.1 Flash Image Preview 모델 접근 권한이 필요합니다.

### Figma MCP 연결

Claude Code에서 Figma MCP 서버를 등록해야 합니다:

```bash
# 1. Figma MCP 서버 추가
claude mcp add --transport http figma-remote-mcp http://mcp.figma.com/mcp

# 2. Figma 플러그인 인증
/plugin install figma@claude-plugin-directory
/plugin          # 인증 진행
```

---

## 2. 파일 복사

### 필수 파일 (모듈)

아래 파일들을 대상 프로젝트에 복사합니다. 폴더 구조를 유지하세요.

```
your-project/
├── .env                          # API 키
├── figma_mcp_test/               # ← 이 폴더 통째로 복사
│   ├── carousel_config.py        # 중앙 설정 (모델명, 디자인 토큰)
│   ├── card_generator.py         # 단일 카드 생성 모듈
│   ├── carousel_content_gen.py   # Gemini Text → 5장 콘텐츠 JSON
│   ├── carousel_image_gen.py     # Gemini Image × 5 → 이미지 베리에이션
│   ├── carousel_html_gen.py      # 5가지 레이아웃 템플릿 + HTML
│   └── carousel_pipeline.py      # 오케스트레이터 (전체 파이프라인)
└── .claude/
    └── skills/
        ├── figma-card-gen/
        │   └── SKILL.md           # 단일 카드 스킬 정의
        └── figma-carousel-gen/
            └── SKILL.md           # 캐러셀 스킬 정의
```

### 스킬 파일만 복사 (최소 설치)

스킬 정의만 필요하면 SKILL.md 파일 2개만 복사:

```bash
# 대상 프로젝트의 .claude/skills/ 에 복사
mkdir -p .claude/skills/figma-card-gen
mkdir -p .claude/skills/figma-carousel-gen

cp /path/to/figma_mcp_test/../.claude/skills/figma-card-gen/SKILL.md .claude/skills/figma-card-gen/
cp /path/to/figma_mcp_test/../.claude/skills/figma-carousel-gen/SKILL.md .claude/skills/figma-carousel-gen/
```

---

## 3. 설정 변경

### carousel_config.py 수정

대상 프로젝트에 맞게 설정을 변경합니다:

```python
# carousel_config.py

# Gemini 모델 (변경하지 않는 것을 권장)
GEMINI_TEXT_MODEL = "gemini-3.1-pro-preview"
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image-preview"

# 카드 규격 (인스타그램 기본값)
CARD_WIDTH = 1080
CARD_HEIGHT = 1350

# 디자인 토큰 — 프로젝트에 맞게 수정 가능
COLOR_ACCENT = "#FFD03C"      # 강조 색상
COLOR_WHITE = "#FFFFFF"
COLOR_DARK_BG = "#0F1417"     # 어두운 배경
TEXT_SHADOW = "2px 2px 8px rgba(0,0,0,0.5)"
FONT_FAMILY = "'Pretendard', sans-serif"
FONT_HANDWRITING = "'Ownglyph_wiseelist', sans-serif"

# 서버
DEFAULT_PORT = 8889           # HTTP 서버 포트

# Figma — 본인의 Figma 파일 키로 변경
DEFAULT_FILE_KEY = "your_figma_file_key_here"

# 이미지 생성
IMAGE_ASPECT_RATIO = "3:4"    # 세로형 (1080×1350)
IMAGE_SIZE = "1K"
MAX_RETRIES = 3
```

### SKILL.md 경로 수정

SKILL.md 내 하드코딩된 경로를 대상 프로젝트에 맞게 변경:

```
# 변경 전
C:/python/venv/figma_mcp_test/

# 변경 후 (예시)
/Users/yourname/your-project/figma_mcp_test/
```

**수정이 필요한 위치** (두 SKILL.md 공통):
- `절대 규칙` 섹션의 프로젝트 경로
- `Phase 2` 코드 블록 내 `load_dotenv` 경로
- `Phase 4` 의 서버 시작 경로

---

## 4. Figma 파일 준비

### 새 Figma 파일 사용 시

1. Figma에서 새 파일 생성
2. URL에서 fileKey 추출: `figma.com/design/{fileKey}/...`
3. `carousel_config.py`의 `DEFAULT_FILE_KEY`에 입력
4. 또는 스킬 실행 시 Figma URL을 직접 제공

### 기존 파일에 추가 시

스킬 실행 시 Q4에서 "다른 Figma 파일에 추가"를 선택하고 URL을 입력하면 됩니다.

---

## 5. 동작 확인

### 단일 카드 테스트

```bash
# Claude Code에서
/figma-card-gen

# 또는 자연어로
"텍스트 카드 하나 만들어줘"
```

### 캐러셀 테스트

```bash
# Claude Code에서
/figma-carousel-gen

# 또는 자연어로
"에어팟 프로 2 디자인 혁신으로 캐러셀 만들어줘"
```

### 모듈 단독 테스트

```python
# Python에서 직접 실행
import sys
sys.path.insert(0, "figma_mcp_test")

from card_generator import generate_text_card_html

generate_text_card_html(
    title="테스트 제목",
    body_lines=["첫 번째 줄", "", "볼드 테스트"],
    bold_keywords=["볼드"],
    output_filename="test.html"
)
# → output/test.html 생성
```

---

## 6. 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError: carousel_config` | Python 경로 문제 | `sys.path`에 `figma_mcp_test/` 추가 또는 해당 폴더에서 실행 |
| `google.genai` import 실패 | 패키지 미설치 | `pip install google-genai` |
| `GOOGLE_API_KEY` None | .env 파일 누락 또는 경로 오류 | .env 파일 위치 확인, `dotenv_path` 수정 |
| 이미지 생성 시 텍스트만 반환 | `response_modalities` 누락 | `["TEXT", "IMAGE"]` 확인 |
| `as_image()` AttributeError | SDK 호환성 문제 | `inline_data.data` → `BytesIO` → `PIL.Image` 패턴 사용 (이미 적용됨) |
| Figma 캡처 실패 | MCP 서버 미연결 | `claude mcp add` 재실행 + `/plugin` 인증 확인 |
| HTTP 서버 포트 충돌 | 이미 사용 중인 포트 | `carousel_config.py`에서 `DEFAULT_PORT` 변경 |
| 스킬이 목록에 안 보임 | SKILL.md 위치 오류 | `.claude/skills/{name}/SKILL.md` 경로 확인 |

---

## 7. 핵심 모듈 API 레퍼런스

### card_generator.py

```python
# 이미지 베리에이션 생성
generate_character_variation(
    ref_image_path: str,       # 레퍼런스 이미지 경로
    variation_prompt: str,     # 변형 지시 (영문 권장)
    output_filename: str,      # 출력 파일명
    aspect_ratio: str = "3:4",
    image_size: str = "1K"
) → str  # 저장된 파일 경로

# 캐릭터 카드 HTML 생성
generate_character_card_html(
    image_filename: str,       # 배경 이미지 파일명
    highlight_text: str,       # 노란색 강조 텍스트
    body_lines: list[str],     # 본문 (줄 단위)
    logo: str = "In10T",
    bg_color: str = "#7B5EA7",
    output_filename: str = "card_output.html"
) → str  # 저장된 HTML 경로

# 텍스트 카드 HTML 생성
generate_text_card_html(
    title: str,                # 대제목
    body_lines: list[str],     # 본문 (빈 문자열 = spacer)
    tag: str = "저장하고 꺼내보기",
    bold_keywords: list[str],  # 볼드 처리할 키워드
    bg_color: str = "#FFD03C",
    footer_text: str = "경험을 디자인하다",
    output_filename: str = "card_text_output.html"
) → str  # 저장된 HTML 경로
```

### carousel_pipeline.py

```python
# 전체 파이프라인 한 번에 실행
run_pipeline(
    topic: str,              # 주제
    image_path: str          # 입력 이미지 경로
) → dict  # 생성 결과 (파일 경로들)
```

---

## 8. 커스터마이징 포인트

| 항목 | 파일 | 변경 방법 |
|------|------|----------|
| 브랜드 색상 | `carousel_config.py` | `COLOR_ACCENT` 등 수정 |
| 카드 크기 | `carousel_config.py` | `CARD_WIDTH`, `CARD_HEIGHT` (Figma 캡처에도 반영됨) |
| 폰트 | `carousel_config.py` + HTML 템플릿 | `FONT_FAMILY` + CDN import URL |
| 슬라이드 수 | `carousel_content_gen.py` | `generate_carousel_content()`의 프롬프트 수정 |
| 레이아웃 템플릿 | `carousel_html_gen.py` | `SLIDE_TEMPLATES` dict 수정 |
| 이미지 모델 | `carousel_config.py` | `GEMINI_IMAGE_MODEL` (신규 모델 출시 시) |
| Figma 기본 파일 | `carousel_config.py` | `DEFAULT_FILE_KEY` |
