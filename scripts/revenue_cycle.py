from __future__ import annotations

import json
import os

from lib.profit_engine.engine import ProfitEngine
from lib.profit_engine.revenue import GitHubLeadScout, load_conversion_prior, make_opportunity, render_drafts, write_leads


def main() -> int:
    query = os.getenv(
        "ZORATHVAEL_LEAD_QUERY",
        'is:issue is:open ("automation" OR "automate" OR "manual" OR "integration" OR "workflow" OR "webhook")',
    )
    limit = int(os.getenv("ZORATHVAEL_LEAD_LIMIT", "20"))
    leads = GitHubLeadScout().discover(query, limit=limit)
    write_leads(leads)
    render_drafts(leads)
    prior = load_conversion_prior()
    ranked = ProfitEngine().select([make_opportunity(lead, prior) for lead in leads], limit=10)
    print(json.dumps({
        "discovered_leads": len(leads),
        "conversion_prior": prior,
        "ranked_opportunities": ranked,
        "outputs": ["data/revenue_leads.jsonl", "data/outreach_drafts.md"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
