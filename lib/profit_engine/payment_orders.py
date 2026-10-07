from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
@dataclass(frozen=True)
class PaymentOrder:
    order_id: str
    amount: Decimal
    currency: str
    method: str
    destination: str
    status: str = 'pending'
    created_at: str = ''
    expires_at: str = ''
class PaymentOrderStore:
    def __init__(self, path='data/payment_orders.jsonl'): self.path=Path(path)
    def add(self, order: PaymentOrder) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a',encoding='utf-8') as f: f.write(json.dumps({**asdict(order),'amount':str(order.amount)},sort_keys=True)+'\n')
    def mark_paid(self, order_id: str) -> None:
        if not self.path.exists(): return
        rows=[json.loads(x) for x in self.path.read_text(encoding='utf-8').splitlines() if x.strip()]
        for row in rows:
            if row.get('order_id') == order_id: row['status']='paid'
        self.path.write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows),encoding='utf-8')

    def pending(self) -> list[PaymentOrder]:
        if not self.path.exists(): return []
        rows=[json.loads(x) for x in self.path.read_text(encoding='utf-8').splitlines() if x.strip()]
        return [PaymentOrder(order_id=x['order_id'],amount=Decimal(x['amount']),currency=x['currency'],method=x['method'],destination=x['destination'],status=x.get('status','pending'),created_at=x.get('created_at',''),expires_at=x.get('expires_at','')) for x in rows if x.get('status','pending')=='pending']