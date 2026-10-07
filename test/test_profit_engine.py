from pathlib import Path

from lib.profit_engine import Opportunity, Outcome, ProfitEngine, ProfitLedger

def test_engine_rejects_negative_expected_profit() -> None:
    engine = ProfitEngine()
    opportunities = [
        Opportunity("bad", "service", expected_value=10, cost=9, probability=0.5, effort_minutes=30),
        Opportunity("good", "service", expected_value=100, cost=2, probability=0.8, effort_minutes=60),
    ]
    selected = engine.select(opportunities, limit=3)
    assert [item["name"] for item in selected] == ["good"]

def test_engine_prioritizes_profit_per_hour() -> None:
    engine = ProfitEngine()
    opportunities = [
        Opportunity("slow", "service", 100, 0, 0.9, 120),
        Opportunity("fast", "service", 40, 0, 0.9, 20),
    ]
    selected = engine.select(opportunities, limit=2)
    assert selected[0]["name"] == "fast"

def test_ledger_records_measured_net_profit(tmp_path: Path) -> None:
    ledger = ProfitLedger(str(tmp_path / "ledger.jsonl"))
    ledger.record(Outcome("sale", 25, 3, "won"))
    ledger.record(Outcome("failed_sale", 0, 2, "lost"))
    summary = ledger.summary()
    assert summary["trades"] == 2
    assert summary["wins"] == 1
    assert summary["net_profit"] == 20
