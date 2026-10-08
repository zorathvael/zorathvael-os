from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    name: str
    command: tuple[str, ...]


def build_stages() -> tuple[Stage, ...]:
    return (
        Stage("revenue_acquisition", (sys.executable, "scripts/revenue_cycle.py")),
        Stage("contact_discovery", (sys.executable, "scripts/discover_contacts.py")),
        Stage("qualified_outreach", (sys.executable, "scripts/execute_outreach.py")),
        Stage("github_response_observation", (sys.executable, "scripts/observe_outreach_responses.py")),
        Stage("email_response_observation", (sys.executable, "scripts/observe_email_responses.py")),
        Stage("payment_verification", (sys.executable, "scripts/scan_usdt_payments.py")),
        Stage("delivery_recovery", (sys.executable, "scripts/recover_deliveries.py")),
        Stage("agentmail_delivery", (sys.executable, "scripts/send_delivery_email.py")),
        Stage(
            "revenue_learning",
            (
                sys.executable,
                "-c",
                "from lib.profit_engine.revenue_learning import write_learning_snapshot; import json; print(json.dumps(write_learning_snapshot(), indent=2, sort_keys=True))",
            ),
        ),
    )


def run_stage(stage: Stage) -> dict[str, object]:
    print(f"\n=== CORE STAGE: {stage.name} ===", flush=True)
    completed = subprocess.run(stage.command, text=True)
    result = {"stage": stage.name, "returncode": completed.returncode}
    print(json.dumps(result, sort_keys=True), flush=True)
    return result


def main() -> int:
    results = [run_stage(stage) for stage in build_stages()]
    failed = [item for item in results if item["returncode"] != 0]
    summary = {
        "mode": "master_orchestrator",
        "stages": results,
        "completed": len(results) - len(failed),
        "failed": len(failed),
    }
    print("\n=== ZORATHVAEL CORE SUMMARY ===")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
