from __future__ import annotations

import argparse
import json
import os

from lib.profit_engine.order_flow import load_orders
from lib.profit_engine.settlement import verify_and_settle


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify and settle an actual Zorathvael USDT payment.")
    parser.add_argument("--tx-hash", required=True)
    args = parser.parse_args()

    order_id = os.environ.get("ZORATHVAEL_ORDER_ID", "")
    orders = load_orders(os.environ.get("ZORATHVAEL_PAYMENT_ORDERS", "data/revenue_orders.jsonl"))
    order = next((item for item in orders if item.order_id == order_id and item.status == "pending"), None)
    if order is None:
        print(json.dumps({"verified": False, "status": "rejected", "reason": "pending order not found", "order_id": order_id, "issue_number": order.issue_number}))
        return 1
    if order.method != "usdt_bep20":
        print(json.dumps({"verified": False, "status": "manual_review", "reason": "only USDT BEP20 is automatically verifiable", "issue_number": order.issue_number}))
        return 1

    result = verify_and_settle(order, args.tx_hash)
    result["issue_number"] = order.issue_number
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
