from __future__ import annotations

import json
import os
from decimal import Decimal

from lib.profit_engine.order_flow import load_orders
from lib.profit_engine.payment_verification import PaymentIntent, PaymentVerifier, BscRpcClient
from lib.profit_engine.settlement import settle_verified_order


def main() -> int:
    rpc = BscRpcClient(tuple(filter(None, os.getenv(
        "ZORATHVAEL_BSC_RPC_URLS",
        "https://bsc-rpc.publicnode.com,https://bsc.nodereal.io,https://bsc-dataseed.bnbchain.org",
    ).split(","))))
    latest = rpc.latest_block()
    window = int(os.getenv("ZORATHVAEL_SCAN_BLOCKS", "1500"))
    start = max(0, latest - window)
    verifier = PaymentVerifier(rpc=rpc)
    results = []

    for order in load_orders(os.getenv("ZORATHVAEL_PAYMENT_ORDERS", "data/revenue_orders.jsonl")):
        if order.status != "pending" or order.method != "usdt_bep20" or order.currency != "USDT":
            continue
        try:
            matches = verifier.discover_usdt(order.destination, start, latest, Decimal(str(order.amount)))
        except Exception as exc:
            results.append({"order_id": order.order_id, "issue_number": order.issue_number, "status": "scan_error", "reason": str(exc)})
            continue

        intent = PaymentIntent(
            order.order_id, order.amount, order.currency, order.method,
            order.destination, order.created_at, order.expires_at,
        )
        for match in matches:
            result = verifier.verify_usdt_tx(intent, match["tx_hash"])
            if not result.verified:
                results.append({
                    "order_id": order.order_id,
                    "issue_number": order.issue_number,
                    "tx_hash": match["tx_hash"],
                    "status": result.status,
                    "reason": result.reason,
                })
                continue
            settlement = settle_verified_order(order, result)
            results.append({
                "order_id": order.order_id,
                "issue_number": order.issue_number,
                "tx_hash": match["tx_hash"],
                "status": settlement["status"],
                "amount": str(result.amount),
                "recorded": settlement["recorded"],
                "delivered": settlement["delivered"],
                "delivery_path": settlement["delivery_path"],
            })
            if settlement["recorded"]:
                break

    print(json.dumps({
        "latest_block": latest,
        "scanned_from": start,
        "orders_checked": len(load_orders(os.getenv("ZORATHVAEL_PAYMENT_ORDERS", "data/revenue_orders.jsonl"))),
        "results": results,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
