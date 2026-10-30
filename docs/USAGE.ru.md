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
| `-t` / `--type` | `auto` | `auto` · `lite` · `fast` · `instant` · `deep-lite` · `deep` · `deep-reasoning` · `keyword` · `neural` |
| `--text` | off | Получить текст; preview в терминале по умолчанию 2000 символов |
| `--max-chars` | — | Лимит текста на результат; требует `--text` |
| `--objective` | — | Цель исследования и предпочтения источников; до 4096 символов |
| `--max-age-hours` | — | Возраст контента: `0` — получить свежий, `-1` — только cache, `1–720` — максимальный возраст в часах |
| `--timeout` | `60` | HTTP connect/read timeout в секундах |
| `--version` | — | Показать версию без credentials |
| `--category` | — | Фильтр по типу контента (см. ниже) |
| `--start-date` | — | Опубликовано после `YYYY-MM-DD` |
| `--end-date` | — | Опубликовано до `YYYY-MM-DD` |
| `--include-domain` | — | Только эти домены (через запятую) |
| `--exclude-domain` | — | Исключить эти домены (через запятую) |
| `--similar` | — | Найти похожие страницы по URL |
| `--json` | off | Структурированный JSON-вывод |
| `--compact` | off | Компактный JSON с источниками, стоимостью и статусами; включает JSON-режим |

**Типы контента (--category):**
`news` · `tweet` · `github` · `paper` · `company` · `research paper` · `financial report` · `personal site` · `pdf` · `linkedin profile`

**Примеры:**
```bash
exa-search "последние архитектуры больших языковых моделей" -n 10
exa-search "transformer attention" --category publication --start-date 2025-01-01
exa-search "async rust" --include-domain github.com --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
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
| `--query` | — | Извлечь фрагменты по вопросу со всей страницы вместо её начала |
| `--max-age-hours` | — | `0` — свежий fetch, `-1` — только cache, `1–720` — максимальный возраст |
| `--json` | off | Структурированный JSON-вывод |
| `--compact` | off | JSON в одну строку без пустых и декоративных полей |

```bash
exa-crawl https://example.com
exa-crawl https://arxiv.org/abs/2303.08774 -c 10000
exa-crawl https://example.com --json
```

---

### Exa Agent / Research API migration

Старый `/research` закрыт. Используй `exa-agent` для создания новой задачи, `exa-agent-status` для чтения результата и `exa-agent-cancel` для отмены. Старые команды завершаются с инструкцией миграции без API-вызова. `--dry-run` работает без ключа и сети. Создание Agent run оплачивается; `--max-cost` задаёт предел для `auto`/`ultra`. Проверка этой версии покрывает контракт запросов и чтение API; завершённый платный run не проверялся.

```bash
exa-agent "Compare local providers" --max-cost 1 --dry-run
exa-agent "Compare local providers" --max-cost 1 --json
exa-agent-status agent_run_REPLACE_WITH_RETURNED_ID --json
exa-agent-cancel agent_run_REPLACE_WITH_RETURNED_ID --json
```

[Complete Agent command reference](USAGE.md#exa-agent).

## Скрипты и пайплайны

```bash
# Извлечь все URL
exa-search "rust web frameworks" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'

# Поиск + краулинг первого результата
exa-search "pytorch tutorial" --json \
  | jq -r '(if type=="array" then . else (.results // []) end)[0].url // empty' \
  | xargs exa-crawl -c 8000

# Фильтр результатов по домену
exa-search "frameworks" --json \
  | jq '[(if type=="array" then . else (.results // []) end)[] | select(.url | test("github\\.com"))]'
```

Пакетное чтение: `exa-crawl URL1 URL2 -c 12000 --json` (до 100 URL). Текстовый вывод соблюдает `-c`. Подробнее об обработке ошибок и сохранённом JSON-контракте: [usage guide](USAGE.md#research-workflow-and-reliability-016).
