import contextlib
import io
import json
import sys
import unittest
from unittest import mock

from exa_cli._output import compact_payload
from exa_cli.main import crawl, search


class CompactOutputTests(unittest.TestCase):
    def test_compact_keeps_evidence_cost_status_and_nonempty_extended_data(self):
        payload = {
            "results": [
                {
                    "title": "Pricing",
                    "url": "https://example.com",
                    "id": "https://example.com",
                    "text": None,
                    "author": "",
                    "image": "https://example.com/image.png",
                    "highlights": ["$100 per visit"],
                    "entities": [{"properties": {"name": "Example", "empty": None}}],
                    "score": 0,
                    "new_field": False,
                }
            ],
            "cost_dollars": {"total": 0, "contents": None},
            "statuses": [{"status": "success", "source": "cached", "error": None}],
        }
        compact = compact_payload(payload)
        result = compact["results"][0]
        self.assertEqual(result["highlights"], ["$100 per visit"])
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["score"], 0)
        self.assertIs(result["new_field"], False)
        self.assertEqual(result["entities"][0]["properties"], {"name": "Example"})
        for key in ("id", "text", "author", "image"):
            self.assertNotIn(key, result)
        self.assertEqual(compact["cost_dollars"], {"total": 0})
        self.assertEqual(
            compact["statuses"], [{"status": "success", "source": "cached"}]
        )
        self.assertIn("text", payload["results"][0])

    def test_compact_preserves_distinct_document_id_and_empty_results(self):
        compact = compact_payload(
            {"results": [{"id": "document-123", "url": "https://example.com"}]}
        )
        self.assertEqual(compact["results"][0]["id"], "document-123")
        self.assertEqual(compact_payload({"results": []}), {"results": []})

    def test_compact_removes_result_alias_without_dropping_other_metadata(self):
        rows = [{"url": "https://example.com"}]
        compact = compact_payload(
            {"results": rows, "items": rows, "data": {"coverage": "partial"}}
        )
        self.assertNotIn("items", compact)
        self.assertEqual(compact["data"], {"coverage": "partial"})

    def test_json_remains_full_and_compact_is_opt_in_for_both_commands(self):
        for entrypoint, positional, method in (
            (search, ["topic"], "search"),
            (crawl, ["https://example.com"], "get_contents"),
        ):
            for flag in ("--json", "--compact"):
                with self.subTest(entrypoint=entrypoint.__name__, flag=flag):
                    client = mock.Mock()
                    getattr(client, method).return_value = {
                        "results": [{"url": "https://example.com", "author": None}],
                        "cost_dollars": {"total": 0.001, "contents": None},
                    }
                    output = io.StringIO()
                    with (
                        mock.patch("exa_cli.main._client", return_value=client),
                        mock.patch.object(sys, "argv", ["exa", *positional, flag]),
                        contextlib.redirect_stdout(output),
                    ):
                        entrypoint()
                    payload = json.loads(output.getvalue())
                    self.assertEqual(payload["cost_dollars"]["total"], 0.001)
                    if flag == "--json":
                        self.assertIn("author", payload["results"][0])
                        self.assertIn("contents", payload["cost_dollars"])
                    else:
                        self.assertNotIn("author", payload["results"][0])
                        self.assertEqual(len(output.getvalue().splitlines()), 1)

    def test_compact_failure_keeps_diagnostics_and_nonzero_exit(self):
        client = mock.Mock()
        client.get_contents.return_value = {
            "results": [],
            "statuses": [{"id": "https://example.com", "status": "error"}],
        }
        output, errors = io.StringIO(), io.StringIO()
        with (
            mock.patch("exa_cli.main._client", return_value=client),
            mock.patch.object(
                sys, "argv", ["exa-crawl", "https://example.com", "--compact"]
            ),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
            self.assertRaises(SystemExit) as error,
        ):
            crawl()
        self.assertEqual(error.exception.code, 1)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["results"], [])
        self.assertEqual(payload["statuses"][0]["status"], "error")
        self.assertIn("could not retrieve 1", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
