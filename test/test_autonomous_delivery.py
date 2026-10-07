from lib.profit_engine.order_flow import build_order, parse_customer_email, parse_order_body


def test_parse_customer_email_from_issue_form() -> None:
    body = """
### Product
public_repo_audit

### Target repository
https://github.com/example/repo

### Customer email
customer@example.com

### Payment method
usdt_bep20
"""
    assert parse_order_body(body) == ("public_repo_audit", "https://github.com/example/repo", "usdt_bep20")
    assert parse_customer_email(body) == "customer@example.com"


def test_build_order_persists_customer_email() -> None:
    order = build_order(42, "public_repo_audit", "https://github.com/example/repo", "usdt_bep20", "customer@example.com")
    assert order.customer_email == "customer@example.com"
    assert order.status == "pending"


def test_build_order_rejects_invalid_customer_email() -> None:
    try:
        build_order(42, "public_repo_audit", "https://github.com/example/repo", "usdt_bep20", "not-an-email")
    except ValueError as exc:
        assert "customer email" in str(exc)
    else:
        raise AssertionError("invalid customer email was accepted")
