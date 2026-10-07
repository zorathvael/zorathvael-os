from __future__ import annotations

import json
import os
from pathlib import Path

from lib.profit_engine.contact_discovery import enrich_leads
from lib.profit_engine.revenue import Lead, rank_outreach_leads


def load_leads(path: str = "data/revenue_leads.jsonl") -> list[Lead]:
    target = Path(path)
    if not target.exists():
        return []
    rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [
        Lead(
            source=row["source"],
            external_id=str(row["external_id"]),
            title=row["title"],
            url=row["url"],
            repository=row["repository"],
            author=row["author"],
            evidence=tuple(row.get("evidence", [])),
            score=int(row["score"]),
            offer_id=row["offer_id"],
            contact_url=row.get("contact_url", ""),
            discovered_at=row.get("discovered_at", ""),
            contact_email=row.get("contact_email"),
            contact_source=row.get("contact_source", "none"),
        )
        for row in rows
    ]


def main() -> int:
    path = "data/revenue_leads.jsonl"
    leads = load_leads(path)
    ranked = rank_outreach_leads(leads, limit=int(os.getenv("ZORATHVAEL_CONTACT_DISCOVERY_LIMIT", "10")))
    enriched = {lead.url: lead for lead in enrich_leads(ranked, token=os.getenv("GITHUB_TOKEN", "").strip())}

    rows = []
    for lead in leads:
        row = {
            "source": lead.source,
            "external_id": lead.external_id,
            "title": lead.title,
            "url": lead.url,
            "repository": lead.repository,
            "author": lead.author,
            "evidence": list(lead.evidence),
            "score": lead.score,
            "offer_id": lead.offer_id,
            "contact_url": lead.contact_url,
            "contact_email": lead.contact_email,
            "contact_source": lead.contact_source,
            "discovered_at": lead.discovered_at,
        }
        if lead.url in enriched:
            contact = enriched[lead.url]
            row["contact_url"] = contact.contact_url
            row["contact_email"] = contact.contact_email
            row["contact_source"] = contact.contact_source
        rows.append(row)

    Path(path).write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    print(json.dumps({
        "leads": len(leads),
        "contact_candidates": len(ranked),
        "public_emails_found": sum(bool(lead.contact_email) for lead in enriched.values()),
        "email_sources": sorted({lead.contact_source for lead in enriched.values()}),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
