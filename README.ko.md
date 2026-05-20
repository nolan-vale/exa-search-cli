<div align="center">

← [English](README.md) · [中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md)

# exa-cli

**[Exa](https://exa.ai) CLI — 뉴럴 웹 검색, URL 크롤링, AI 리서치를 터미널에서.**

[![PyPI](https://img.shields.io/pypi/v/exa-cli?color=0ea5e9&label=PyPI)](https://pypi.org/project/exa-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-0ea5e9.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5e9.svg)](../LICENSE)

</div>

---

`exa-cli`는 [Exa API](https://exa.ai)를 세 개의 터미널 명령어로 감쌉니다. Exa는 키워드가 아닌 의미로 검색합니다. 모든 명령어는 스크립트, AI 에이전트, 파이프라인을 위한 `--json` 출력을 지원합니다.

## 60초 시작 가이드

**1단계 — 설치:**
```bash
uv tool install exa-cli
```

> `uv`가 없다면 `curl -LsSf https://astral.sh/uv/install.sh | sh`를 실행하거나, `pip install exa-search-cli`를 사용하세요.

**2단계 — API 키 발급:**  
[exa.ai](https://exa.ai) → 회원가입 (무료 플랜 있음) → Dashboard → API Keys.

**3단계 — 키 설정:**
```bash
export EXA_API_KEY=발급받은-키
# ~/.zshrc 또는 ~/.bashrc에 추가하면 영구 적용됩니다
```

**4단계 — 검색:**
```bash
exa-search "트랜스포머 작동 원리" --category "research paper"
```

## 명령어

| 명령어 | 기능 |
|---|---|
| `exa-search <쿼리>` | 의미 기반 웹 검색. 타입·날짜·도메인 필터링. 유사 페이지 검색. |
| `exa-crawl <url>` | 어떤 URL에서도 깔끔한 텍스트 추출 (HTML 없음). |
| `exa-research <주제>` | 심층 리서치 태스크. Exa AI가 웹을 읽고 답변을 합성. |

모든 명령어는 `--json` 지원 (`jq`, 스크립트, AI 에이전트와 연동 가능).

## 예시

```bash
# 어떤 URL과 유사한 페이지 찾기
exa-search --similar https://github.com/astral-sh/uv

# 2025년 AI 연구 논문
exa-search "비전 언어 모델" --category "research paper" --start-date 2025-01-01

# GitHub 저장소만, URL 목록 추출
exa-search "async rust runtime" --include-domain github.com --json | jq -r '.results[].url'

# 어떤 페이지든 깔끔한 텍스트 추출
exa-crawl https://example.com -c 8000

# AI 심층 리서치
exa-research "양자 오류 수정의 현황"
```

## 옵션 레퍼런스

**`exa-search`**

| 플래그 | 기본값 | 설명 |
|---|---|---|
| `-n` / `--num-results` | `8` | 반환할 결과 수 |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--category` | — | `news` · `tweet` · `github` · `research paper` · `pdf` 등 |
| `--start-date` | — | 이 날짜 이후 게시 `YYYY-MM-DD` |
| `--end-date` | — | 이 날짜 이전 게시 `YYYY-MM-DD` |
| `--include-domain` | — | 이 도메인만 포함 (쉼표 구분) |
| `--exclude-domain` | — | 이 도메인 제외 (쉼표 구분) |
| `--similar` | — | 이 URL과 유사한 페이지 검색 |
| `--json` | off | 원시 JSON 출력 |

→ **[전체 문서](docs/USAGE.md)**（영어）

---

Built by [Nolan Vale](https://github.com/nolan-vale)  
Part of **Nolan Vale Tools** — practical open-source utilities for search, automation, AI agents, and developer workflows.
