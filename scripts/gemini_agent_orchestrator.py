"""Gemini-supervised Core pipeline with deterministic completion on model failure."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from lib.core_modules.ai_router.agent_core import GeminiAgent, ToolRegistry
from scripts.core_orchestrator import build_stages


def execute_stage(stage) -> dict[str, Any]:
    print(f"\n=== CORE STAGE: {stage.name} ===", flush=True)
    completed = subprocess.run(stage.command, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n", flush=True)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="" if completed.stderr.endswith("\n") else "\n", flush=True)
    return {
        "stage": stage.name,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-5000:],
        "stderr": completed.stderr[-2000:],
    }


def run_pipeline() -> int:
    stages = list(build_stages())
    results: list[dict[str, Any]] = []
    index = 0

    def status(_args: dict[str, Any]) -> dict[str, Any]:
        return {
            "total_stages": len(stages),
            "completed": len(results),
            "next_stage": stages[index].name if index < len(stages) else None,
            "failed_stages": [r["stage"] for r in results if r["returncode"] != 0],
        }

    def run_next(args: dict[str, Any]) -> dict[str, Any]:
        nonlocal index
        count = args.get("count", 3)
        if isinstance(count, bool) or not isinstance(count, int) or count < 1 or count > 3:
            raise ValueError("count must be an integer from 1 to 3")
        batch = []
        for _ in range(count):
            if index >= len(stages):
                break
            stage = stages[index]
            index += 1
            result = execute_stage(stage)
            results.append(result)
            batch.append({k: v for k, v in result.items() if k in ("stage", "returncode", "stdout", "stderr")})
        return {"ran": len(batch), "results": batch, "pipeline": status({})}

    registry = ToolRegistry([
        {
            "name": "get_pipeline_status",
            "description": "Read pipeline progress and failed stage names.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "handler": status,
            "requires_approval": False,
        },
        {
            "name": "run_next_stages",
            "description": "Run the next 1 to 3 stages in the existing fixed order; never skips or reorders stages.",
            "parameters": {
                "type": "object",
                "properties": {"count": {"type": "integer", "minimum": 1, "maximum": 3}},
                "required": ["count"],
            },
            "handler": run_next,
            "requires_approval": False,
        },
    ])
    agent = GeminiAgent(registry, max_steps=5)
    agent_result = agent.run(
        "Supervise the existing Zorathvael Core pipeline. Inspect status, call run_next_stages with count 3 "
        "repeatedly until all stages are completed, inspect the results, and report failed stages. "
        "The tool enforces the existing fixed stage order. Do not claim success without returncode 0."
    )
    print("\n=== GEMINI AGENT SUPERVISION ===")
    print(json.dumps(agent_result, ensure_ascii=False, indent=2))

    # Never let model quota, timeouts, or an early final answer leave a partial pipeline.
    if agent_result.get("status") != "success":
        print("Gemini unavailable or step limit reached; deterministically completing remaining stages.", flush=True)
    if index < len(stages):
        print(f"Completing remaining {len(stages) - index} stage(s) in deterministic order.", flush=True)
    while index < len(stages):
        stage = stages[index]
        index += 1
        results.append(execute_stage(stage))

    failed = [item for item in results if item["returncode"] != 0]
    summary = {
        "mode": "gemini_supervised_with_deterministic_completion",
        "agent_status": agent_result.get("status"),
        "stages": [{"stage": r["stage"], "returncode": r["returncode"]} for r in results],
        "completed": len(results) - len(failed),
        "failed": len(failed),
    }
    print("\n=== ZORATHVAEL CORE SUMMARY ===")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run_pipeline())
