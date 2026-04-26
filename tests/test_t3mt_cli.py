from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "skills" / "t3mt-cli" / "scripts" / "t3mt-cli.py"


def load_cli_module():
    spec = importlib.util.spec_from_file_location("t3mt_cli", CLI_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load t3mt-cli module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class T3mtCliTests(unittest.TestCase):
    def test_run_task_command_builds_waiting_request(self) -> None:
        cli = load_cli_module()

        request = cli.build_command_request(
            "run-task",
            {"task_id": "demo", "wait_for_completion": "true"},
            json_override=None,
        )

        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/api/tasks/demo/run")
        self.assertEqual(request["body"], {"wait_for_completion": True})

    def test_raw_api_command_keeps_query_pairs_and_json_body(self) -> None:
        cli = load_cli_module()

        request = cli.build_api_request(
            ["POST", "/api/resources/search/query", "trace=true"],
            json_override='{"plugin_id":"search.pansou","keyword":"test"}',
        )

        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/api/resources/search/query")
        self.assertEqual(request["query"], {"trace": "true"})
        self.assertEqual(request["body"], {"plugin_id": "search.pansou", "keyword": "test"})


if __name__ == "__main__":
    unittest.main()
