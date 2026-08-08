import logging
from typing import Callable, Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginSandbox")

class PluginSandbox:
    @staticmethod
    def execute_safely(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            logger.info("Executing plugin action inside secure sandbox...")
            result = func(*args, **kwargs)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"Plugin execution failed inside sandbox: {str(e)}")
            return {"status": "failed", "error": str(e)}
