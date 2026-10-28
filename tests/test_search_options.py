import contextlib
import io
import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

import requests

from exa_cli._common import api_call
from exa_cli.main import crawl, search


class SearchOptionsTests(unittest.TestCase):
    def invoke(self, entrypoint, argv, client):
        output = io.StringIO()
        with (
            mock.patch("exa_cli.main._client", return_value=client),
            mock.patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(output),
        ):
            entrypoint()
        return output.getvalue()

    def test_invalid_arguments_fail_before_client_creation(self):
        cases = [
            (search, ["exa-search", " "]),
            (search, ["exa-search", "topic", "-n", "0"]),
            (search, ["exa-search", "topic", "-n", "101"]),
            (search, ["exa-search", "topic", "--timeout", "nan"]),
            (search, ["exa-search", "topic", "--timeout", "0"]),
            (search, ["exa-search", "topic", "--max-chars", "100"]),
            (search, ["exa-search", "topic", "--start-date", "2026-02-30"]),
            (search, ["exa-search", "topic", "--start-date", "20260101"]),
            (
                search,
                [
                    "exa-search",
                    "topic",
                    "--start-date",
                    "2026-10-01",
                    "--end-date",
                    "2026-01-01",
                ],
            ),
            (search, ["exa-search", "--similar", "file:///tmp/article"]),
            (search, ["exa-search", "topic", "--include-domain", ", ,"]),
            (
                search,
                [
                    "exa-search",
                    "topic",
                    "--category",
                    "people",
                    "--exclude-domain",
                    "example.com",
                ],
            ),
            (
                search,
                [
                    "exa-search",
                    "topic",
                    "--category",
                    "company",
                    "--end-date",
                    "2026-01-01",
                ],
            ),
            (crawl, ["exa-crawl", "https://example.com", "-c", "-1"]),
            (crawl, ["exa-crawl", "https://user:password@example.com"]),
            (crawl, ["exa-crawl"] + ["https://example.com"] * 101),
        ]
        for entrypoint, argv in cases:
            with self.subTest(argv=argv), mock.patch("exa_cli.main._client") as client:
                with (
                    mock.patch.object(sys, "argv", argv),
                    contextlib.redirect_stderr(io.StringIO()),
                ):
                    with self.assertRaises(SystemExit) as error:
                        entrypoint()
                self.assertEqual(error.exception.code, 2)
                client.assert_not_called()

    def test_default_requests_only_highlights_without_deprecated_options(self):
        client = mock.Mock()
        client.search.return_value = SimpleNamespace(results=[])
        self.invoke(search, ["exa-search", "topic", "--json"], client)
        self.assertEqual(
            client.search.call_args.kwargs["contents"], {"highlights": True}
        )
        self.assertEqual(client.search.call_args.kwargs["type"], "auto")

    def test_paper_aliases_request_publication_category(self):
        for category in ["paper", "research paper", "publication"]:
            client = mock.Mock()
            client.search.return_value = SimpleNamespace(results=[])
            self.invoke(
                search,
                ["exa-search", "topic", "--category", category, "--json"],
                client,
            )
            self.assertEqual(client.search.call_args.kwargs["category"], "publication")

    def test_search_text_cap_avoids_second_content_mode(self):
        client = mock.Mock()
        client.search.return_value = SimpleNamespace(results=[])
        self.invoke(
            search,
            ["exa-search", "topic", "--text", "--max-chars", "7000", "--json"],
            client,
        )
        self.assertEqual(
            client.search.call_args.kwargs["contents"],
            {"text": {"max_characters": 7000}},
        )

    def test_date_window_includes_both_complete_utc_days(self):
        client = mock.Mock()
        client.search.return_value = SimpleNamespace(results=[])
        self.invoke(
            search,
            [
                "exa-search",
                "topic",
                "--start-date",
                "2026-01-01",
                "--end-date",
                "2026-10-28",
                "--json",
            ],
            client,
        )
        kwargs = client.search.call_args.kwargs
        self.assertEqual(kwargs["start_published_date"], "2026-01-01T00:00:00.000Z")
        self.assertEqual(kwargs["end_published_date"], "2026-10-28T23:59:59.999Z")

    def test_lite_search_type_is_forwarded(self):
        client = mock.Mock()
        client.search.return_value = SimpleNamespace(results=[])
        self.invoke(search, ["exa-search", "topic", "-t", "lite", "--json"], client)
        self.assertEqual(client.search.call_args.kwargs["type"], "lite")

    def test_crawl_honors_text_limit_in_terminal(self):
        text = "A" * 3000 + "\nMARKER_AFTER_2000"
        client = mock.Mock()
        client.get_contents.return_value = SimpleNamespace(
            results=[SimpleNamespace(text=text)]
        )
        output = self.invoke(
            crawl, ["exa-crawl", "https://example.com", "-c", "5000"], client
        )
        self.assertIn("MARKER_AFTER_2000", output)

    def test_crawl_batches_urls_in_one_api_call(self):
        client = mock.Mock()
        client.get_contents.return_value = SimpleNamespace(results=[])
        output = self.invoke(
            crawl,
            ["exa-crawl", "https://example.com/a", "https://example.com/b", "--json"],
            client,
        )
        self.assertEqual(json.loads(output)["results"], [])
        client.get_contents.assert_called_once_with(
            ["https://example.com/a", "https://example.com/b"],
            text={"max_characters": 5000},
        )

    def test_crawl_reports_all_failed_urls_with_json_intact(self):
        client = mock.Mock()
        client.get_contents.return_value = SimpleNamespace(
            results=[],
            statuses=[SimpleNamespace(id="https://example.com", status="error")],
        )
        output, errors = io.StringIO(), io.StringIO()
        with (
            mock.patch("exa_cli.main._client", return_value=client),
            mock.patch.object(
                sys, "argv", ["exa-crawl", "https://example.com", "--json"]
            ),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            with self.assertRaises(SystemExit) as error:
                crawl()
        self.assertEqual(error.exception.code, 1)
        self.assertEqual(
            json.loads(output.getvalue())["statuses"][0]["status"], "error"
        )
        self.assertIn("could not retrieve 1", errors.getvalue())

    def test_partial_crawl_keeps_successful_results(self):
        client = mock.Mock()
        client.get_contents.return_value = SimpleNamespace(
            results=[SimpleNamespace(url="https://example.com/a")],
            statuses=[SimpleNamespace(id="https://example.com/b", status="error")],
        )
        with contextlib.redirect_stderr(io.StringIO()):
            output = self.invoke(
                crawl,
                [
                    "exa-crawl",
                    "https://example.com/a",
                    "https://example.com/b",
                    "--json",
                ],
                client,
            )
        self.assertEqual(len(json.loads(output)["results"]), 1)

    def test_timeout_configures_sdk_client(self):
        client = mock.Mock()
        client.search.return_value = SimpleNamespace(results=[])
        with (
            mock.patch.dict(os.environ, {"EXA_API_KEY": "test-key"}),
            mock.patch("exa_cli.main.Exa", return_value=client) as constructor,
            mock.patch.object(
                sys, "argv", ["exa-search", "topic", "--timeout", "12", "--json"]
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            search()
        constructor.assert_called_once_with(api_key="test-key", timeout=12)

    def test_api_error_redacts_key_and_network_error_omits_sensitive_details(self):
        for exc in [
            ValueError("HTTP 401 secret-token"),
            requests.Timeout("secret-token"),
        ]:
            with mock.patch.dict(os.environ, {"EXA_API_KEY": "secret-token"}):
                with self.assertRaises(SystemExit) as error:
                    api_call(mock.Mock(side_effect=exc))
            self.assertNotIn("secret-token", str(error.exception))
            self.assertIn("Exa", str(error.exception))

    def test_actual_sdk_request_has_current_content_contract_and_timeout(self):
        response = mock.Mock(status_code=200)
        response.json.return_value = {"results": [], "requestId": "test-request"}
        with (
            mock.patch.dict(os.environ, {"EXA_API_KEY": "test-key"}),
            mock.patch("requests.post", return_value=response) as post,
            mock.patch.object(
                sys,
                "argv",
                [
                    "exa-search",
                    "topic",
                    "--category",
                    "publication",
                    "--timeout",
                    "12",
                    "--json",
                ],
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            search()
        body = json.loads(post.call_args.kwargs["data"])
        self.assertEqual(body["category"], "publication")
        self.assertEqual(body["contents"], {"highlights": True})
        self.assertEqual(post.call_args.kwargs["timeout"], 12)


if __name__ == "__main__":
    unittest.main()
