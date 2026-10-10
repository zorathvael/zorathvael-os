from types import SimpleNamespace
from unittest.mock import patch

from scripts import gemini_agent_orchestrator as orchestrator


def test_quota_or_agent_failure_still_runs_every_stage(monkeypatch, capsys):
    stages = [SimpleNamespace(name=f"stage_{i}", command=("python", str(i))) for i in range(4)]
    monkeypatch.setattr(orchestrator, "build_stages", lambda: tuple(stages))

    class UnavailableAgent:
        def __init__(self, registry, **kwargs):
            pass
        def run(self, task):
            return {"status": "fallback", "fallback_reason": "quota_exceeded", "audit": []}

    monkeypatch.setattr(orchestrator, "GeminiAgent", UnavailableAgent)
    completed = SimpleNamespace(returncode=0, stdout="ok\n", stderr="")
    with patch("scripts.gemini_agent_orchestrator.subprocess.run", return_value=completed) as run:
        exit_code = orchestrator.run_pipeline()

    assert exit_code == 0
    assert run.call_count == len(stages)
    output = capsys.readouterr().out
    assert '"mode": "gemini_supervised_with_deterministic_completion"' in output
    assert '"completed": 4' in output


def test_stage_runner_reports_nonzero_exit(monkeypatch):
    stage = SimpleNamespace(name="failed", command=("python", "failed.py"))
    completed = SimpleNamespace(returncode=2, stdout="partial", stderr="traceback")
    with patch("scripts.gemini_agent_orchestrator.subprocess.run", return_value=completed):
        result = orchestrator.execute_stage(stage)
    assert result["stage"] == "failed"
    assert result["returncode"] == 2
    assert result["stderr"] == "traceback"
