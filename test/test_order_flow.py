from decimal import Decimal

from lib.profit_engine.order_flow import (
    build_order,
    find_order_by_external_id,
    parse_order_body,
    save_order,
    validate_repository_url,
    validate_tx_hash,
)

TX = "0x" + "a" * 64


def test_parse_order_form():
    body = """### Product
public_repo_audit

### Target repository
https://github.com/example/project

### Payment method
usdt_bep20
"""
    assert parse_order_body(body) == ("public_repo_audit", "https://github.com/example/project", "usdt_bep20")


def test_order_amounts():
    order = build_order(7, "public_repo_audit", "https://github.com/example/project", "usdt_bep20")
    assert order.currency == "USDT"
    assert order.amount == 10


def test_repository_validation():
    assert validate_repository_url("https://github.com/example/project") == "https://github.com/example/project"


def test_tx_hash_validation():
    assert validate_tx_hash(TX) == TX


def test_portal_order_metadata():
    order = build_order(
        123,
        "automation_blueprint",
        "https://github.com/example/project",
        "usdt_bep20",
        "customer@example.com",
        source="websitepublisher",
        external_id="123",
        tx_hash=TX,
    )
    assert order.source == "websitepublisher"
    assert order.external_id == "123"
    assert order.tx_hash == TX
    assert order.amount == Decimal("20")
    assert order.customer_email == "customer@example.com"


def test_existing_order_lookup(tmp_path):
    path = tmp_path / "orders.jsonl"
    order = build_order(
        123,
        "public_repo_audit",
        "https://github.com/example/project",
        "usdt_bep20",
        "customer@example.com",
        source="websitepublisher",
        external_id="123",
        tx_hash=TX,
    )
    save_order(order, str(path))
    assert find_order_by_external_id("websitepublisher", "123", str(path)).order_id == order.order_id


def test_build_order_rejects_invalid_customer_email() -> None:
    try:
        build_order(42, "public_repo_audit", "https://github.com/example/repo", "usdt_bep20", "not-an-email")
    except ValueError as exc:
        assert "customer email" in str(exc)
    else:
        raise AssertionError("invalid customer email was accepted")
