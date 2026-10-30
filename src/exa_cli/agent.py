"""Exa Agent run lifecycle; no implicit polling or research delegation."""

import argparse
import json
import math
from pathlib import Path
import re

from exa_cli._common import add_common_args, api_call
from exa_cli.main import _client, _dump_json, _to_serializable


EFFORTS = ("minimal", "low", "medium", "high", "xhigh", "auto", "ultra")


def _max_cost(value: str) -> float:
    try:
        amount = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "must be a dollar amount from 1 to 100"
        ) from exc
    if not math.isfinite(amount) or not 1 <= amount <= 100:
        raise argparse.ArgumentTypeError("must be a finite dollar amount from 1 to 100")
    return amount


def _run_id(value: str) -> str:
    if value in (".", "..") or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,200}", value):
        raise argparse.ArgumentTypeError("must be an Agent run ID, not a URL or path")
    return value


def _emit(run, json_output: bool) -> dict:
    data = _to_serializable(run)
    if json_output:
        _dump_json(data)
        return data
    print(f"Run: {data['id']}")
    print(f"Status: {data['status']}")
    if data.get("stopReason"):
        print(f"Stop reason: {data['stopReason']}")
    output = data.get("output") or {}
    if output.get("text"):
        print("\n" + output["text"])
    if output.get("structured") is not None:
        print("\nStructured output:")
        _dump_json(output["structured"])
    seen = set()
    for field in output.get("grounding") or []:
        for citation in field.get("citations") or []:
            url = citation.get("url")
            if url and url not in seen:
                print(f"Source: {url}")
                seen.add(url)
    cost = data.get("costDollars") or {}
    if cost.get("total") is not None:
        print(f"Cost: ${cost['total']:.4f}")
    if data.get("error"):
        print("Error:")
        _dump_json(data["error"])
    return data


def create() -> None:
    parser = argparse.ArgumentParser(
        description="Create an asynchronous, usage-billed Exa Agent run",
        epilog="Returns immediately; retrieve the saved run ID with exa-agent-status.",
    )
    parser.add_argument("query", help="research task for Exa Agent")
    parser.add_argument("--effort", choices=EFFORTS, default="auto")
    parser.add_argument(
        "--max-cost",
        type=_max_cost,
        metavar="USD",
        help="spend cap ($1-100), for auto/ultra only; omitted = Exa's default",
    )
    parser.add_argument(
        "--system-prompt", help="source preferences or output instructions"
    )
    parser.add_argument(
        "--output-schema", type=Path, metavar="FILE", help="JSON Schema file"
    )
    parser.add_argument("--json", action="store_true", help="native Agent API run JSON")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the request body without credentials, authentication or network calls",
    )
    add_common_args(parser)
    args = parser.parse_args()
    if not args.query.strip():
        parser.error("query must not be blank")
    if args.max_cost is not None and args.effort not in ("auto", "ultra"):
        parser.error("--max-cost is supported only with --effort auto or ultra")
    if args.system_prompt is not None and not args.system_prompt.strip():
        parser.error("--system-prompt must not be blank")
    body = {"query": args.query, "effort": args.effort}
    if args.max_cost is not None:
        body["budget"] = {"maxCostDollars": args.max_cost}
    if args.system_prompt is not None:
        body["systemPrompt"] = args.system_prompt
    if args.output_schema is not None:
        try:
            schema = json.loads(args.output_schema.read_text())
        except (OSError, UnicodeError, ValueError) as exc:
            parser.error(f"cannot read --output-schema as JSON ({type(exc).__name__})")
        if not isinstance(schema, dict):
            parser.error("--output-schema must contain a JSON object")
        body["outputSchema"] = schema
    if args.dry_run:
        _dump_json({"method": "POST", "path": "/agent/runs", "body": body})
        return
    # Use the SDK transport without its narrower Agent response enums. The API
    # explicitly permits new stopReason values, which must remain readable.
    run = api_call(
        _client(args.timeout).request, "/agent/runs", method="POST", data=body
    )
    data = _emit(run, args.json)
    if data["status"] == "failed":
        raise SystemExit(1)
    if not args.json:
        print(f"\nRetrieve: exa-agent-status {data['id']}")


def _lifecycle(operation: str) -> None:
    parser = argparse.ArgumentParser(description=f"Exa Agent — {operation} a run")
    parser.add_argument("run_id", type=_run_id)
    parser.add_argument("--json", action="store_true", help="native Agent API run JSON")
    add_common_args(parser)
    args = parser.parse_args()
    endpoint = f"/agent/runs/{args.run_id}"
    method = "GET"
    if operation == "cancel":
        endpoint += "/cancel"
        method = "POST"
    run = api_call(_client(args.timeout).request, endpoint, method=method)
    if _emit(run, args.json)["status"] == "failed":
        raise SystemExit(1)


def status() -> None:
    _lifecycle("get")


def cancel() -> None:
    _lifecycle("cancel")
