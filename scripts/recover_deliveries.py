from __future__ import annotations

import json
from pathlib import Path

from lib.profit_engine.order_flow import load_orders, mark_status
from lib.profit_engine.settlement import deliver_order


def main() -> int:
    results = []
    for order in load_orders():
        if order.status not in {"paid", "delivery_pending"}:
            continue
        delivery_path = Path(f"data/delivery_{order.order_id}.md")
        if order.status == "paid" and delivery_path.exists() and "Delivery pending" not in delivery_path.read_text(encoding="utf-8"):
            mark_status(order.order_id, "delivery_ready")
            results.append({"order_id": order.order_id, "status": "delivery_ready", "reason": "existing_delivery"})
            continue
        try:
            ok, path = deliver_order(order)
            if ok:
                mark_status(order.order_id, "delivery_ready")
                results.append({"order_id": order.order_id, "status": "delivery_ready", "path": path})
        except Exception as exc:
            results.append({"order_id": order.order_id, "status": "pending", "error": type(exc).__name__})
    payload = {"results": results}
    Path("/tmp/delivery-recovery.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
