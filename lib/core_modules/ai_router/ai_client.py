import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIClient")


class AIClient:
    def __init__(self) -> None:
        self.providers = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY"),
            "openrouter": os.getenv("OPENROUTER_API_KEY")
        }

    def execute_request(self, provider: str, prompt: str, timeout: float = 5.0) -> Dict[str, Any]:
        start_time = time.time()
        logger.info("Executing AI request for provider: %s with prompt length: %s", provider, len(prompt))

        try:
            if provider not in self.providers:
                raise ValueError(f"Unknown AI provider: {provider}")

            api_key = self.providers[provider]
            if not api_key:
                logger.warning("API key missing for provider: %s. Triggering fallback...", provider)
                return self._fallback_execution(prompt, "missing_api_key")

            if provider == "gemini":
                response = self._execute_gemini(prompt, api_key, timeout)
                latency = (time.time() - start_time) * 1000
                logger.info("Gemini request successful in %.2fms", latency)
                return {
                    "status": "success",
                    "provider": "gemini",
                    "response": response,
                    "latency_ms": latency
                }

            # Other provider adapters are intentionally unchanged until their real API
            # contracts are implemented; do not mistake this branch for live API inference.
            if api_key == "invalid-key":
                raise PermissionError("Invalid API key provided.")

            time.sleep(0.05)
            latency = (time.time() - start_time) * 1000
            logger.info("AI request simulated for provider: %s in %.2fms", provider, latency)
            return {
                "status": "success",
                "provider": provider,
                "response": f"Processed '{prompt}' via {provider}",
                "latency_ms": latency,
                "simulated": True
            }
        except Exception as e:
            reason = self._classify_error(e)
            logger.warning("AI request failed for %s (%s); using local fallback.", provider, reason)
            result = self._fallback_execution(prompt, reason)
            result["requested_provider"] = provider
            result["error"] = str(e)
            return result

    def _execute_gemini(self, prompt: str, api_key: str, timeout: float) -> str:
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            method="POST"
        )
        # Quota/rate-limit failures are not retried here: retrying an exhausted daily
        # quota wastes time and can stall the caller. The caller gets a deterministic fallback.
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (408, 429, 500, 502, 503, 504):
                detail = exc.read().decode("utf-8", errors="replace")[:500]
                kind = "quota_exceeded" if exc.code == 429 else "provider_unavailable"
                raise RuntimeError(f"{kind}: HTTP {exc.code} {detail}") from exc
            raise RuntimeError(f"provider_error: HTTP {exc.code}") from exc

        parts = body.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "".join(str(part.get("text", "")) for part in parts if isinstance(part, dict)).strip()
        if not text:
            raise RuntimeError("provider_error: Gemini returned an empty response")
        return text

    @staticmethod
    def _classify_error(error: Exception) -> str:
        message = str(error).lower()
        if "quota_exceeded" in message or "resource_exhausted" in message or "quota exceeded" in message:
            return "quota_exceeded"
        if "provider_unavailable" in message or "timeout" in message or "timed out" in message:
            return "provider_unavailable"
        if "missing_api_key" in message:
            return "missing_api_key"
        return "provider_error"

    def _fallback_execution(self, prompt: str, reason: str = "provider_error") -> Dict[str, Any]:
        logger.info("Executing graceful fallback to local heuristic engine (%s).", reason)
        return {
            "status": "fallback",
            "provider": "local_heuristic",
            "response": f"Fallback processed: {prompt}",
            "fallback_reason": reason
        }
