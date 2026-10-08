from decimal import Decimal
from lib.profit_engine.payment_verification import PaymentIntent, PaymentVerifier
TX='0x' + 'a' * 64
TO='0x4ce7004e7127f8b2386eb355e088f127c24b3fac'
TOKEN='0x55d398326f99059ff775485246999027b3197955'
TOPIC='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55aebf7f2d7'
class FakeRpc:
    def receipt(self, tx_hash):
        return {'status':'0x1','blockNumber':'0x64','logs':[{'address':TOKEN,'topics':[TOPIC,'0x'+'11'*32,'0x'+TO.rjust(64,'0')],'data':hex(125*10**18),'transactionHash':tx_hash}]}
    def latest_block(self): return 0x80
def intent(amount='100', destination=TO): return PaymentIntent('ORD-1',Decimal(amount),'USDT','usdt_bep20',destination,'','')
def test_verifies_matching_confirmed_transfer():
    r=PaymentVerifier(rpc=FakeRpc(),confirmations=12).verify_usdt_tx(intent(),'0xabc')
    assert r.verified and r.amount == Decimal('125')
def test_rejects_wrong_destination():
    r=PaymentVerifier(rpc=FakeRpc(),confirmations=12).verify_usdt_tx(intent(destination='0x1111111111111111111111111111111111111111'),'0xabc')
    assert not r.verified and r.status == 'rejected'

def test_verified_payment_is_idempotent(tmp_path):
    from lib.profit_engine import ProfitLedger
    ledger = ProfitLedger(str(tmp_path / 'ledger.jsonl'))
    assert ledger.record_verified_payment('ORD-9', '0xtx', 50.0) is True
    assert ledger.record_verified_payment('ORD-9', '0xtx', 50.0) is False
    assert ledger.summary()['revenue'] == 50.0
