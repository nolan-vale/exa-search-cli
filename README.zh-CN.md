<div align="center">

← [English](README.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# exa-search-cli

**[Exa](https://exa.ai) 的命令行工具 — 神经网络 Web 搜索、URL 爬取、AI 研究任务。**

[![PyPI](https://img.shields.io/pypi/v/exa-search-cli?color=0ea5e9&label=PyPI)](https://pypi.org/project/exa-search-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-0ea5e9.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5e9.svg)](../LICENSE)

</div>

---

`exa-cli` 将 [Exa API](https://exa.ai) 封装为四个终端命令。Exa 按语义搜索，而非关键词匹配。所有命令支持 `--json` 输出，适合脚本、AI 代理和流水线使用。

## 60 秒上手

**第一步 — 安装：**
```bash
uv tool install exa-search-cli
```

> 没有 `uv`？先运行 `curl -LsSf https://astral.sh/uv/install.sh | sh`，或使用 `pip install exa-search-cli`。

**第二步 — 获取 API 密钥：**  
访问 [exa.ai](https://exa.ai) → 注册（有免费套餐）→ Dashboard → API Keys。

**第三步 — 设置密钥：**
```bash
export EXA_API_KEY=你的密钥
# 添加到 ~/.zshrc 或 ~/.bashrc 以永久生效
```

**第四步 — 搜索：**
```bash
exa-search "transformer 注意力机制" --category "research paper"
```

## 命令

| 命令 | 功能 |
|---|---|
| `exa-search <查询>` | 语义 Web 搜索。支持类型过滤、日期范围、域名过滤、查找相似页面。 |
| `exa-crawl <url>` | 获取任意 URL 的干净可读文本。 |
| `exa-research <主题>` | 提交深度研究任务，立即返回 `research_id`。 |
| `exa-research-status <research-id>` | 查询 `exa-research` 提交的任务的状态/结果。 |

所有命令支持 `--json`（结构化输出，可与 `jq` 或 AI 代理配合使用）。

## 示例

```bash
# 查找与任意 URL 相似的页面
exa-search --similar https://github.com/astral-sh/uv

# 2025 年的 AI 研究论文
exa-search "视觉语言模型" --category "research paper" --start-date 2025-01-01

# 只搜索 GitHub 仓库，输出 URL 列表
exa-search "async rust runtime" --include-domain github.com --json | jq -r '.results[].url'

# 抓取任意页面的干净文本
exa-crawl https://example.com -c 8000

# AI 深度研究
exa-research "量子纠错的现状"
exa-research-status <research-id>   # 查看进度 / 获取结果
```

## 参数参考

**`exa-search`**

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-n` / `--num-results` | `8` | 返回结果数量 |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--category` | — | `news` · `tweet` · `github` · `research paper` · `pdf` 等 |
| `--start-date` | — | 发布日期不早于 `YYYY-MM-DD` |
| `--end-date` | — | 发布日期不晚于 `YYYY-MM-DD` |
| `--include-domain` | — | 只包含这些域名（逗号分隔） |
| `--exclude-domain` | — | 排除这些域名（逗号分隔） |
| `--similar` | — | 查找与此 URL 相似的页面 |
| `--json` | off | 原始 JSON 输出 |

→ **[完整文档](docs/USAGE.zh-CN.md)** · [English](docs/USAGE.md)

---

Built by [Nolan Vale](https://github.com/nolan-vale)  
Part of **Nolan Vale Tools** — practical open-source utilities for search, automation, AI agents, and developer workflows.
