import contextlib
import io
import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

from exa_cli.main import crawl, search


class FocusedRetrievalTests(unittest.TestCase):
    def invoke(self, entrypoint, argv, client):
        output, errors = io.StringIO(), io.StringIO()
        with (
            mock.patch("exa_cli.main._client", return_value=client),
            mock.patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            entrypoint()
        return output.getvalue(), errors.getvalue()

    def test_focused_crawl_returns_excerpts_without_full_text_in_terminal(self):
        client = mock.Mock()
        client.get_contents.return_value = SimpleNamespace(
            results=[
                SimpleNamespace(
                    url="https://example.com/long-faq",
                    highlights=["The answer near the end of the FAQ."],
                )
            ]
        )
        output, errors = self.invoke(
            crawl,
            ["exa-crawl", "https://example.com/long-faq", "--query", "specific rule"],
            client,
        )
        self.assertIn("The answer near the end", output)
        self.assertEqual(errors, "")
        client.get_contents.assert_called_once_with(
            ["https://example.com/long-faq"],
            text=False,
            highlights={"query": "specific rule", "max_characters": 5000},
        )

    def test_focused_crawl_wire_contract_avoids_sdk_implicit_full_text(self):
        response = mock.Mock(status_code=200)
        response.json.return_value = {
            "results": [
                {"url": "https://example.com", "highlights": ["Relevant passage"]}
            ],
            "statuses": [{"id": "https://example.com", "status": "success"}],
        }
        output = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"EXA_API_KEY": "test-key"}),
            mock.patch("requests.post", return_value=response) as post,
            mock.patch.object(
                sys,
                "argv",
                [
                    "exa-crawl",
                    "https://example.com",
                    "--query",
                    "specific rule",
                    "-c",
                    "1500",
                    "--max-age-hours",
                    "0",
                    "--compact",
                ],
            ),
            contextlib.redirect_stdout(output),
        ):
            crawl()
        body = json.loads(post.call_args.kwargs["data"])
        self.assertIs(body["text"], False)
        self.assertEqual(
            body["highlights"], {"query": "specific rule", "maxCharacters": 1500}
        )
        self.assertEqual(body["maxAgeHours"], 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["results"][0]["highlights"], ["Relevant passage"])
        self.assertNotIn("text", payload["results"][0])

    def test_search_wire_contract_preserves_goal_and_highlights(self):
        response = mock.Mock(status_code=200)
        response.json.return_value = {"results": []}
        with (
            mock.patch.dict(os.environ, {"EXA_API_KEY": "test-key"}),
            mock.patch("requests.post", return_value=response) as post,
            mock.patch.object(
                sys,
                "argv",
                [
                    "exa-search",
                    "local service pricing",
                    "--objective",
                    "Prefer provider pricing pages; exclude directories.",
                    "--max-age-hours",
                    "24",
                    "--json",
                ],
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            search()
        body = json.loads(post.call_args.kwargs["data"])
        self.assertEqual(body["type"], "auto")
        self.assertEqual(
            body["objective"], "Prefer provider pricing pages; exclude directories."
        )
        self.assertEqual(body["contents"], {"highlights": True, "maxAgeHours": 24})

    def test_cache_only_and_freshness_boundaries_are_not_treated_as_unset(self):
        for age in (-1, 0, 720):
            with self.subTest(age=age):
                client = mock.Mock()
                client.get_contents.return_value = SimpleNamespace(results=[])
                self.invoke(
                    crawl,
                    ["exa-crawl", "https://example.com", "--max-age-hours", str(age)],
                    client,
                )
                self.assertEqual(
                    client.get_contents.call_args.kwargs["max_age_hours"], age
                )

    def test_invalid_options_fail_before_authentication_or_network(self):
        cases = [
            (crawl, ["https://example.com", "--query", " "]),
            (search, ["topic", "--objective", " "]),
            (search, ["topic", "--objective", "x" * 4097]),
            (search, ["--similar", "https://example.com", "--objective", "goal"]),
            (search, ["topic", "-t", "lite", "--max-age-hours", "-1"]),
        ]
        for age in ("-2", "721", "nan", "1.5"):
            cases.extend(
                [
                    (crawl, ["https://example.com", "--max-age-hours", age]),
                    (search, ["topic", "--max-age-hours", age]),
                ]
            )
        for entrypoint, args in cases:
            with self.subTest(args=args), mock.patch("exa_cli.main._client") as client:
                with (
                    mock.patch.object(sys, "argv", ["exa", *args]),
                    contextlib.redirect_stderr(io.StringIO()),
                    self.assertRaises(SystemExit) as error,
                ):
                    entrypoint()
                self.assertEqual(error.exception.code, 2)
                client.assert_not_called()

    def test_text_at_cap_warns_without_corrupting_json(self):
        client = mock.Mock()
        client.get_contents.return_value = SimpleNamespace(
            results=[SimpleNamespace(url="https://example.com", text="Intro" * 20)]
        )
        output, errors = self.invoke(
            crawl, ["exa-crawl", "https://example.com", "-c", "100", "--json"], client
        )
        self.assertEqual(len(json.loads(output)["results"][0]["text"]), 100)
        self.assertIn("may be incomplete", errors)
        self.assertIn("exa-crawl --query", errors)

    def test_short_page_does_not_warn(self):
        client = mock.Mock()
        client.get_contents.return_value = SimpleNamespace(
            results=[SimpleNamespace(url="https://example.com", text="Complete page")]
        )
        _, errors = self.invoke(
            crawl, ["exa-crawl", "https://example.com", "-c", "100", "--json"], client
        )
        self.assertEqual(errors, "")

    def test_search_text_at_explicit_cap_warns(self):
        client = mock.Mock()
        client.search.return_value = SimpleNamespace(
            results=[SimpleNamespace(url="https://example.com", text="X" * 100)]
        )
        output, errors = self.invoke(
            search,
            ["exa-search", "topic", "--text", "--max-chars", "100", "--compact"],
            client,
        )
        self.assertEqual(len(json.loads(output)["results"][0]["text"]), 100)
        self.assertIn("may be incomplete", errors)


if __name__ == "__main__":
    unittest.main()
