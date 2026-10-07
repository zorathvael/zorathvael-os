from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .revenue import Lead, buyer_intent_score, commercial_relevance_score, offers


@dataclass(frozen=True)
class OutreachEvent:
    event_id: str
    event_type: str
    lead_url: str
    repository: str
    issue_number: str
    offer_id: str
    occurred_at: str
    metadata: dict[str, object]


def _explicit_intent(lead: Lead) -> bool:
    evidence = set(lead.evidence)
    return bool(
        evidence.intersection(
            {
                "need help",
                "looking for",
                "github actions failed",
                "actions failed",
                "workflow failed",
                "failing workflow",
                "ci failed",
                "build failed",
                "deployment failed",
                "deploy failed",
                "pipeline failed",
                "cant deploy",
                "cannot deploy",
            }
        )
    )


def select_auto_outreach(
    leads: list[Lead],
    already_contacted: set[str],
    limit: int = 3,
) -> list[Lead]:
    candidates = [
        lead
        for lead in leads
        if lead.url not in already_contacted
        and _explicit_intent(lead)
        and buyer_intent_score(lead) >= 45
        and commercial_relevance_score(lead) >= 70
    ]
    return sorted(
        candidates,
        key=lambda lead: (
            buyer_intent_score(lead),
            commercial_relevance_score(lead),
            lead.score,
        ),
        reverse=True,
    )[: max(0, limit)]


def build_outreach_message(lead: Lead) -> str:
    offer = offers()[lead.offer_id]
    return (
        f"Hi @{lead.author} — I found this public issue ({lead.title}) while looking for "
        "specific problems where I can provide a concrete outcome. "
        f"Zorathvael can deliver {offer.name.lower()} for this case. "
        f"The fixed price is {offer.price_usdt:g} USDT or Rp{offer.price_idr:,}. "
        "No repository credentials are required; the service uses public repository evidence. "
        "If you want it, open the order form here: "
        "https://github.com/zorathvael/zorathvael-os/issues/new?template=order.yml&title=%5BORDER%5D%20"
    )


def load_events(path: str = "data/revenue_events.jsonl") -> list[OutreachEvent]:
    target = Path(path)
    if not target.exists():
        return []
    events: list[OutreachEvent] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            events.append(OutreachEvent(**row))
    return events


def append_event(event: OutreachEvent, path: str = "data/revenue_events.jsonl") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")


def make_event(event_type: str, lead: Lead, metadata: dict[str, object] | None = None) -> OutreachEvent:
    occurred_at = datetime.now(timezone.utc).isoformat()
    event_id = f"{event_type}:{lead.url}:{occurred_at}"
    return OutreachEvent(
        event_id=event_id,
        event_type=event_type,
        lead_url=lead.url,
        repository=lead.repository,
        issue_number=lead.external_id,
        offer_id=lead.offer_id,
        occurred_at=occurred_at,
        metadata=metadata or {},
    )
