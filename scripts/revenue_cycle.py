from __future__ import annotations

import json
import os
from pathlib import Path

from lib.profit_engine.engine import ProfitEngine
from lib.profit_engine.revenue import GitHubLeadScout, Lead, STRONG_SIGNALS, load_conversion_prior, make_opportunity, render_drafts


def merge_leads(path: str, fresh: list[Lead]) -> list[Lead]:
    target = Path(path)
    existing: dict[str, dict] = {}
    if target.exists():
        for line in target.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                existing[row["url"]] = row
    for lead in fresh:
        prior = existing.get(lead.url, {})
        existing[lead.url] = {
            "source": lead.source, "external_id": lead.external_id, "title": lead.title,
            "url": lead.url, "repository": lead.repository, "author": lead.author,
            "evidence": list(lead.evidence), "score": lead.score, "offer_id": lead.offer_id,
            "contact_url": lead.contact_url,
            "discovered_at": prior.get("discovered_at", lead.discovered_at),
        }
    existing = {
        url: row for url, row in existing.items()
        if int(row.get("score", 0)) >= 30
        and any(signal in set(row.get("evidence", [])) for signal, _ in STRONG_SIGNALS)
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in existing.values()), encoding="utf-8")
    return [Lead(
        source=row["source"], external_id=str(row["external_id"]), title=row["title"],
        url=row["url"], repository=row["repository"], author=row["author"],
        evidence=tuple(row.get("evidence", [])), score=int(row["score"]),
        offer_id=row["offer_id"], contact_url=row.get("contact_url", ""),
        discovered_at=row.get("discovered_at", ""),
    ) for row in existing.values()]


def refresh_metrics(qualified: int, path: str = "data/revenue_metrics.json") -> None:
    target = Path(path)
    data = {"qualified_leads": qualified, "paid_orders": 0, "delivered_orders": 0, "revenue_usdt": 0.0, "last_updated": None}
    if target.exists():
        data.update(json.loads(target.read_text(encoding="utf-8")))
    data["qualified_leads"] = qualified
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    query = os.getenv("ZORATHVAEL_LEAD_QUERY", 'is:issue is:open ("need help" OR "looking for" OR "automate" OR "automation")')
    limit = int(os.getenv("ZORATHVAEL_LEAD_LIMIT", "20"))
    fresh = GitHubLeadScout().discover(query, limit=limit)
    all_leads = merge_leads("data/revenue_leads.jsonl", fresh)
    refresh_metrics(len(all_leads))
    prior = load_conversion_prior()
    render_drafts(fresh)
    ranked = ProfitEngine().select([make_opportunity(lead, prior) for lead in fresh], limit=10)
    print(json.dumps({
        "new_leads": len(fresh), "qualified_leads_total": len(all_leads),
        "conversion_prior": prior, "ranked_opportunities": ranked,
        "outputs": ["data/revenue_leads.jsonl", "data/outreach_drafts.md", "data/revenue_metrics.json"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
