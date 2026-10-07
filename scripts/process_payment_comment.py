from __future__ import annotations

import argparse
import json

from lib.profit_engine.order_flow import find_pending_issue
from lib.profit_engine.settlement import verify_and_settle

import re

TX_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{64}\b")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", type=int, required=True)
    parser.add_argument("--comment", required=True)
    args = parser.parse_args()

    match = TX_PATTERN.search(args.comment)
    if not match:
        print(json.dumps({"status": "ignored", "reason": "no BSC transaction hash found"}))
        return 0

    order = find_pending_issue(args.issue_number)
    if order is None:
        print(json.dumps({"status": "ignored", "reason": "no pending revenue order for issue"}))
        return 0

    if order.method != "usdt_bep20":
        print(json.dumps({"status": "manual_review", "reason": "QRIS payment requires provider verification"}))
        return 0

    payload = verify_and_settle(order, match.group(0))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
