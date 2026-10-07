from __future__ import annotations

import argparse
import json

from lib.profit_engine.order_flow import build_order, parse_order_body, save_order


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", type=int, required=True)
    parser.add_argument("--body", required=True)
    args = parser.parse_args()
    product_id, repository, method = parse_order_body(args.body)
    order = build_order(args.issue_number, product_id, repository, method)
    save_order(order)
    print(json.dumps({
        "order_id": order.order_id,
        "issue_number": order.issue_number,
        "product_id": order.product_id,
        "target_repository": order.target_repository,
        "amount": str(order.amount),
        "currency": order.currency,
        "method": order.method,
        "destination": order.destination,
        "expires_at": order.expires_at,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
