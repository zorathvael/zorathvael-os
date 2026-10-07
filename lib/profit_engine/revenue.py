from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Opportunity


@dataclass(frozen=True)
class ProductOffer:
    product_id: str
    name: str
    description: str
    price_idr: int
    price_usdt: float
    effort_minutes: int
    delivery: str


@dataclass(frozen=True)
class Lead:
    source: str
    external_id: str
    title: str
    url: str
    repository: str
    author: str
    evidence: tuple[str, ...]
    score: int
    offer_id: str
    contact_url: str
    discovered_at: str


DEFAULT_OFFERS = (
    ProductOffer(
        "public_repo_audit",
        "AI Automation Audit",
        "Automated public-repository audit with concrete automation opportunities, bottlenecks, and prioritized actions.",
        149000,
        10.0,
        30,
        "Markdown audit delivered in the order issue.",
    ),
    ProductOffer(
        "automation_blueprint",
        "Automation Blueprint",
        "A practical implementation blueprint for turning a public repository workflow into a measurable automation system.",
        299000,
        20.0,
        60,
        "Markdown implementation blueprint delivered in the order issue.",
    ),
    ProductOffer(
        "instant_automation_scorecard",
        "Instant Automation Scorecard",
        "A deterministic public-repository scorecard covering automation maturity, CI reliability signals, maintenance pressure, and the highest-value next actions.",
        79000,
        5.0,
        5,
        "Instant Markdown scorecard generated from public GitHub data and delivered in the order issue.",
    ),
)

STRONG_SIGNALS: tuple[tuple[str, int], ...] = (
    ("need help", 32),
    ("looking for", 30),
    ("how to automate", 30),
    ("automate", 26),
    ("automation", 26),
    ("manual process", 24),
    ("repetitive", 22),
    ("workflow automation", 22),
    ("webhook integration", 20),
    ("reduce manual", 20),
    ("script this", 20),
    ("want to automate", 28),
    ("is there a way to automate", 30),
    ("automating", 24),
)

WEAK_SIGNALS: tuple[tuple[str, int], ...] = (
    ("webhook", 8),
    ("integration", 7),
    ("workflow", 6),
    ("api", 4),
    ("bot", 4),
    ("ai", 3),
    ("cron", 3),
)


def offers() -> dict[str, ProductOffer]:
    return {offer.product_id: offer for offer in DEFAULT_OFFERS}


def score_lead(title: str, body: str, comments: int = 0) -> tuple[int, tuple[str, ...]]:
    text = f"{title}\n{body}".lower()
    score = 0
    evidence: list[str] = []
    strong_hit = False
    for phrase, weight in STRONG_SIGNALS:
        if re.search(r"\b" + re.escape(phrase) + r"\b", text):
            score += weight
            evidence.append(phrase)
            strong_hit = True
    for phrase, weight in WEAK_SIGNALS:
        if re.search(r"\b" + re.escape(phrase) + r"\b", text):
            score += weight
            evidence.append(phrase)
    score += min(max(int(comments), 0) * 2, 8)
    if comments:
        evidence.append(f"{comments} comments")
    if not strong_hit:
        return 0, tuple(evidence)
    return min(score, 100), tuple(evidence)


def select_offer(score: int) -> ProductOffer:
    return offers()["automation_blueprint"] if score >= 55 else offers()["public_repo_audit"]


def make_opportunity(lead: Lead, prior_conversion: float = 0.02) -> Opportunity:
    offer = offers()[lead.offer_id]
    probability = min(max(float(prior_conversion) + lead.score / 1000.0, 0.01), 0.20)
    return Opportunity(
        name=f"{offer.name}: {lead.repository}#{lead.external_id}",
        kind="service",
        expected_value=offer.price_usdt,
        cost=0.0,
        probability=probability,
        effort_minutes=offer.effort_minutes,
        risk=max(0.0, 1.0 - lead.score / 100.0),
        evidence={
            "source": lead.source,
            "lead_url": lead.url,
            "lead_score": lead.score,
            "prior_conversion": prior_conversion,
            "estimated": True,
        },
    )


class GitHubLeadScout:
    def __init__(self, token: str | None = None, timeout: float = 20.0) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.timeout = timeout

    def _get(self, url: str) -> dict[str, Any]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "Zorathvael-Revenue-Engine",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"GitHub API request failed ({exc.code}): {detail}") from exc

    def discover(self, query: str, limit: int = 20) -> list[Lead]:
        params = urllib.parse.urlencode({
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": min(max(limit, 1), 50),
        })
        data = self._get(f"https://api.github.com/search/issues?{params}")
        now = datetime.now(timezone.utc).isoformat()
        results: list[Lead] = []
        for item in data.get("items", []):
            if item.get("pull_request"):
                continue
            author = item.get("user", {}).get("login", "")
            if author.endswith("[bot]"):
                continue
            repository_url = item.get("repository_url", "")
            repository = repository_url.rsplit("/repos/", 1)[-1] if "/repos/" in repository_url else ""
            if not repository:
                repository = item.get("repository", {}).get("full_name", "")
            score, evidence = score_lead(item.get("title", ""), item.get("body") or "", item.get("comments", 0))
            if score < 30:
                continue
            offer = select_offer(score)
            results.append(
                Lead(
                    source="github_issue_search",
                    external_id=str(item.get("number")),
                    title=item.get("title", "").strip(),
                    url=item.get("html_url", ""),
                    repository=repository,
                    author=author,
                    evidence=evidence,
                    score=score,
                    offer_id=offer.product_id,
                    contact_url=item.get("user", {}).get("html_url", ""),
                    discovered_at=now,
                )
            )
        return sorted(results, key=lambda lead: (lead.score, lead.discovered_at), reverse=True)


def load_conversion_prior(path: str = "data/revenue_metrics.json") -> float:
    default = 0.02
    file = Path(path)
    if not file.exists():
        return default
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        qualified = int(data.get("qualified_leads", 0))
        paid = int(data.get("paid_orders", 0))
        if qualified > 0:
            return min(max(paid / qualified, 0.01), 0.20)
    except (ValueError, OSError, TypeError):
        pass
    return default


def write_leads(leads: list[Lead], path: str = "data/revenue_leads.jsonl") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for lead in leads:
            handle.write(json.dumps(asdict(lead), sort_keys=True) + "\n")


def render_drafts(leads: list[Lead], path: str = "data/outreach_drafts.md") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Zorathvael Revenue Acquisition Queue",
        "",
        "> Drafts only. Zorathvael does not automatically contact third parties.",
        "",
    ]
    for index, lead in enumerate(leads, 1):
        offer = offers()[lead.offer_id]
        evidence = ", ".join(lead.evidence) if lead.evidence else "intent signal"
        lines.extend([
            f"## {index}. {lead.repository}#{lead.external_id} — score {lead.score}/100",
            f"- Issue: {lead.url}",
            f"- Public profile: {lead.contact_url}",
            f"- Offer: {offer.name} — {offer.price_usdt:g} USDT / Rp{offer.price_idr:,}",
            f"- Evidence: {evidence}",
            "",
            "Suggested message:",
            f"> I found your public issue: {lead.title}. "
            f"Detected intent signals: {evidence}. "
            f"I can provide a {offer.name} focused on this repository, "
            "with prioritized automation opportunities and implementation steps. "
            f"Fixed price: {offer.price_usdt:g} USDT or Rp{offer.price_idr:,}. "
            "If you want the audit, open the Zorathvael order form.",
            "",
        ])
    target.write_text("\n".join(lines), encoding="utf-8")
