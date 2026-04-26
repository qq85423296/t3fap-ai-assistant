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

    def test_update_plugin_config_command_wraps_values_object(self) -> None:
        cli = load_cli_module()

        request = cli.build_command_request(
            "update-plugin-config",
            {"plugin_id": "task.transfer", "values_json": '{"default_exclude_keywords":"测试"}'},
            json_override=None,
        )

        self.assertEqual(request["method"], "PUT")
        self.assertEqual(request["path"], "/api/plugins/task.transfer/config")
        self.assertEqual(request["body"], {"values": {"default_exclude_keywords": "测试"}})

    def test_create_drive_account_command_wraps_payload(self) -> None:
        cli = load_cli_module()

        request = cli.build_command_request(
            "create-drive-account",
            {"plugin_id": "drive.quark", "payload_json": '{"cookie":"abc"}'},
            json_override=None,
        )

        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/api/drive/providers/drive.quark/accounts")
        self.assertEqual(request["body"], {"payload": {"cookie": "abc"}})

    def test_run_resource_action_command_builds_payload_wrapper(self) -> None:
        cli = load_cli_module()

        request = cli.build_command_request(
            "run-resource-action",
            {
                "resource_id": "search.pansou::demo",
                "action_key": "task.transfer.create",
                "payload_json": '{"target_account_id":"1"}',
            },
            json_override=None,
        )

        self.assertEqual(request["method"], "POST")
        self.assertEqual(
            request["path"],
            "/api/resources/search.pansou::demo/actions/task.transfer.create",
        )
        self.assertEqual(request["body"], {"payload": {"target_account_id": "1"}})

    def test_monitor_executions_command_keeps_filters(self) -> None:
        cli = load_cli_module()

        request = cli.build_command_request(
            "monitor-executions",
            {"limit": "20", "status": "failed", "trigger_source": "manual"},
            json_override=None,
        )

        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["path"], "/api/monitor/executions")
        self.assertEqual(request["query"], {"limit": "20", "status": "failed", "trigger_source": "manual"})

    def test_monitor_system_realtime_command_maps_to_endpoint(self) -> None:
        cli = load_cli_module()

        request = cli.build_command_request("monitor-system-realtime", {}, json_override=None)

        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["path"], "/api/monitor/system/realtime")


if __name__ == "__main__":
    unittest.main()
