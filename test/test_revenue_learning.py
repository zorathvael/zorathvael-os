from lib.profit_engine.outreach import OutreachEvent
from lib.profit_engine.revenue_learning import build_learning_snapshot


def _event(event_type: str, offer: str) -> OutreachEvent:
    return OutreachEvent(
        event_id=f"{event_type}:{offer}",
        event_type=event_type,
        lead_url="https://github.com/example/repo/issues/1",
        repository="example/repo",
        issue_number="1",
        offer_id=offer,
        occurred_at="2026-10-07T00:00:00+00:00",
        metadata={},
    )


def test_learning_counts_delivered_orders_as_paid_revenue():
    snapshot = build_learning_snapshot(
        events=[_event("outreach_sent", "ci_failure_recovery")],
        orders=[{
            "status": "delivered",
            "product_id": "ci_failure_recovery",
            "amount": "10",
            "currency": "USDT",
        }],
    )
    assert snapshot["paid_orders"] == 1
    assert snapshot["delivered_orders"] == 1
    assert snapshot["revenue_usdt"] == 10.0
    assert snapshot["offer_stats"]["ci_failure_recovery"]["paid_orders"] == 1


def test_learning_payment_rate_is_zero_without_outreach():
    snapshot = build_learning_snapshot(
        events=[],
        orders=[{
            "status": "delivered",
            "product_id": "ci_failure_recovery",
            "amount": "10",
            "currency": "USDT",
        }],
    )
    assert snapshot["offer_stats"]["ci_failure_recovery"]["payment_rate_per_outreach"] == 0.0
