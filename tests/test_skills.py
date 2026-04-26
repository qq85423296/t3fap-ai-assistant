from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"


class BundledSkillsTests(unittest.TestCase):
    def test_expected_t3mt_skills_are_bundled(self) -> None:
        expected = {
            "t3mt-api",
            "t3mt-cli",
            "t3mt-command-dispatch",
            "t3mt-drive-ops",
            "t3mt-generic-plugin-adapter",
            "t3mt-monitor-ops",
            "t3mt-plugin-ops",
            "t3mt-remediation-ops",
            "t3mt-resource-ops",
            "t3mt-settings-ops",
            "t3mt-sidecar-automation",
            "t3mt-task-ops",
            "t3mt-workflow-ops",
        }

        actual = {path.name for path in SKILLS_ROOT.glob("t3mt-*") if path.is_dir()}

        self.assertEqual(actual, expected)

    def test_skill_frontmatter_uses_only_supported_keys(self) -> None:
        for skill_file in SKILLS_ROOT.glob("t3mt-*/SKILL.md"):
            with self.subTest(skill=skill_file.parent.name):
                text = skill_file.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                _, frontmatter, _ = text.split("---", 2)
                keys = {
                    line.split(":", 1)[0].strip()
                    for line in frontmatter.splitlines()
                    if line.strip() and ":" in line
                }
                self.assertEqual(keys, {"name", "description"})

    def test_sidecar_skills_default_to_docker_service_host(self) -> None:
        combined = "\n".join(
            skill_file.read_text(encoding="utf-8")
            for skill_file in SKILLS_ROOT.glob("t3mt-*/SKILL.md")
        )

        self.assertIn("http://t3fap:8521", combined)
        self.assertNotIn("http://127.0.0.1:8521", combined)
        self.assertNotIn("http://localhost:8521", combined)


if __name__ == "__main__":
    unittest.main()
