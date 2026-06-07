# exa-search-cli — 完整文档（中文）

← [返回 README](../README.zh-CN.md) · [English version](USAGE.md)

## 安装

```bash
uv tool install exa-search-cli
```

```bash
export EXA_API_KEY=你的密钥   # 在 exa.ai 获取，有免费套餐
# 持久化：echo 'export EXA_API_KEY=你的密钥' >> ~/.zshrc
```

## 命令

### exa-search — 神经网络 Web 搜索

```
exa-search <查询> [--similar <url>] [选项]
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-n` / `--num-results` | `8` | 返回结果数量 |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--text` | 关闭 | 获取并显示完整页面文本 |
| `--category` | — | 内容类型过滤（见下方） |
| `--start-date` | — | 发布日期不早于 `YYYY-MM-DD` |
| `--end-date` | — | 发布日期不晚于 `YYYY-MM-DD` |
| `--include-domain` | — | 只包含这些域名（逗号分隔） |
| `--exclude-domain` | — | 排除这些域名（逗号分隔） |
| `--similar` | — | 查找与此 URL 相似的页面 |
| `--json` | 关闭 | 原始 JSON 输出 |

**内容类型 (--category)：**
`news` · `tweet` · `github` · `paper` · `company` · `research paper` · `financial report` · `personal site` · `pdf` · `linkedin profile`

**示例：**
```bash
exa-search "最新的大语言模型架构" -n 10
exa-search "transformer attention" --category "research paper" --start-date 2025-01-01
exa-search "async rust" --include-domain github.com --json | jq -r '.results[].url'
exa-search --similar https://github.com/astral-sh/uv
exa-search "python 教程" --exclude-domain medium.com
```

---

### exa-crawl — URL 内容提取

```
exa-crawl <url> [选项]
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-c` / `--max-chars` | `5000` | 最大返回字符数 |
| `--json` | 关闭 | 原始 JSON 输出 |

```bash
exa-crawl https://example.com
exa-crawl https://arxiv.org/abs/2303.08774 -c 10000
exa-crawl https://example.com --json
```

---

### exa-research — AI 深度研究

```
exa-research <主题> [选项]
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-m` / `--model` | `exa-research` | `exa-research` 或 `exa-research-pro` |
| `--json` | 关闭 | 原始 JSON 输出 |

```bash
exa-research "量子纠错的现状"
exa-research "视觉语言模型 2025" --model exa-research-pro
```

---

## 脚本和管道示例

```bash
# 提取所有 URL
exa-search "rust web frameworks" --json | jq -r '.results[].url'

# 搜索 + 爬取第一个结果
exa-search "pytorch tutorial" --json \
  | jq -r '.results[0].url' \
  | xargs exa-crawl -c 8000

# 按域名过滤
exa-search "frameworks" --json \
  | jq '[.results[] | select(.url | test("github\\.com"))]'
```
