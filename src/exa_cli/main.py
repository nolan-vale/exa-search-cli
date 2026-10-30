import argparse
import json
import os
import re
import sys
import textwrap

from exa_py import Exa
from exa_py.api import ContentsOptions

from exa_cli._common import (
    add_common_args,
    api_call,
    cache_age_hours,
    http_url,
    iso_date,
    positive_int,
    result_count,
)
from exa_cli._output import compact_payload, warn_text_limit

TEXT_PREVIEW_LEN = 2000
RESULT_LIST_KEYS = ("results", "data", "items")

CATEGORIES = [
    "publication",
    "people",
    "news",
    "tweet",
    "github",
    "paper",
    "company",
    "research paper",
    "financial report",
    "personal site",
    "pdf",
    "linkedin profile",
]


def _client(timeout: float = 60) -> Exa:
    key = os.environ.get("EXA_API_KEY", "").strip()
    if not key:
        sys.exit("EXA_API_KEY not set. Export your key: export EXA_API_KEY=your-key")
    return Exa(api_key=key, timeout=timeout)


def _to_serializable(obj):
    # Recursively unwrap SDK objects (SearchResponse, Result, cost_dollars, ...)
    # into plain dicts so nested results serialize as JSON objects, not str().
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, list | tuple):
        return [_to_serializable(item) for item in obj]
    if isinstance(obj, dict):
        return {str(key): _to_serializable(value) for key, value in obj.items()}
    if hasattr(obj, "_asdict"):
        return _to_serializable(obj._asdict())
    if hasattr(obj, "__dict__"):
        return _to_serializable(vars(obj))
    return str(obj)


def _results_json_payload(response) -> dict:
    data = _to_serializable(response)

    if isinstance(data, list):
        return {"results": data}

    if isinstance(data, dict):
        for key in RESULT_LIST_KEYS:
            if isinstance(data.get(key), list):
                payload = dict(data)
                payload["results"] = data[key]
                return payload

        payload = dict(data)
        if "results" in payload:
            payload["raw_results"] = payload["results"]
        payload["results"] = []
        return payload

    return {"results": [], "value": data}


def _dump_json(data, compact: bool = False) -> None:
    if compact:
        data = compact_payload(data)
    print(
        json.dumps(
            data,
            default=_to_serializable,
            ensure_ascii=False,
            indent=None if compact else 2,
            separators=(",", ":") if compact else None,
        )
    )


def _add_source_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="structured JSON output")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="compact JSON with source evidence, costs and statuses; implies --json",
    )
    parser.add_argument(
        "--max-age-hours",
        type=cache_age_hours,
        metavar="HOURS",
        help="content freshness: 0 = fetch fresh, -1 = cache only, 1-720 = max age",
    )


def _meta(r) -> str:
    parts = []
    if getattr(r, "published_date", None):
        parts.append(r.published_date[:10])
    if getattr(r, "author", None):
        parts.append(r.author)
    return "  ·  ".join(parts) if parts else ""


def _clean(text: str) -> str:
    text = re.sub(r"(\[\.\.\.\]\s*){2,}", "[...]\n", text)
    lines = [ln for ln in text.splitlines() if not re.fullmatch(r"\s*\d{0,3}\s*", ln)]
    return "\n".join(lines).strip()


def _snippet(r, full_text: bool = False, max_chars: int = TEXT_PREVIEW_LEN) -> str:
    text = getattr(r, "text", None) or ""
    highlights = getattr(r, "highlights", None) or []

    if full_text and text:
        preview = text[:max_chars]
        tail = "…" if len(text) > max_chars else ""
        return preview + tail

    if highlights:
        parts = []
        for h in highlights:
            cleaned = _clean(h.strip())
            if cleaned:
                parts.append(textwrap.fill(cleaned, width=100))
        return "\n\n".join(parts)

    if text:
        preview = text.strip()[:600]
        return textwrap.fill(preview + ("…" if len(text) > 600 else ""), width=100)

    return ""


def _print_results(
    results, response, full_text: bool = False, max_chars: int = TEXT_PREVIEW_LEN
) -> None:
    for i, r in enumerate(results, 1):
        title = getattr(r, "title", None) or "(no title)"
        url = getattr(r, "url", "") or getattr(r, "id", "")
        meta = _meta(r)
        snippet = _snippet(r, full_text, max_chars)

        print(f"[{i}] {title}")
        print(f"    {url}")
        if meta:
            print(f"    {meta}")
        if snippet:
            indented = "\n".join("    " + line for line in snippet.splitlines())
            print(indented)
        print()

    cost = getattr(response, "cost_dollars", None)
    t = getattr(response, "search_time", None)
    cost_str = f"${cost.total:.4f}" if cost and hasattr(cost, "total") else ""
    time_str = f"{t / 1000:.1f}s" if t else ""
    footer = "  ·  ".join(filter(None, [f"{len(results)} results", cost_str, time_str]))
    print(f"── {footer} ──")


def _split_domains(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [d.strip() for d in value.split(",") if d.strip()]


def search() -> None:
    p = argparse.ArgumentParser(
        description="Exa web search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  exa-search "python async frameworks" -n 5
  exa-search "latest AI news" --category news --start-date 2024-01-01
  exa-search "rust web" --include-domain github.com,crates.io
  exa-search "similar to this" --similar https://example.com
  exa-search "query" --json | jq '.'
""",
    )
    p.add_argument("query", nargs="?", help="search query (omit when using --similar)")
    p.add_argument("-n", "--num-results", type=result_count, default=8)
    p.add_argument(
        "-t",
        "--type",
        choices=[
            "auto",
            "lite",
            "fast",
            "instant",
            "deep-lite",
            "deep",
            "deep-reasoning",
            "keyword",
            "neural",
        ],
        default="auto",
    )
    p.add_argument(
        "--text",
        action="store_true",
        help="fetch page text (terminal preview: 2000 chars)",
    )
    p.add_argument(
        "--max-chars", type=positive_int, help="text limit per result; requires --text"
    )
    p.add_argument(
        "--category",
        choices=CATEGORIES,
        metavar="CATEGORY",
        help=f"filter by content type: {', '.join(CATEGORIES)}",
    )
    p.add_argument(
        "--start-date",
        type=iso_date,
        metavar="YYYY-MM-DD",
        help="published on or after this date",
    )
    p.add_argument(
        "--end-date",
        type=iso_date,
        metavar="YYYY-MM-DD",
        help="published on or before this date",
    )
    p.add_argument(
        "--include-domain",
        metavar="DOMAINS",
        help="only include these domains (comma-separated)",
    )
    p.add_argument(
        "--exclude-domain",
        metavar="DOMAINS",
        help="exclude these domains (comma-separated)",
    )
    p.add_argument(
        "--similar", type=http_url, metavar="URL", help="find pages similar to this URL"
    )
    p.add_argument(
        "--objective",
        help="broader search goal and source preferences (up to 4096 characters)",
    )
    _add_source_args(p)
    add_common_args(p)
    args = p.parse_args()

    if not (args.query and args.query.strip()) and not args.similar:
        p.error("provide a query or --similar URL")
    if args.max_chars and not args.text:
        p.error("--max-chars requires --text")
    if args.objective is not None:
        if not args.objective.strip() or len(args.objective) > 4096:
            p.error("--objective must be non-blank and at most 4096 characters")
        if args.similar:
            p.error("--objective is not supported with --similar")
    if args.type == "lite" and args.max_age_hours is not None and not args.similar:
        p.error("--max-age-hours is not supported with --type lite; use auto or crawl")
    if args.start_date and args.end_date and args.start_date > args.end_date:
        p.error("--start-date must be on or before --end-date")
    category = (
        "publication" if args.category in ("paper", "research paper") else args.category
    )
    if category in ("company", "people") and (args.start_date or args.end_date):
        p.error("date filters are not supported for company/people categories")
    if category == "people" and args.exclude_domain:
        p.error("--exclude-domain is not supported for the people category")
    for name in ("include_domain", "exclude_domain"):
        value = getattr(args, name)
        if value is not None and not _split_domains(value):
            p.error(f"--{name.replace('_', '-')} must contain at least one domain")

    exa = _client(args.timeout)
    contents = (
        ContentsOptions(
            text={"max_characters": args.max_chars} if args.max_chars else True
        )
        if args.text
        else ContentsOptions(highlights=True)
    )
    if args.max_age_hours is not None:
        contents["max_age_hours"] = args.max_age_hours

    kwargs: dict = dict(
        num_results=args.num_results,
        type=args.type,
        contents=contents,
    )
    if args.objective is not None:
        kwargs["objective"] = args.objective
    if category:
        kwargs["category"] = category
    if args.start_date:
        kwargs["start_published_date"] = f"{args.start_date}T00:00:00.000Z"
    if args.end_date:
        kwargs["end_published_date"] = f"{args.end_date}T23:59:59.999Z"
    if args.include_domain:
        kwargs["include_domains"] = _split_domains(args.include_domain)
    if args.exclude_domain:
        kwargs["exclude_domains"] = _split_domains(args.exclude_domain)

    if args.similar:
        result = api_call(
            exa.find_similar,
            args.similar,
            **{k: v for k, v in kwargs.items() if k not in ("type",)},
        )
    else:
        result = api_call(exa.search, args.query, **kwargs)

    payload = _results_json_payload(result)
    if args.json or args.compact:
        _dump_json(payload, compact=args.compact)
    else:
        _print_results(
            result.results,
            result,
            full_text=args.text,
            max_chars=args.max_chars or TEXT_PREVIEW_LEN,
        )
    if args.text and args.max_chars:
        warn_text_limit(payload, args.max_chars)


def crawl() -> None:
    p = argparse.ArgumentParser(
        description="Exa URL crawl — extract readable text or query-focused excerpts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  exa-crawl https://example.com
  exa-crawl https://arxiv.org/abs/2303.08774 -c 10000
  exa-crawl https://example.com --json
""",
    )
    p.add_argument("url", nargs="+", type=http_url, help="one or more URLs (up to 100)")
    p.add_argument(
        "-c",
        "--max-chars",
        type=positive_int,
        default=5000,
        help="max characters to return (default: 5000)",
    )
    p.add_argument(
        "--query",
        help="extract query-focused highlights from the whole page instead of its start",
    )
    _add_source_args(p)
    add_common_args(p)
    args = p.parse_args()
    if len(args.url) > 100:
        p.error("at most 100 URLs may be requested at once")
    if args.query is not None and not args.query.strip():
        p.error("--query must not be blank")

    exa = _client(args.timeout)
    if args.query is not None:
        # Explicit False prevents the SDK from adding a full-text request.
        options = {
            "text": False,
            "highlights": {"query": args.query, "max_characters": args.max_chars},
        }
    else:
        options = {"text": {"max_characters": args.max_chars}}
    if args.max_age_hours is not None:
        options["max_age_hours"] = args.max_age_hours
    result = api_call(exa.get_contents, args.url, **options)

    payload = _results_json_payload(result)
    if args.json or args.compact:
        _dump_json(payload, compact=args.compact)
    else:
        _print_results(result.results, result, full_text=True, max_chars=args.max_chars)
    if args.query is None:
        warn_text_limit(payload, args.max_chars)
    failures = [
        item for item in payload.get("statuses") or [] if item.get("status") == "error"
    ]
    if failures:
        print(
            f"Exa could not retrieve {len(failures)} URL(s); see statuses in --json output",
            file=sys.stderr,
        )
        if not payload["results"]:
            raise SystemExit(1)


def research() -> None:
    p = argparse.ArgumentParser(
        description="Exa deep research — AI-powered research task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  exa-research "explain transformer attention mechanisms"
  exa-research "quantum computing current state" --model exa-research-pro
  exa-research "topic" --json
""",
    )
    p.add_argument("topic")
    p.add_argument(
        "-m",
        "--model",
        default="exa-research",
        choices=["exa-research-fast", "exa-research", "exa-research-pro"],
    )
    p.add_argument("--json", action="store_true", help="structured JSON output")
    add_common_args(p)
    args = p.parse_args()

    if not args.topic.strip():
        p.error("topic must not be empty")
    exa = _client(args.timeout)
    result = api_call(exa.research.create, instructions=args.topic, model=args.model)

    if args.json:
        _dump_json(result)
    else:
        print("Research task created")
        print(f"  ID:     {result.research_id}")
        print(f"  Model:  {result.model}")
        print(f"  Status: {result.status}")
        print(f"\nCheck status: exa-research-status {result.research_id}")


def research_status() -> None:
    p = argparse.ArgumentParser(
        description="Exa deep research — check status and fetch the result of a research task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  exa-research-status <research-id>
  exa-research-status <research-id> --json
""",
    )
    p.add_argument("research_id")
    p.add_argument("--json", action="store_true", help="structured JSON output")
    add_common_args(p)
    args = p.parse_args()

    exa = _client(args.timeout)
    result = api_call(exa.research.get, args.research_id)

    if args.json:
        _dump_json(result)
        return

    print(f"Status: {result.status}")
    if result.status == "completed":
        print("\nResult:")
        print(result.output.content)
    elif result.status == "failed":
        print(f"\nError: {result.error}")
    else:
        print("Still in progress — check again shortly.")
