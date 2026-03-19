"""sns_card_factory 중앙 설정 — 모든 상수를 한 곳에서 관리."""

from pathlib import Path

# ── 프로젝트 경로 ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent   # sns_card_news_for_theplay/
PACKAGE_DIR = Path(__file__).resolve().parent            # sns_card_factory/
DATA_DIR = PROJECT_ROOT / "data"
RUNS_DIR = DATA_DIR / "runs"

# ── Gemini 모델 ────────────────────────────────────────────
GEMINI_TEXT_MODEL = "gemini-3.1-pro-preview"
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image-preview"

# ── 카드 규격 ──────────────────────────────────────────────
CARD_WIDTH = 1080
CARD_HEIGHT = 1350

# ── 디자인 토큰 ────────────────────────────────────────────
COLOR_ACCENT = "#FFD03C"
COLOR_WHITE = "#FFFFFF"
COLOR_DARK_BG = "#0F1417"
TEXT_SHADOW = "2px 2px 8px rgba(0,0,0,0.5)"
FONT_FAMILY = "'Pretendard', sans-serif"
FONT_HANDWRITING = "'Ownglyph_wiseelist', sans-serif"

# ── 이미지 생성 ────────────────────────────────────────────
IMAGE_ASPECT_RATIO = "3:4"
IMAGE_SIZE = "1K"
MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 10]  # 초, exponential backoff

# ── 다운로드 ───────────────────────────────────────────────
DOWNLOAD_TIMEOUT = 60  # seconds
VIDEO_FORMAT = "best[ext=mp4]/best"
MAX_VIDEO_SIZE = "100M"

# ── Gemini Files API ───────────────────────────────────────
FILE_UPLOAD_POLL_INTERVAL = 2   # seconds
FILE_UPLOAD_MAX_WAIT = 120      # seconds

# ── 서버 ───────────────────────────────────────────────────
DEFAULT_PORT = 8889

# ── Figma ──────────────────────────────────────────────────
DEFAULT_FIGMA_FILE_KEY = "inuxM4oZWXoyPY9kqqUpPl"
