from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "runtime" / "t3mt_automation.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("t3mt_automation", POLICY_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load automation policy module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AutomationPolicyTests(unittest.TestCase):
    def test_unknown_mode_falls_back_to_whitelist(self) -> None:
        policy = load_policy_module()
        self.assertEqual(policy.normalize_automation_mode("wild-west"), "whitelist")

    def test_full_access_allows_normal_writes_without_confirmation(self) -> None:
        policy = load_policy_module()
        self.assertFalse(
            policy.action_requires_confirmation(
                "full-access",
                "task.run",
                confirm_redline_actions=True,
            )
        )

    def test_full_access_keeps_redline_confirmation_when_enabled(self) -> None:
        policy = load_policy_module()
        self.assertTrue(
            policy.action_requires_confirmation(
                "full-access",
                "api-key.reset",
                confirm_redline_actions=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
