from __future__ import annotations

import argparse
import json

from lib.profit_engine.payments import PaymentRouter

def main() -> int:
    parser = argparse.ArgumentParser(description="Print a Zorathvael payment instruction.")
    parser.add_argument("--method", choices=["qris", "usdt_bep20"], required=True)
    parser.add_argument("--amount", type=float, required=True)
    parser.add_argument("--currency", default="IDR")
    args = parser.parse_args()
    print(json.dumps(
        PaymentRouter.checkout_instructions(args.amount, args.currency, args.method),
        indent=2,
        sort_keys=True,
    ))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())