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

    def test_research_json_entrypoint_outputs_task_metadata(self):
        client = mock.Mock()
        client.research.create.return_value = Obj(
            research_id="r_1",
            model="exa-research",
            instructions="topic",
            status="pending",
        )

        with mock.patch.dict(os.environ, {"EXA_API_KEY": "test"}, clear=True):
            with mock.patch("exa_cli.main.Exa", return_value=client):
                with mock.patch.object(
                    sys, "argv", ["exa-research", "topic", "--json"]
                ):
                    stdout = io.StringIO()
                    with contextlib.redirect_stdout(stdout):
                        research()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["research_id"], "r_1")
        client.research.create.assert_called_once_with(
            instructions="topic",
            model="exa-research",
        )

    def test_research_status_json_entrypoint_outputs_completed_result(self):
        client = mock.Mock()
        client.research.get.return_value = Obj(
            research_id="r_1",
            status="completed",
            output=Obj(content="answer"),
        )

        with mock.patch.dict(os.environ, {"EXA_API_KEY": "test"}, clear=True):
            with mock.patch("exa_cli.main.Exa", return_value=client):
                with mock.patch.object(
                    sys, "argv", ["exa-research-status", "r_1", "--json"]
                ):
                    stdout = io.StringIO()
                    with contextlib.redirect_stdout(stdout):
                        research_status()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["output"]["content"], "answer")
        client.research.get.assert_called_once_with("r_1")

    def test_research_status_text_entrypoint_prints_completed_content(self):
        client = mock.Mock()
        client.research.get.return_value = Obj(
            research_id="r_1",
            status="completed",
            output=Obj(content="answer"),
        )

        with mock.patch.dict(os.environ, {"EXA_API_KEY": "test"}, clear=True):
            with mock.patch("exa_cli.main.Exa", return_value=client):
                with mock.patch.object(sys, "argv", ["exa-research-status", "r_1"]):
                    stdout = io.StringIO()
                    with contextlib.redirect_stdout(stdout):
                        research_status()

        self.assertIn("Status: completed", stdout.getvalue())
        self.assertIn("answer", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
