from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = REPO_ROOT / "runtime" / "t3fap_assistant_runtime.py"


def load_runtime_module():
    spec = importlib.util.spec_from_file_location("t3fap_assistant_runtime", RUNTIME_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load assistant runtime module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AssistantRuntimeTests(unittest.TestCase):
    def test_build_runtime_config_uses_docker_t3fap_default(self) -> None:
        runtime = load_runtime_module()
        env = {
            "OPENAI_API_KEY": "sk-test",
            "T3FAP_ASSISTANT_PICO_TOKEN": "pico-token",
        }

        config = runtime.build_runtime_config(env)

        self.assertEqual(config.t3mt_host, "http://t3fap:8521")
        self.assertEqual(config.t3mt_api_key, "")
        self.assertEqual(config.automation_mode, "full-access")
        self.assertEqual(config.model_name, "gpt-5.4")
        self.assertEqual(config.model, "openai/gpt-5.4")
        self.assertEqual(config.model_api_key, "sk-test")
        self.assertEqual(config.pico_token, "pico-token")

    def test_write_picoclaw_config_contains_workspace_model_and_pico_channel(self) -> None:
        runtime = load_runtime_module()
        with tempfile.TemporaryDirectory() as raw_dir:
            home = Path(raw_dir)
            config = runtime.build_runtime_config(
                {
                    "PICOCLAW_HOME": str(home),
                    "T3MT_HOST": "http://app:8521",
                    "T3MT_API_KEY": "t3mt-secret",
                    "T3FAP_ASSISTANT_MODEL_NAME": "test-model",
                    "T3FAP_ASSISTANT_MODEL": "openai/test-model",
                    "T3FAP_ASSISTANT_API_KEY": "model-secret",
                    "T3FAP_ASSISTANT_API_BASE": "https://models.example/v1",
                    "T3FAP_ASSISTANT_PICO_TOKEN": "pico-secret",
                }
            )

            runtime.prepare_runtime(config, bundled_skills_dir=REPO_ROOT / "skills")

            payload = json.loads(config.config_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["agents"]["defaults"]["workspace"], str(config.workspace_dir))
            self.assertTrue(payload["tools"]["skills"]["enabled"])
            self.assertTrue(payload["tools"]["exec"]["enabled"])
            self.assertEqual(payload["channels"]["pico"]["token"], "pico-secret")
            self.assertEqual(payload["model_list"][0]["model_name"], "test-model")
            self.assertEqual(payload["model_list"][0]["api_base"], "https://models.example/v1")

    def test_sync_skills_copies_only_t3mt_skills_into_workspace(self) -> None:
        runtime = load_runtime_module()
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            source = root / "source"
            workspace = root / "workspace"
            (source / "t3mt-api").mkdir(parents=True)
            (source / "t3mt-api" / "SKILL.md").write_text("---\nname: t3mt-api\ndescription: test\n---\n", encoding="utf-8")
            (source / "other-skill").mkdir()
            (source / "other-skill" / "SKILL.md").write_text("---\nname: other\ndescription: test\n---\n", encoding="utf-8")
            (workspace / "skills" / "t3mt-api").mkdir(parents=True)
            (workspace / "skills" / "t3mt-api" / "old.txt").write_text("old", encoding="utf-8")

            runtime.sync_t3mt_skills(source, workspace / "skills")

            self.assertTrue((workspace / "skills" / "t3mt-api" / "SKILL.md").exists())
            self.assertFalse((workspace / "skills" / "t3mt-api" / "old.txt").exists())
            self.assertFalse((workspace / "skills" / "other-skill").exists())

    def test_prepare_environment_passes_t3mt_values_to_child_process(self) -> None:
        runtime = load_runtime_module()
        config = runtime.build_runtime_config(
            {
                "T3MT_HOST": "http://app:8521",
                "T3MT_API_KEY": "t3mt-secret",
                "PICOCLAW_CONFIG": "/tmp/picoclaw-config.json",
                "T3MT_AUTOMATION_MODE": "full-access",
                "T3MT_CONFIRM_REDLINE_ACTIONS": "false",
            }
        )

        child_env = runtime.build_child_environment(config, base_env={})

        self.assertEqual(child_env["T3MT_HOST"], "http://app:8521")
        self.assertEqual(child_env["T3MT_API_KEY"], "t3mt-secret")
        self.assertEqual(child_env["T3MT_AUTOMATION_MODE"], "full-access")
        self.assertEqual(child_env["T3MT_CONFIRM_REDLINE_ACTIONS"], "false")
        self.assertEqual(child_env["PICOCLAW_CONFIG"], "/tmp/picoclaw-config.json")


if __name__ == "__main__":
    unittest.main()
