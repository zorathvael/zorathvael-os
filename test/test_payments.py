from lib.profit_engine.payments import PaymentRouter

def test_payment_router_exposes_two_settlement_options():
    methods = {item.method for item in PaymentRouter.options()}
    assert methods == {"qris", "usdt_bep20"}

def test_usdt_destination_is_configured():
    option = PaymentRouter.get("usdt_bep20")
    assert option.destination.startswith("0x")
    assert len(option.destination) == 42

def test_checkout_does_not_claim_payment_confirmation():
    checkout = PaymentRouter.checkout_instructions(100.0, "IDR", "qris")
    assert "confirmed" not in str(checkout).lower()
    assert checkout["verification"].startswith("provider/manual")