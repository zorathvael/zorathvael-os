from __future__ import annotations
import argparse, uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from lib.profit_engine.payment_orders import PaymentOrder, PaymentOrderStore
from lib.profit_engine.payments import PaymentRouter
def main():
    p=argparse.ArgumentParser(); p.add_argument('--amount',type=Decimal,required=True); p.add_argument('--currency',default='USDT'); p.add_argument('--method',choices=['qris','usdt_bep20'],required=True); p.add_argument('--order-id',default=''); args=p.parse_args()
    oid=args.order_id or 'ZOR-'+uuid.uuid4().hex[:12].upper(); now=datetime.now(timezone.utc); expires=now+timedelta(hours=24)
    destination=PaymentRouter.get(args.method).destination
    order=PaymentOrder(oid,args.amount,args.currency.upper(),args.method,destination,'pending',now.isoformat(),expires.isoformat())
    PaymentOrderStore().add(order); print({'order_id':oid,'amount':str(args.amount),'currency':args.currency.upper(),'method':args.method,'destination':destination,'expires_at':expires.isoformat()})
if __name__=='__main__': main()