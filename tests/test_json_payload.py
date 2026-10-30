import contextlib
import io
import json
import os
import sys
import unittest
from unittest import mock

from exa_cli.main import (
    _client,
    _results_json_payload,
    crawl,
    research,
    research_status,
    search,
)


class Obj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class JsonPayloadTests(unittest.TestCase):
    def test_results_payload_wraps_top_level_result_array(self):
        payload = _results_json_payload([Obj(title="A", url="https://example.com")])

        self.assertEqual(
            payload,
            {"results": [{"title": "A", "url": "https://example.com"}]},
        )

    def test_results_payload_preserves_documented_results_object(self):
        payload = _results_json_payload(
            Obj(
                results=[Obj(title="A", url="https://example.com")],
                search_time=123,
            )
        )

        self.assertEqual(
            payload,
            {
                "results": [{"title": "A", "url": "https://example.com"}],
                "search_time": 123,
            },
        )

    def test_results_payload_maps_data_array_to_results(self):
        payload = _results_json_payload(
            {
                "data": [{"title": "A", "url": "https://example.com"}],
                "request_id": "req_1",
            }
        )

        self.assertEqual(payload["results"], payload["data"])
        self.assertEqual(payload["request_id"], "req_1")

    def test_results_payload_maps_items_array_to_results(self):
        payload = _results_json_payload(
            {
                "items": [{"title": "A", "url": "https://example.com"}],
                "request_id": "req_1",
            }
        )

        self.assertEqual(payload["results"], payload["items"])

    def test_results_payload_replaces_non_list_results_and_preserves_raw_value(self):
        payload = _results_json_payload({"results": None, "statuses": []})

        self.assertEqual(payload["results"], [])
        self.assertIsNone(payload["raw_results"])
        self.assertEqual(payload["statuses"], [])

    def test_results_payload_preserves_unexpected_scalar_value(self):
        payload = _results_json_payload("unexpected")

        self.assertEqual(payload, {"results": [], "value": "unexpected"})

    def test_results_payload_is_json_serializable(self):
        payload = _results_json_payload([Obj(title="A", url="https://example.com")])
        encoded = json.dumps(payload)

        self.assertEqual(
            json.loads(encoded)["results"][0]["url"], "https://example.com"
        )

    def test_client_requires_api_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                _client()

        self.assertIn("EXA_API_KEY not set", str(ctx.exception))

    def test_search_json_entrypoint_wraps_top_level_array_response(self):
        client = mock.Mock()
        client.search.return_value = [Obj(title="A", url="https://example.com")]

        with mock.patch.dict(os.environ, {"EXA_API_KEY": "test"}, clear=True):
            with mock.patch("exa_cli.main.Exa", return_value=client):
                with mock.patch.object(sys, "argv", ["exa-search", "topic", "--json"]):
                    stdout = io.StringIO()
                    with contextlib.redirect_stdout(stdout):
                        search()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["results"][0]["url"], "https://example.com")

    def test_search_similar_does_not_pass_search_type(self):
        client = mock.Mock()
        client.find_similar.return_value = Obj(results=[])

        with mock.patch.dict(os.environ, {"EXA_API_KEY": "test"}, clear=True):
            with mock.patch("exa_cli.main.Exa", return_value=client):
                with mock.patch.object(
                    sys,
                    "argv",
                    ["exa-search", "--similar", "https://example.com", "--json"],
                ):
                    stdout = io.StringIO()
                    with contextlib.redirect_stdout(stdout):
                        search()

        _, kwargs = client.find_similar.call_args
        self.assertNotIn("type", kwargs)

    def test_crawl_json_entrypoint_maps_items_response(self):
        client = mock.Mock()
        client.get_contents.return_value = {"items": [{"url": "https://example.com"}]}

        with mock.patch.dict(os.environ, {"EXA_API_KEY": "test"}, clear=True):
            with mock.patch("exa_cli.main.Exa", return_value=client):
                with mock.patch.object(
                    sys, "argv", ["exa-crawl", "https://example.com", "--json"]
                ):
                    stdout = io.StringIO()
                    with contextlib.redirect_stdout(stdout):
                        crawl()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["results"][0]["url"], "https://example.com")

    def test_retired_research_commands_never_authenticate_or_start_an_agent(self):
        cases = [
            (research, ["exa-research", "topic", "--json"]),
            (research, ["exa-research", "topic", "--model", "exa-research-pro"]),
            (research_status, ["exa-research-status", "old-research-id", "--json"]),
        ]
        for entrypoint, argv in cases:
            output, errors = io.StringIO(), io.StringIO()
            with (
                self.subTest(argv=argv),
                mock.patch("exa_cli.main._client") as client,
                mock.patch.object(sys, "argv", argv),
                contextlib.redirect_stdout(output),
                contextlib.redirect_stderr(errors),
                self.assertRaises(SystemExit) as error,
            ):
                entrypoint()
            self.assertIn("retired", str(error.exception))
            self.assertIn("exa-agent", str(error.exception))
            self.assertEqual(output.getvalue(), "")
            client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
