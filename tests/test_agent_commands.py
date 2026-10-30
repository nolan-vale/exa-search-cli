import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from exa_cli.agent import cancel, create, status


class AgentCommandTests(unittest.TestCase):
    def invoke(self, entrypoint, argv, client=None):
        output = io.StringIO()
        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch("exa_cli.agent._client", return_value=client),
            contextlib.redirect_stdout(output),
        ):
            entrypoint()
        return output.getvalue()

    def test_dry_run_is_credential_free_and_matches_real_sdk_request(self):
        argv = [
            "exa-agent",
            "Find official local provider prices",
            "--effort",
            "auto",
            "--max-cost",
            "1",
            "--system-prompt",
            "Prefer primary sources",
        ]
        with mock.patch.dict(os.environ, {}, clear=True):
            preview = json.loads(self.invoke(create, [*argv, "--dry-run"]))
        self.assertEqual(preview["path"], "/agent/runs")
        self.assertEqual(preview["body"]["budget"], {"maxCostDollars": 1})
        self.assertNotIn("headers", preview)
        output = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"EXA_API_KEY": "test-key"}),
            mock.patch(
                "exa_py.Exa.request",
                return_value={"id": "agent_run_test", "status": "queued"},
            ) as request,
            mock.patch.object(sys, "argv", [*argv, "--json"]),
            contextlib.redirect_stdout(output),
        ):
            create()
        args, kwargs = request.call_args
        self.assertEqual(args, ("/agent/runs",))
        self.assertEqual(kwargs["method"], "POST")
        self.assertEqual(kwargs["data"], preview["body"])
        self.assertEqual(json.loads(output.getvalue())["id"], "agent_run_test")
        request.assert_called_once()

    def test_default_effort_is_auto_without_overriding_server_budget(self):
        preview = json.loads(self.invoke(create, ["exa-agent", "Task", "--dry-run"]))
        self.assertEqual(preview["body"], {"query": "Task", "effort": "auto"})

    def test_output_schema_survives_sdk_serialization(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "schema.json"
            schema = {"type": "object", "properties": {"name": {"type": "string"}}}
            path.write_text(json.dumps(schema))
            output = io.StringIO()
            with (
                mock.patch.dict(os.environ, {"EXA_API_KEY": "test-key"}),
                mock.patch(
                    "exa_py.Exa.request",
                    return_value={"id": "agent_run_test", "status": "queued"},
                ) as request,
                mock.patch.object(
                    sys,
                    "argv",
                    ["exa-agent", "Task", "--output-schema", str(path), "--json"],
                ),
                contextlib.redirect_stdout(output),
            ):
                create()
            self.assertEqual(request.call_args.kwargs["data"]["outputSchema"], schema)

    def test_status_preserves_answer_citations_partial_stop_reason_and_cost(self):
        response = {
            "id": "agent_run_test",
            "status": "completed",
            "stopReason": "budget_reached",
            "output": {
                "text": "Supported answer",
                "structured": {"price": 10},
                "grounding": [
                    {
                        "field": "price",
                        "citations": [{"url": "https://example.com/pricing"}],
                        "confidence": "high",
                    }
                ],
            },
            "costDollars": {"total": 1},
        }
        output = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"EXA_API_KEY": "test-key"}),
            mock.patch("exa_py.Exa.request", return_value=response) as request,
            mock.patch.object(
                sys, "argv", ["exa-agent-status", "agent_run_test", "--json"]
            ),
            contextlib.redirect_stdout(output),
        ):
            status()
        data = json.loads(output.getvalue())
        self.assertEqual(data["output"]["text"], "Supported answer")
        self.assertEqual(data["output"]["structured"], {"price": 10})
        self.assertEqual(
            data["output"]["grounding"][0]["citations"][0]["url"],
            "https://example.com/pricing",
        )
        self.assertEqual(data["costDollars"]["total"], 1)
        self.assertEqual(data["stopReason"], "budget_reached")
        self.assertEqual(request.call_args.args, ("/agent/runs/agent_run_test",))
        self.assertEqual(request.call_args.kwargs["method"], "GET")
        request.assert_called_once()

    def test_terminal_output_includes_sources_and_zero_cost(self):
        client = mock.Mock()
        client.request.return_value = {
            "id": "agent_run_test",
            "status": "completed",
            "stopReason": "schema_satisfied",
            "output": {
                "text": "Answer",
                "grounding": [{"citations": [{"url": "https://example.com"}]}],
            },
            "costDollars": {"total": 0},
        }
        output = self.invoke(status, ["exa-agent-status", "agent_run_test"], client)
        self.assertIn("Answer", output)
        self.assertIn("Source: https://example.com", output)
        self.assertIn("Cost: $0.0000", output)

    def test_new_stop_reasons_and_metadata_remain_readable(self):
        client = mock.Mock()
        client.request.return_value = {
            "id": "agent_run_test",
            "status": "completed",
            "stopReason": "iteration_limit_reached",
            "futureMetadata": {"value": 0},
        }
        output = self.invoke(
            status, ["exa-agent-status", "agent_run_test", "--json"], client
        )
        data = json.loads(output)
        self.assertEqual(data["stopReason"], "iteration_limit_reached")
        self.assertEqual(data["futureMetadata"], {"value": 0})

    def test_cancel_uses_only_the_requested_run_and_returns_cancelled_state(self):
        with (
            mock.patch.dict(os.environ, {"EXA_API_KEY": "test-key"}),
            mock.patch(
                "exa_py.Exa.request",
                return_value={"id": "agent_run_test", "status": "cancelled"},
            ) as request,
            mock.patch.object(
                sys, "argv", ["exa-agent-cancel", "agent_run_test", "--json"]
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            cancel()
        self.assertEqual(request.call_args.args, ("/agent/runs/agent_run_test/cancel",))
        self.assertEqual(request.call_args.kwargs["method"], "POST")
        request.assert_called_once()

    def test_failed_run_returns_nonzero_with_valid_json(self):
        client = mock.Mock()
        client.request.return_value = {
            "id": "agent_run_test",
            "status": "failed",
            "error": {"message": "Failed"},
        }
        output = io.StringIO()
        with (
            mock.patch("exa_cli.agent._client", return_value=client),
            mock.patch.object(
                sys, "argv", ["exa-agent-status", "agent_run_test", "--json"]
            ),
            contextlib.redirect_stdout(output),
            self.assertRaises(SystemExit) as error,
        ):
            status()
        self.assertEqual(error.exception.code, 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "failed")

    def test_invalid_input_fails_before_authentication_or_run_creation(self):
        cases = [
            (create, ["exa-agent", " "]),
            (create, ["exa-agent", "Task", "--max-cost", "0.5"]),
            (create, ["exa-agent", "Task", "--max-cost", "nan"]),
            (create, ["exa-agent", "Task", "--max-cost", "101"]),
            (create, ["exa-agent", "Task", "--effort", "low", "--max-cost", "1"]),
            (create, ["exa-agent", "Task", "--system-prompt", " "]),
            (create, ["exa-agent", "Task", "--output-schema", "/missing/schema.json"]),
        ]
        for bad in ("../run", "a/b", "..", "id?query", " ", "x" * 201):
            cases.extend(
                [
                    (status, ["exa-agent-status", bad]),
                    (cancel, ["exa-agent-cancel", bad]),
                ]
            )
        for entrypoint, argv in cases:
            with self.subTest(argv=argv), mock.patch("exa_cli.agent._client") as client:
                with (
                    mock.patch.object(sys, "argv", argv),
                    contextlib.redirect_stderr(io.StringIO()),
                    self.assertRaises(SystemExit) as error,
                ):
                    entrypoint()
                self.assertEqual(error.exception.code, 2)
                client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
