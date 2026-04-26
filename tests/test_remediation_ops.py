from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "t3mt-remediation-ops" / "scripts" / "t3mt-remediation-ops.py"


def load_module():
    spec = importlib.util.spec_from_file_location("t3mt_remediation_ops", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load remediation helper module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RemediationOpsTests(unittest.TestCase):
    def test_build_analysis_marks_unhealthy_plugins_and_failed_executions(self) -> None:
        module = load_module()

        def fake_run_cli(*args: str):
            if args[0] == "monitor-plugin-health":
                return {
                    "items": [
                        {"plugin_id": "task.transfer", "status": "error", "message": "config missing"},
                        {"plugin_id": "search.pansou", "status": "healthy"},
                    ]
                }
            if args[0] == "monitor-executions":
                return {
                    "items": [
                        {"execution_id": "exec-1", "task_id": "task-1", "plugin_id": "task.transfer", "status": "failed"},
                        {"execution_id": "exec-2", "task_id": "task-2", "plugin_id": "task.strm", "status": "success"},
                    ]
                }
            raise AssertionError(args)

        module.run_cli = fake_run_cli
        result = module.build_analysis(limit=20)

        self.assertEqual(result["summary"]["recovery_candidates"], 2)
        self.assertTrue(any(item["kind"] == "plugin" and item["plugin_id"] == "task.transfer" for item in result["issues"]))
        self.assertTrue(any(item["kind"] == "execution" and item["execution_id"] == "exec-1" for item in result["issues"]))


if __name__ == "__main__":
    unittest.main()
