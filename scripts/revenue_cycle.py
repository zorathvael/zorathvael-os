from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from lib.profit_engine.engine import ProfitEngine
from lib.profit_engine.conversion import build_conversion_funnel
from lib.profit_engine.revenue import (
    GitHubLeadScout,
    Lead,
    STRONG_SIGNALS,
    buyer_intent_score,
    commercial_relevance_score,
    load_conversion_prior,
    make_opportunity,
    rank_outreach_leads,
    render_drafts,
    is_non_buying_meta_issue,
)


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
            "contact_email": lead.contact_email if lead.contact_email is not None else prior.get("contact_email"),
            "contact_source": lead.contact_source if lead.contact_source != "none" else prior.get("contact_source", "none"),
            "discovered_at": prior.get("discovered_at", lead.discovered_at),
        }
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(os.getenv("ZORATHVAEL_LEAD_RETENTION_DAYS", "30")))
    retained = {}
    for url, row in existing.items():
        if int(row.get("score", 0)) < 30:
            continue
        if not any(signal in set(row.get("evidence", [])) for signal, _ in STRONG_SIGNALS):
            continue
        if is_non_buying_meta_issue(row.get("title", ""), ""):
            continue
        try:
            discovered = datetime.fromisoformat(str(row.get("discovered_at", "")).replace("Z", "+00:00"))
            if discovered < cutoff:
                continue
        except ValueError:
            continue
        retained[url] = row
    existing = retained
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in existing.values()), encoding="utf-8")
    return [
        Lead(
            source=row["source"], external_id=str(row["external_id"]), title=row["title"],
            url=row["url"], repository=row["repository"], author=row["author"],
            evidence=tuple(row.get("evidence", [])), score=int(row["score"]),
            offer_id=row["offer_id"], contact_url=row.get("contact_url", ""),
            discovered_at=row.get("discovered_at", ""),
            contact_email=row.get("contact_email"), contact_source=row.get("contact_source", "none"),
        )
        for row in existing.values()
    ]


def refresh_metrics(qualified: int, commercially_relevant: int, outreach_ready: int, path: str = "data/revenue_metrics.json") -> None:
    target = Path(path)
    data = {
        "qualified_leads": qualified,
        "commercially_relevant_leads": commercially_relevant,
        "outreach_ready_leads": outreach_ready,
        "paid_orders": 0,
        "delivered_orders": 0,
        "revenue_usdt": 0.0,
        "last_updated": None,
    }
    if target.exists():
        data.update(json.loads(target.read_text(encoding="utf-8")))
    data["qualified_leads"] = qualified
    data["commercially_relevant_leads"] = commercially_relevant
    data["outreach_ready_leads"] = outreach_ready
    orders_path = Path("data/revenue_orders.jsonl")
    if orders_path.exists():
        orders = [json.loads(line) for line in orders_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        leads_path = Path("data/revenue_leads.jsonl")
        leads = [json.loads(line) for line in leads_path.read_text(encoding="utf-8").splitlines() if line.strip()] if leads_path.exists() else []
        funnel = build_conversion_funnel(leads, orders)
        data.update({
            "paid_orders": funnel["paid_orders"],
            "attributed_paid_orders": funnel["attributed_paid_orders"],
            "unattributed_paid_orders": funnel["unattributed_paid_orders"],
            "paid_revenue_orders": funnel["paid_revenue_orders"],
            "paid_revenue_usdt": funnel["paid_revenue_usdt"],
            "paid_revenue_idr": funnel["paid_revenue_idr"],
            "revenue_usdt": funnel["paid_revenue_usdt"],
        })
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    recent_since = (datetime.now(timezone.utc) - timedelta(days=int(os.getenv("ZORATHVAEL_DISCOVERY_DAYS", "14")))).date().isoformat()
    default_queries = [
        f'is:issue is:open updated:>={recent_since} ("need help" OR "looking for" OR "how to automate" OR "want to automate" OR "manual process")',
        f'is:issue is:open updated:>={recent_since} ("workflow failed" OR "actions failed" OR "ci failed" OR "build failed" OR "deployment failed" OR "deploy failed")',
    ]
    configured = os.getenv("ZORATHVAEL_LEAD_QUERY", "").strip()
    queries = [configured] if configured else default_queries
    limit = int(os.getenv("ZORATHVAEL_LEAD_LIMIT", "20"))
    scout = GitHubLeadScout()
    fresh_by_url: dict[str, Lead] = {}
    for query in queries:
        for lead in scout.discover(query, limit=limit):
            current = fresh_by_url.get(lead.url)
            if current is None or (buyer_intent_score(lead), commercial_relevance_score(lead)) > (buyer_intent_score(current), commercial_relevance_score(current)):
                fresh_by_url[lead.url] = lead
    fresh = sorted(
        fresh_by_url.values(),
        key=lambda lead: (buyer_intent_score(lead), commercial_relevance_score(lead), lead.score, lead.discovered_at),
        reverse=True,
    )
    all_leads = merge_leads("data/revenue_leads.jsonl", fresh)
    outreach_ready = rank_outreach_leads(all_leads, limit=10)
    commercially_relevant = [lead for lead in all_leads if commercial_relevance_score(lead) >= 55]
    refresh_metrics(len(all_leads), len(commercially_relevant), len(outreach_ready))
    prior = load_conversion_prior()
    render_drafts(outreach_ready)
    ranked = ProfitEngine().select(
        [make_opportunity(lead, prior) for lead in outreach_ready],
        limit=10,
    )
    print(json.dumps({
        "new_leads": len(fresh),
        "qualified_leads_total": len(all_leads),
        "commercially_relevant_leads": len(commercially_relevant),
        "outreach_ready_leads": len(outreach_ready),
        "conversion_prior": prior,
        "ranked_opportunities": ranked,
        "outputs": ["data/revenue_leads.jsonl", "data/outreach_drafts.md", "data/revenue_metrics.json"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
