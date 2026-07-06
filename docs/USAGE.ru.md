# exa-search-cli — Полная документация (русский)

← [Назад в README](../README.ru.md) · [English version](USAGE.md)

## Установка

```bash
uv tool install exa-search-cli
```

```bash
export EXA_API_KEY=твой-ключ   # получить на exa.ai — есть бесплатный тариф
# Сохранить навсегда: echo 'export EXA_API_KEY=твой-ключ' >> ~/.zshrc
```

## Команды

### exa-search — нейронный веб-поиск

```
exa-search <запрос> [--similar <url>] [параметры]
```

| Флаг | По умолчанию | Описание |
|---|---|---|
| `-n` / `--num-results` | `8` | Количество результатов |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--text` | off | Получить и показать полный текст страницы |
| `--category` | — | Фильтр по типу контента (см. ниже) |
| `--start-date` | — | Опубликовано после `YYYY-MM-DD` |
| `--end-date` | — | Опубликовано до `YYYY-MM-DD` |
| `--include-domain` | — | Только эти домены (через запятую) |
| `--exclude-domain` | — | Исключить эти домены (через запятую) |
| `--similar` | — | Найти похожие страницы по URL |
| `--json` | off | Сырой JSON-вывод |

**Типы контента (--category):**
`news` · `tweet` · `github` · `paper` · `company` · `research paper` · `financial report` · `personal site` · `pdf` · `linkedin profile`

**Примеры:**
```bash
exa-search "последние архитектуры больших языковых моделей" -n 10
exa-search "transformer attention" --category "research paper" --start-date 2025-01-01
exa-search "async rust" --include-domain github.com --json | jq -r '.results[].url'
exa-search --similar https://github.com/astral-sh/uv
exa-search "python туториал" --exclude-domain medium.com
```

---

### exa-crawl — извлечение текста из URL

```
exa-crawl <url> [параметры]
```

| Флаг | По умолчанию | Описание |
|---|---|---|
| `-c` / `--max-chars` | `5000` | Максимум символов для возврата |
| `--json` | off | Сырой JSON-вывод |

```bash
exa-crawl https://example.com
exa-crawl https://arxiv.org/abs/2303.08774 -c 10000
exa-crawl https://example.com --json
```

---

### exa-research — глубокое AI-исследование

```
exa-research <тема> [параметры]
```

| Флаг | По умолчанию | Описание |
|---|---|---|
| `-m` / `--model` | `exa-research` | `exa-research-fast` · `exa-research` · `exa-research-pro` |
| `--json` | off | Сырой JSON-вывод |

```bash
exa-research "текущее состояние квантовой коррекции ошибок"
exa-research "vision language models 2025" --model exa-research-pro
```

`exa-research` только запускает задачу — печатает `research_id` и сразу завершается. Статус и результат проверяются через `exa-research-status`.

---

### exa-research-status — статус / результат задачи

```
exa-research-status <research-id> [параметры]
```

| Флаг | По умолчанию | Описание |
|---|---|---|
| `--json` | off | Сырой JSON-вывод |

```bash
exa-research-status r_01k...
exa-research-status r_01k... --json
```

Статус — один из `pending`, `running`, `completed`, `failed`, `canceled`. При `completed` печатается синтезированный ответ (`.output.content` в `--json`). При `failed` — сообщение об ошибке (`.error`).

---

## Скрипты и пайплайны

```bash
# Извлечь все URL
exa-search "rust web frameworks" --json | jq -r '.results[].url'

# Поиск + краулинг первого результата
exa-search "pytorch tutorial" --json \
  | jq -r '.results[0].url' \
  | xargs exa-crawl -c 8000

# Фильтр результатов по домену
exa-search "frameworks" --json \
  | jq '[.results[] | select(.url | test("github\\.com"))]'
```
