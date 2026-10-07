from __future__ import annotations

import argparse
import json

from lib.profit_engine.email_delivery import send_delivery_email
from lib.profit_engine.order_flow import load_orders

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order-id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    targets = [o for o in load_orders() if o.status == "delivery_ready" and (not args.order_id or o.order_id == args.order_id)]
    results = []
    for order in targets:
        try: results.append(send_delivery_email(order, f"data/delivery_{order.order_id}.md", dry_run=args.dry_run))
        except Exception as exc: results.append({"order_id":order.order_id,"status":"failed","error":f"{type(exc).__name__}: {exc}"})
    print(json.dumps({"results":results}, indent=2, sort_keys=True))
    return 1 if any(item.get("status") == "failed" for item in results) else 0

if __name__ == "__main__":
    raise SystemExit(main())
