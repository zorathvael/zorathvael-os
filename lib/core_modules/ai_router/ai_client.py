import os
import logging
import time
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
        logger.info(f"Executing AI request for provider: {provider} with prompt length: {len(prompt)}")
        
        try:
            if provider not in self.providers:
                raise ValueError(f"Unknown AI provider: {provider}")
            
            api_key = self.providers[provider]
            if not api_key:
                logger.warning(f"API key missing for provider: {provider}. Triggering fallback...")
                return self._fallback_execution(prompt)
            
            # Simulate network request & validation
            if api_key == "invalid-key":
                raise PermissionError("Invalid API key provided.")
            
            time.sleep(0.05) # simulate latency
            latency = (time.time() - start_time) * 1000
            
            logger.info(f"AI request successful for {provider} in {latency:.2f}ms")
            return {
                "status": "success",
                "provider": provider,
                "response": f"Processed '{prompt}' via {provider}",
                "latency_ms": latency
            }
        except Exception as e:
            logger.error(f"AI request failed for {provider}: {str(e)}")
            return {
                "status": "error",
                "provider": provider,
                "error": str(e),
                "fallback": self._fallback_execution(prompt)
            }

    def _fallback_execution(self, prompt: str) -> Dict[str, Any]:
        logger.info("Executing graceful fallback to local heuristic engine.")
        return {
            "status": "fallback",
            "provider": "local_heuristic",
            "response": f"Fallback processed: {prompt}"
        }
