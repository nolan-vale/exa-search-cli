# exa-search-cli

**반복적인 조사를 위한 Exa CLI 연동: 출처 검색, 페이지 텍스트 조회, 조사 작업을 지원합니다.**

[English](README.md) · [中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md)

## 목적과 기여

기존 Exa 서비스를 스크립트와 AI 에이전트에 연결합니다. 검색과 조사 기능은 Exa가 제공하며, 이 저장소는 CLI 연동을 구현합니다. 자체 검색 엔진이나 AI 모델이 아닙니다.

[Nolan Vale](https://github.com/nolan-vale)의 독립적인 제품 작업에서 코딩 에이전트와 함께 만들었습니다. 담당 역할은 요구사항 정의, AI 지원 구현 지시, 결과 확인, 반복 개선입니다.

## 설치

```bash
uv tool install exa-search-cli
export EXA_API_KEY=your-key
exa-search "document review workflow" --json
```

적절한 Python 환경에서 `pip install exa-search-cli`도 사용할 수 있습니다. Exa에서 API 키를 발급받고 저장소에 올리지 마세요.

## 명령

| 명령 | 목적 |
|---|---|
| `exa-search <query>` | 날짜, 도메인, 카테고리 필터로 출처 또는 유사 페이지 검색 |
| `exa-crawl <url>` | Exa를 통해 읽기 쉬운 페이지 텍스트 요청 |
| `exa-research <topic>` | Exa에 조사 작업 생성 |
| `exa-research-status <research-id>` | 상태 확인과 결과 조회 |

각 명령은 `--json`을 지원합니다. 검색 옵션은 `--num-results`, `--type`, `--text`, `--category`, `--start-date`, `--end-date`, `--include-domain`, `--exclude-domain`, `--similar`입니다.

```bash
exa-search --similar https://github.com/astral-sh/uv
exa-crawl https://example.com -c 8000
exa-research "document processing approaches" --json
exa-research-status <research-id> --json
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

## 제한

요청은 외부 서비스로 전송됩니다. 조사 명령은 Exa에 작업을 생성하므로 완전한 로컬 처리나 읽기 전용 작업이 아닙니다. 텍스트 조회는 제공자 기능과 페이지 접근 가능 여부에 따라 달라지며 모든 URL에서 성공한다고 보장하지 않습니다. 생성된 결과는 원문 출처와 대조하세요.

[전체 문서](docs/USAGE.md) · [최신 개요](README.md).

[MIT](LICENSE) — Nolan Vale. **Nolan Vale Tools**는 독립적인 공개 프로젝트에 사용하는 이름입니다.
