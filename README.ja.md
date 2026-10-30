# exa-search-cli

**繰り返し行う調査のための Exa CLI 連携。情報源の検索、ページ本文の取得、調査タスクを扱います。**

[English](README.md) · [中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [한국어](README.ko.md)

## 目的と担当範囲

既存の Exa サービスをスクリプトや AI エージェントに接続します。検索・調査機能は Exa が提供し、このリポジトリは CLI 連携を実装します。独自の検索エンジンや AI モデルではありません。

[Nolan Vale](https://github.com/nolan-vale) の独立した製品づくりの一環として、コーディングエージェントと作成しました。担当は要件定義、AI 支援実装の指示、結果確認、改善です。

## インストール

```bash
uv tool install exa-search-cli
export EXA_API_KEY=your-key
exa-search "document review workflow" --json
```

適切な Python 環境で `pip install exa-search-cli` も利用できます。API キーを Exa から取得し、リポジトリに保存しないでください。

## コマンド

| コマンド | 目的 |
|---|---|
| `exa-search <query>` | 日付・ドメイン・カテゴリで絞り込み、情報源や類似ページを検索 |
| `exa-crawl <url>` | Exa 経由で読みやすいページ本文を要求 |
| `exa-research <topic>` | Exa 上に調査タスクを作成 |
| `exa-research-status <research-id>` | 状態確認と結果取得 |

各コマンドは `--json` に対応します。検索では `--num-results`、`--type`、`--text`、`--category`、`--start-date`、`--end-date`、`--include-domain`、`--exclude-domain`、`--similar` を利用できます。

```bash
exa-search --similar https://github.com/astral-sh/uv
exa-crawl https://example.com -c 8000
exa-research "document processing approaches" --json
exa-research-status <research-id> --json
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

## 制限

リクエストは外部サービスに送られます。調査コマンドは Exa 上にタスクを作成するため、完全なローカル処理や読み取り専用の処理ではありません。本文取得は提供元の機能とページへのアクセス可否に依存し、すべての URL での成功は保証されません。生成された結果は情報源と照合してください。

[完全なドキュメント](docs/USAGE.md) · [最新の概要](README.md)。

[MIT](LICENSE) — Nolan Vale。**Nolan Vale Tools** は独立した公開プロジェクトの名称です。
