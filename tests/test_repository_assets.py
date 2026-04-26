from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class RepositoryAssetsTests(unittest.TestCase):
    def test_github_actions_workflow_builds_and_pushes_ghcr_image(self) -> None:
        workflow = REPO_ROOT / ".github" / "workflows" / "docker-image.yml"

        text = workflow.read_text(encoding="utf-8")

        self.assertIn("docker/build-push-action", text)
        self.assertIn("ghcr.io/${{ github.repository }}", text)
        self.assertIn("push: ${{ github.event_name != 'pull_request' }}", text)

    def test_docker_assets_keep_t3fap_sidecar_defaults(self) -> None:
        dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
        compose = (REPO_ROOT / "compose.example.yaml").read_text(encoding="utf-8")

        self.assertIn("T3MT_HOST=http://t3fap:8521", dockerfile)
        self.assertIn("T3MT_HOST: http://t3fap:8521", compose)
        self.assertIn("T3MT_AUTOMATION_MODE=whitelist", dockerfile)
        self.assertIn("T3MT_AUTOMATION_MODE: whitelist", compose)


if __name__ == "__main__":
    unittest.main()
