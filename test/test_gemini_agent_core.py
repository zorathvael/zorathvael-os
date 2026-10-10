import io
import json
import urllib.error
from unittest.mock import patch

from lib.core_modules.ai_router.agent_core import GeminiAgent, ToolRegistry


def response(payload):
    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return json.dumps(payload).encode()
    return Response()


def test_agent_returns_final_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    with patch("urllib.request.urlopen", return_value=response({
        "candidates": [{"content": {"parts": [{"text": "Verified answer"}]}}]
    })):
        result = GeminiAgent(ToolRegistry()).run("Review task")
    assert result["status"] == "success"
    assert result["response"] == "Verified answer"


def test_agent_executes_registered_tool_and_returns_observation(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    registry = ToolRegistry([{
        "name": "read_status", "description": "Read status.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "handler": lambda args: {"status": "verified"}, "requires_approval": False,
    }])
    with patch("urllib.request.urlopen", side_effect=[
        response({"candidates": [{"content": {"parts": [{
            "functionCall": {"name": "read_status", "args": {}, "id": "call-1"}
        }]}}]}),
        response({"candidates": [{"content": {"parts": [{"text": "Status verified"}]}}]}),
    ]) as request:
        result = GeminiAgent(registry).run("Read status")
    assert result["status"] == "success"
    assert result["audit"][0]["status"] == "executed"
    sent = json.loads(request.call_args_list[1].args[0].data.decode())
    assert sent["contents"][-1]["parts"][0]["functionResponse"]["response"]["result"]["status"] == "verified"


def test_agent_blocks_write_tool_without_approval(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    executed = []
    registry = ToolRegistry([{
        "name": "send_email", "description": "Send email.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "handler": lambda args: executed.append(args), "requires_approval": True,
    }])
    with patch("urllib.request.urlopen", side_effect=[
        response({"candidates": [{"content": {"parts": [{
            "functionCall": {"name": "send_email", "args": {}, "id": "call-2"}
        }]}}]}),
        response({"candidates": [{"content": {"parts": [{"text": "Approval is required"}]}}]}),
    ]):
        result = GeminiAgent(registry).run("Send email")
    assert result["audit"][0]["status"] == "blocked"
    assert executed == []


def test_agent_does_not_retry_quota_exhaustion(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    error = urllib.error.HTTPError("https://generativelanguage.googleapis.com", 429,
                                   "quota exceeded", {}, io.BytesIO(b"quota exceeded"))
    with patch("urllib.request.urlopen", side_effect=error) as request:
        result = GeminiAgent(ToolRegistry()).run("Do work")
    assert result["status"] == "fallback"
    assert result["fallback_reason"] == "quota_exceeded"
    assert request.call_count == 1


def test_agent_respects_step_limit(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    registry = ToolRegistry([{
        "name": "noop", "description": "No-op.", "parameters": {"type": "object", "properties": {}, "required": []},
        "handler": lambda args: "ok", "requires_approval": False,
    }])
    with patch("urllib.request.urlopen", return_value=response({
        "candidates": [{"content": {"parts": [{"functionCall": {"name": "noop", "args": {}}}]}}]
    })):
        result = GeminiAgent(registry, max_steps=1).run("Loop")
    assert result["status"] == "max_steps_reached"
    assert result["steps"] == 1
