from __future__ import annotations
import json, os
from lib.profit_engine.payment_orders import PaymentOrderStore
from lib.profit_engine.payment_verification import PaymentVerifier, BscRpcClient
from lib.profit_engine.ledger import ProfitLedger
def main():
    rpc=BscRpcClient(tuple(filter(None,os.getenv('ZORATHVAEL_BSC_RPC_URLS','https://bsc.nodereal.io,https://bsc-dataseed.bnbchain.org').split(','))))
    latest=rpc.latest_block(); window=int(os.getenv('ZORATHVAEL_SCAN_BLOCKS','1500')); start=max(0,latest-window)
    verifier=PaymentVerifier(rpc=rpc); ledger=ProfitLedger(os.getenv('ZORATHVAEL_PROFIT_LEDGER','data/profit_ledger.jsonl'))
    results=[]
    for order in PaymentOrderStore(os.getenv('ZORATHVAEL_PAYMENT_ORDERS','data/payment_orders.jsonl')).pending():
        if order.method!='usdt_bep20': continue
        try: matches=verifier.discover_usdt(order.destination,start,latest,order.amount)
        except Exception as exc: results.append({'order_id':order.order_id,'status':'scan_error','reason':str(exc)}); continue
        for match in matches:
            result=verifier.verify_usdt_tx(__import__('lib.profit_engine.payment_verification',fromlist=['PaymentIntent']).PaymentIntent(order.order_id,order.amount,order.currency,order.method,order.destination,order.created_at,order.expires_at),match['tx_hash'])
            if result.verified:
                recorded=ledger.record_verified_payment(order.order_id,match['tx_hash'],float(result.amount),order.method)
                PaymentOrderStore(os.getenv('ZORATHVAEL_PAYMENT_ORDERS','data/payment_orders.jsonl')).mark_paid(order.order_id)
                results.append({'order_id':order.order_id,'tx_hash':match['tx_hash'],'status':'verified','amount':str(result.amount),'recorded':recorded})
    print(json.dumps({'latest_block':latest,'scanned_from':start,'results':results,'ledger':ledger.summary()},indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())