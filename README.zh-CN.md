# exa-search-cli

**用于重复性研究任务的 Exa 命令行集成：搜索来源、获取网页文本并提交研究任务。**

[English](README.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## 用途与贡献

将现有 Exa 服务连接到脚本和 AI 代理。搜索与研究能力由 Exa 提供，本仓库实现的是 CLI 集成，并非自行开发的搜索引擎或 AI 模型。

本项目由 [Nolan Vale](https://github.com/nolan-vale) 在独立产品实践中使用编码代理完成。其贡献包括定义需求、指导 AI 辅助实现、检查结果并迭代。

## 安装

```bash
uv tool install exa-search-cli
export EXA_API_KEY=your-key
exa-search "document review workflow" --json
```

也可在合适的 Python 环境中使用 `pip install exa-search-cli`。请向 Exa 获取 API 密钥，不要将其提交到仓库。

## 命令

| 命令 | 用途 |
|---|---|
| `exa-search <query>` | 搜索来源或相似页面，支持日期、域名和类别过滤 |
| `exa-crawl <url>` | 通过 Exa 请求可读网页文本 |
| `exa-research <topic>` | 在 Exa 上创建研究任务 |
| `exa-research-status <research-id>` | 查询状态并获取结果 |

各命令支持 `--json`。搜索参数包括 `--num-results`、`--type`、`--text`、`--category`、`--start-date`、`--end-date`、`--include-domain`、`--exclude-domain` 和 `--similar`。

```bash
exa-search --similar https://github.com/astral-sh/uv
exa-crawl https://example.com -c 8000
exa-research "document processing approaches" --json
exa-research-status <research-id> --json
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

## 限制

请求会发送到外部服务。研究命令会在 Exa 上创建任务，因此该流程并非完全本地或只读。文本获取取决于服务提供方和页面可访问性，不保证支持所有 URL。使用生成结果前应核对来源。

[中文完整文档](docs/USAGE.zh-CN.md) · [English](docs/USAGE.md) · [最新概览](README.md)。

[MIT](LICENSE) — Nolan Vale。**Nolan Vale Tools** 是其独立公开项目所使用的名称。
