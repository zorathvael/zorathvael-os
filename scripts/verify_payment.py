from __future__ import annotations
import argparse, json
import os
from lib.profit_engine.payment_verification import PaymentVerifier, intent_from_env
from lib.profit_engine.ledger import ProfitLedger
def main() -> int:
    parser=argparse.ArgumentParser(description='Verify an actual Zorathvael USDT payment.')
    parser.add_argument('--tx-hash', required=True); args=parser.parse_args()
    r=PaymentVerifier().verify_usdt_tx(intent_from_env(), args.tx_hash)
    recorded = False
    if r.verified:
        ledger = ProfitLedger(os.getenv('ZORATHVAEL_PROFIT_LEDGER','data/profit_ledger.jsonl'))
        recorded = ledger.record_verified_payment(r.order_id, r.tx_hash or '', float(r.amount), r.method)
    print(json.dumps({'verified':r.verified,'recorded':recorded,'order_id':r.order_id,'method':r.method,'amount':str(r.amount),'tx_hash':r.tx_hash,'status':r.status,'reason':r.reason},indent=2,sort_keys=True))
    return 0 if r.verified else 1
if __name__ == '__main__': raise SystemExit(main())