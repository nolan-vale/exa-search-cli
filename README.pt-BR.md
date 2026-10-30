# exa-search-cli

> A Exa desativou `/research`. Na versão 0.1.7 use `exa-agent`, `exa-agent-status` e `exa-agent-cancel`; `exa-research*` apenas mostra instruções de migração, sem chamadas nem tarefas pagas automáticas. `--dry-run` permite revisar a solicitação sem rede. [Guia](docs/USAGE.md#exa-agent).

**Integração de linha de comando com Exa para pesquisas repetíveis: busca, recuperação de texto e tarefas de pesquisa.**

[English](README.md) · [中文](README.zh-CN.md) · [Русский](README.ru.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Objetivo e contribuição

Conecta os serviços existentes da Exa a scripts e agentes de IA. A Exa fornece a busca e a pesquisa; este repositório implementa uma integração CLI, não um mecanismo de busca ou modelo de IA próprio.

Criado com agentes de programação de IA como parte do trabalho independente de [Nolan Vale](https://github.com/nolan-vale). Sua contribuição é definir requisitos, orientar a implementação, verificar resultados e iterar.

## Instalação

```bash
uv tool install exa-search-cli
export EXA_API_KEY=your-key
exa-search "document review workflow" --json
```

Também é possível usar `pip install exa-search-cli` em um ambiente Python adequado. Obtenha uma chave da Exa e não a salve no repositório.

## Comandos

| Comando | Objetivo |
|---|---|
| `exa-search <query>` | Buscar fontes ou páginas similares com filtros de data, domínio e categoria |
| `exa-crawl <url>` | Solicitar texto legível de uma página pela Exa |
| `exa-agent <query>` | Criar uma tarefa assíncrona Exa Agent |
| `exa-agent-status <run-id>` | Consultar o resultado de Agent |
| `exa-agent-cancel <run-id>` | Cancelar uma tarefa de Agent |

Os comandos aceitam `--json`. A busca aceita `--num-results`, `--type`, `--text`, `--category`, `--start-date`, `--end-date`, `--include-domain`, `--exclude-domain` e `--similar`.

```bash
exa-search --similar https://github.com/astral-sh/uv
exa-crawl https://example.com -c 8000
exa-agent "document processing approaches" --max-cost 1 --json
exa-agent-status agent_run_REPLACE_WITH_RETURNED_ID --json
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

## Limites

As solicitações são enviadas a um serviço externo. Os comandos de pesquisa criam tarefas na Exa; o fluxo não é totalmente local nem somente de leitura. A recuperação depende do provedor e do acesso à página; não é garantida para qualquer URL. Confira fontes e resultados gerados antes de usá-los.

[Documentação completa](docs/USAGE.md) · [Visão geral atualizada](README.md).

[MIT](LICENSE) — Nolan Vale. **Nolan Vale Tools** é o nome usado para seus projetos públicos independentes.
