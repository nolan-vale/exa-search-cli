<div align="center">

← [English](README.md) · [中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [한국어](README.ko.md)

# exa-cli

**[Exa](https://exa.ai) の CLI ツール — ニューラル Web 検索・URL クロール・AI リサーチをターミナルから。**

[![PyPI](https://img.shields.io/pypi/v/exa-cli?color=0ea5e9&label=PyPI)](https://pypi.org/project/exa-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-0ea5e9.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5e9.svg)](../LICENSE)

</div>

---

`exa-cli` は [Exa API](https://exa.ai) を 3 つのターミナルコマンドにラップします。Exa はキーワードではなく意味で検索します。すべてのコマンドはスクリプト・AI エージェント・パイプライン向けに `--json` をサポートします。

## 60 秒で始める

**ステップ 1 — インストール：**
```bash
uv tool install exa-cli
```

> `uv` がない場合は `curl -LsSf https://astral.sh/uv/install.sh | sh` を実行するか、`pip install exa-search-cli` を使用してください。

**ステップ 2 — API キーを取得：**  
[exa.ai](https://exa.ai) → サインアップ（無料プランあり）→ Dashboard → API Keys。

**ステップ 3 — キーを設定：**
```bash
export EXA_API_KEY=あなたのキー
# ~/.zshrc や ~/.bashrc に追加すると永続化できます
```

**ステップ 4 — 検索：**
```bash
exa-search "トランスフォーマーの仕組み" --category "research paper"
```

## コマンド

| コマンド | 機能 |
|---|---|
| `exa-search <クエリ>` | 意味による Web 検索。タイプ・日付・ドメインフィルタリング、類似ページ検索。 |
| `exa-crawl <url>` | 任意の URL からクリーンなテキストを取得（HTML なし）。 |
| `exa-research <トピック>` | 深層リサーチタスク。Exa AI が Web を読んで回答を合成。 |

すべてのコマンドは `--json` に対応（`jq`、スクリプト、AI エージェントと連携可能）。

## 使用例

```bash
# 任意の URL に類似したページを検索
exa-search --similar https://github.com/astral-sh/uv

# 2025 年の AI 研究論文
exa-search "視覚言語モデル" --category "research paper" --start-date 2025-01-01

# GitHub リポジトリのみ、URL リストを取得
exa-search "async rust runtime" --include-domain github.com --json | jq -r '.results[].url'

# 任意ページのクリーンなテキストを取得
exa-crawl https://example.com -c 8000

# AI による深層リサーチ
exa-research "量子エラー訂正の現状"
```

## オプションリファレンス

**`exa-search`**

| フラグ | デフォルト | 説明 |
|---|---|---|
| `-n` / `--num-results` | `8` | 返す結果数 |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--category` | — | `news` · `tweet` · `github` · `research paper` · `pdf` など |
| `--start-date` | — | 指定日以降に公開 `YYYY-MM-DD` |
| `--end-date` | — | 指定日以前に公開 `YYYY-MM-DD` |
| `--include-domain` | — | このドメインのみ含める（カンマ区切り） |
| `--exclude-domain` | — | このドメインを除外（カンマ区切り） |
| `--similar` | — | この URL に類似したページを検索 |
| `--json` | off | 生の JSON 出力 |

→ **[完全なドキュメント](docs/USAGE.md)**（英語）

---

Built by [Nolan Vale](https://github.com/nolan-vale)  
Part of **Nolan Vale Tools** — practical open-source utilities for search, automation, AI agents, and developer workflows.
