from lib.profit_engine.revenue import offers, select_offer


def test_instant_scorecard_is_sellable():
    offer = offers()["instant_automation_scorecard"]
    assert offer.price_idr == 79000
    assert offer.price_usdt == 5.0
    assert offer.effort_minutes == 5
    assert "automatically" not in offer.delivery.lower()


def test_high_intent_lead_can_select_blueprint():
    assert select_offer(55).product_id == "automation_blueprint"
