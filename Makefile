.PHONY: test validate-skills py-compile docker-build

test:
	python -m unittest discover -s tests

py-compile:
	python -m py_compile runtime/t3fap_assistant_runtime.py skills/t3mt-api/scripts/t3mt-api.py skills/t3mt-cli/scripts/t3mt-cli.py

validate-skills:
	python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-api
	python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-cli
	python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-command-dispatch
	python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-sidecar-automation

docker-build:
	docker build -t t3fap-ai-assistant:local .
