from lib.profit_engine.order_flow import build_order, parse_order_body, validate_repository_url


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
