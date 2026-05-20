import argparse
import json
import os
import re
import sys
import textwrap

from exa_py import Exa
from exa_py.api import ContentsOptions

TEXT_PREVIEW_LEN = 2000

CATEGORIES = [
    "news", "tweet", "github", "paper", "company",
    "research paper", "financial report", "personal site",
    "pdf", "linkedin profile",
]


def _client() -> Exa:
    key = os.environ.get("EXA_API_KEY")
    if not key:
        sys.exit("EXA_API_KEY not set. Export your key: export EXA_API_KEY=your-key")
    return Exa(api_key=key)


def _dump_json(data) -> None:
    if hasattr(data, "__dict__"):
        print(json.dumps(data.__dict__, default=str, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, default=str, ensure_ascii=False, indent=2))


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


def _snippet(r, full_text: bool = False) -> str:
    text = getattr(r, "text", None) or ""
    highlights = getattr(r, "highlights", None) or []

    if full_text and text:
        preview = text[:TEXT_PREVIEW_LEN]
        tail = "…" if len(text) > TEXT_PREVIEW_LEN else ""
        return textwrap.fill(preview + tail, width=100)

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


def _print_results(results, response, full_text: bool = False) -> None:
    for i, r in enumerate(results, 1):
        title = getattr(r, "title", None) or "(no title)"
        url = getattr(r, "url", "") or getattr(r, "id", "")
        meta = _meta(r)
        snippet = _snippet(r, full_text)

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
    time_str = f"{t/1000:.1f}s" if t else ""
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
    p.add_argument("-n", "--num-results", type=int, default=8)
    p.add_argument("-t", "--type", choices=["auto", "keyword", "neural"], default="auto")
    p.add_argument("--text", action="store_true", help="fetch and show full page text")
    p.add_argument("--category", choices=CATEGORIES, metavar="CATEGORY",
                   help=f"filter by content type: {', '.join(CATEGORIES)}")
    p.add_argument("--start-date", metavar="YYYY-MM-DD", help="published on or after this date")
    p.add_argument("--end-date", metavar="YYYY-MM-DD", help="published on or before this date")
    p.add_argument("--include-domain", metavar="DOMAINS",
                   help="only include these domains (comma-separated)")
    p.add_argument("--exclude-domain", metavar="DOMAINS",
                   help="exclude these domains (comma-separated)")
    p.add_argument("--similar", metavar="URL", help="find pages similar to this URL")
    p.add_argument("--json", action="store_true", help="raw JSON output")
    args = p.parse_args()

    if not args.query and not args.similar:
        p.error("provide a query or --similar URL")

    exa = _client()
    highlights = {"num_sentences": 5, "highlights_per_url": 2}
    contents = ContentsOptions(
        text=True if args.text else False,
        highlights=highlights,
    )

    kwargs: dict = dict(
        num_results=args.num_results,
        type=args.type,
        contents=contents,
    )
    if args.category:
        kwargs["category"] = args.category
    if args.start_date:
        kwargs["start_published_date"] = args.start_date
    if args.end_date:
        kwargs["end_published_date"] = args.end_date
    if args.include_domain:
        kwargs["include_domains"] = _split_domains(args.include_domain)
    if args.exclude_domain:
        kwargs["exclude_domains"] = _split_domains(args.exclude_domain)

    if args.similar:
        result = exa.find_similar(args.similar, **{k: v for k, v in kwargs.items()
                                                    if k not in ("type",)})
    else:
        result = exa.search(args.query, **kwargs)

    if args.json:
        _dump_json(result)
    else:
        _print_results(result.results, result, full_text=args.text)


def crawl() -> None:
    p = argparse.ArgumentParser(
        description="Exa URL crawl — extract full page content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  exa-crawl https://example.com
  exa-crawl https://arxiv.org/abs/2303.08774 -c 10000
  exa-crawl https://example.com --json
""",
    )
    p.add_argument("url")
    p.add_argument("-c", "--max-chars", type=int, default=5000,
                   help="max characters to return (default: 5000)")
    p.add_argument("--json", action="store_true", help="raw JSON output")
    args = p.parse_args()

    exa = _client()
    result = exa.get_contents([args.url], text={"max_characters": args.max_chars})

    if args.json:
        _dump_json(result)
    else:
        _print_results(result.results, result, full_text=True)


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
    p.add_argument("-m", "--model", default="exa-research",
                   choices=["exa-research", "exa-research-pro"])
    p.add_argument("--json", action="store_true", help="raw JSON output")
    args = p.parse_args()

    exa = _client()
    result = exa.research.create_task(instructions=args.topic, model=args.model)

    if args.json:
        _dump_json(result)
    else:
        task_id = getattr(result, "id", None) or getattr(result, "task_id", str(result))
        status = getattr(result, "status", "submitted")
        print(f"Research task created")
        print(f"  ID:     {task_id}")
        print(f"  Model:  {args.model}")
        print(f"  Status: {status}")
        print(f"\nCheck status: exa-research-status {task_id}")
