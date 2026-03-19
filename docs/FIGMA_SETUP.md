# Figma MCP + Plugin Setup Guide

이 프로젝트의 카드뉴스 → Figma 삽입 워크플로우를 사용하기 위한 설정 가이드입니다.

## 아키텍처

```
┌─────────────────────────────────────────────────────┐
│  Claude Code                                         │
│                                                      │
│  ┌──────────────────────┐   ┌─────────────────────┐ │
│  │ Figma Plugin v1.2.0  │   │ Playwright MCP      │ │
│  │ (Agent Skills 포함)   │   │ (외부 사이트 캡처용)  │ │
│  └──────────┬───────────┘   └─────────────────────┘ │
│             │                                        │
│             ▼                                        │
│  ┌──────────────────────┐                           │
│  │ Figma MCP Server     │  ← https://mcp.figma.com │
│  │ (Figma 공식 원격)     │                           │
│  └──────────────────────┘                           │
└─────────────────────────────────────────────────────┘
```

| 구성요소 | 제공자 | 설치 명령 |
|---------|--------|----------|
| **Figma MCP Server** | Figma (공식) | `claude mcp add --transport http figma https://mcp.figma.com/mcp` |
| **Figma Plugin** | Anthropic (공식 마켓플레이스) | `claude plugin install figma@claude-plugins-official` |

> **Plugin은 MCP 서버 설정 + Agent Skills을 번들로 포함합니다.**
> Plugin을 설치하면 MCP 서버도 자동 등록되므로, 둘 중 하나만 해도 됩니다.

## 1. Figma Plugin 설치 (권장)

Plugin은 Anthropic의 공식 플러그인 마켓플레이스(`anthropics/claude-plugins-official`)에서 배포됩니다.

```bash
# Claude Code 터미널에서 실행
claude plugin install figma@claude-plugins-official
```

이 명령은 다음을 자동으로 수행합니다:
- `https://mcp.figma.com/mcp` 원격 MCP 서버 등록
- Figma Agent Skills 설치 (`implement-design`, `code-connect-components`, `create-design-system-rules`)
- `plugin:figma:figma`라는 이름으로 등록

### 설치 확인

```bash
claude mcp list
```

출력에서 아래 항목이 보여야 합니다:
```
plugin:figma:figma: https://mcp.figma.com/mcp (HTTP) - ✓ Connected
```

### 수동 설치 (Plugin 없이 MCP만)

Plugin 없이 MCP 서버만 등록할 수도 있습니다:
```bash
claude mcp add --transport http figma-remote-mcp https://mcp.figma.com/mcp
```

## 2. Figma 계정 인증

MCP 서버에 처음 접근하면 Figma 로그인 페이지가 브라우저에 열립니다.
OAuth로 인증하면 이후 자동으로 연결됩니다.

### 필요 조건
- Figma 계정 (무료 OK, 단 Starter 플랜은 월 6회 도구 호출 제한)
- Dev 또는 Full seat (Professional/Organization/Enterprise 플랜)이면 분당 Rate Limit 적용

## 3. 권한 설정

프로젝트에 `.claude/settings.local.json`이 포함되어 있습니다:

```json
{
  "permissions": {
    "allow": [
      "mcp__plugin_figma_figma__*"
    ]
  }
}
```

이 설정으로 Figma MCP 도구 호출 시 매번 승인 팝업 없이 자동 실행됩니다.

## 4. 사용 가능 MCP 도구

| 도구 | 용도 | 이 프로젝트에서 사용 |
|------|------|-------------------|
| `generate_figma_design` | HTML → Figma 프레임 캡처 | 카드뉴스 Figma 삽입 |
| `get_screenshot` | Figma 노드 스크린샷 | 레퍼런스 이미지 추출 |
| `get_design_context` | 디자인 코드 + 에셋 URL | 캐릭터 이미지 다운로드 |
| `get_metadata` | 파일/노드 메타데이터 | 노드 탐색 |
| `get_variable_defs` | 디자인 토큰 (색상, 간격) | - |
| `generate_diagram` | Mermaid → FigJam | - |

## 5. Figma 파일 설정

### 기본 Figma 파일
프로젝트 기본 Figma 파일 키: `inuxM4oZWXoyPY9kqqUpPl`

다른 Figma 파일을 사용하려면 URL에서 fileKey를 추출합니다:
```
https://figma.com/design/[fileKey]/[fileName]?node-id=1-2
                          ^^^^^^^^
                          이 부분이 fileKey
```

## 6. Playwright MCP (선택)

외부 웹사이트를 Figma로 캡처할 때만 필요합니다. 로컬 HTML 캡처는 Figma MCP만으로 충분합니다.

```bash
# 프로젝트 또는 글로벌 .mcp.json에 추가
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

## 7. 캡처 워크플로우

### 자동 (CLI)
```bash
python cli.py capture <run_id> --post TK4
```

### 수동 (스킬)
```
/figma-card-gen      → 단일 카드 생성 + Figma 삽입
/figma-carousel-gen  → 5장 캐러셀 생성 + Figma 삽입
```

### 캡처 과정
1. 로컬 HTTP 서버 기동 (port 8889)
2. `generate_figma_design` → captureId 발급
3. 브라우저에서 HTML 열기 (capture.js 자동 로드)
4. 5초 간격 폴링 → completed
5. Figma 파일에 프레임 삽입됨

## 8. 트러블슈팅

### Figma MCP 도구가 안 보임
```bash
# 1. MCP 서버 상태 확인
claude mcp list

# 2. "Needs authentication" → Claude Code 재시작 후 Figma 로그인
# 3. "Failed to connect" → 네트워크 확인, https://mcp.figma.com/mcp 접근 가능한지
```

### 캡처가 pending 상태에서 안 넘어감
- 로컬 서버 실행 확인: `curl http://localhost:8889`
- 브라우저가 정상적으로 열렸는지 확인
- `figmadelay` 값 늘리기 (기본 2000ms → 5000ms)

### CSP 에러 (외부 사이트 캡처 시)
- Playwright MCP 사용 필요 (CSP 헤더 제거)
- 로컬 HTML은 CSP 영향 없음

### 포트 충돌
```bash
netstat -ano | findstr :8889
python cli.py capture <run_id> --post TK4 --port 8891
```

## 9. 다른 기기에서 사용

GitHub에서 클론 후:
```bash
git clone https://github.com/davidcho0326/search2figma.git
cd search2figma

# 1. Python 의존성
pip install -r requirements.txt

# 2. Figma Plugin 설치
claude plugin install figma@claude-plugins-official

# 3. .env에 API 키 설정
cp .env.example .env
# GOOGLE_API_KEY, SCRAPECREATORS_API_KEY 입력

# 4. 실행
python cli.py run "검색어" --select auto
```

동일한 Figma 계정이면 바로 사용 가능합니다.
