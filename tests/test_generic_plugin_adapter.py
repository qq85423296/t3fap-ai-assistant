from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = REPO_ROOT / "skills" / "t3mt-generic-plugin-adapter" / "scripts" / "t3mt-generic-plugin-adapter.py"


def load_adapter_module():
    spec = importlib.util.spec_from_file_location("t3mt_generic_plugin_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load generic plugin adapter module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenericPluginAdapterTests(unittest.TestCase):
    def test_infer_roles_from_capabilities_and_provider_types(self) -> None:
        adapter = load_adapter_module()

        roles = adapter.infer_roles(
            {
                "category": "assistant",
                "provider_types": ["automation"],
                "capabilities": ["resource.search", "task.template", "drive.account"],
            }
        )

        self.assertEqual(roles, ["assistant", "automation", "drive", "resource", "search", "task"])

    def test_build_suggested_commands_for_drive_plugin(self) -> None:
        adapter = load_adapter_module()

        commands = adapter.build_suggested_commands("drive.123pan", ["drive"])

        self.assertTrue(any("t3mt-drive-ops" in command and "plugin_id=drive.123pan" in command for command in commands))
        self.assertTrue(any("account-form" in command and "plugin_id=drive.123pan" in command for command in commands))


if __name__ == "__main__":
    unittest.main()
