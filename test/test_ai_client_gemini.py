import io
import json
import urllib.error
from unittest.mock import patch

from lib.core_modules.ai_router.ai_client import AIClient


def test_gemini_quota_exhaustion_uses_local_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    client = AIClient()
    error = urllib.error.HTTPError(
        "https://generativelanguage.googleapis.com", 429, "quota exceeded", {}, io.BytesIO(b"quota exceeded")
    )
    with patch("urllib.request.urlopen", side_effect=error):
        result = client.execute_request("gemini", "classify this task", timeout=0.1)

    assert result["status"] == "fallback"
    assert result["provider"] == "local_heuristic"
    assert result["fallback_reason"] == "quota_exceeded"


def test_gemini_success_uses_api_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    client = AIClient()
    payload = {
        "candidates": [{
            "content": {"parts": [{"text": "Gemini result"}]}
        }]
    }

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    with patch("urllib.request.urlopen", return_value=Response()) as request:
        result = client.execute_request("gemini", "analyze task", timeout=0.1)

    assert result["status"] == "success"
    assert result["provider"] == "gemini"
    assert result["response"] == "Gemini result"
    assert request.called
