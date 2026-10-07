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
    ProductOffer("public_repo_audit", "AI Automation Audit", "Automated public-repository audit with concrete automation opportunities, bottlenecks, and prioritized actions.", 149000, 10.0, 30, "Markdown audit delivered in the order issue."),
    ProductOffer("ci_failure_recovery", "CI Failure Recovery", "Evidence-based diagnosis of a recent GitHub Actions failure with the failing job/step, error fingerprint, likely cause, and concrete remediation path.", 149000, 10.0, 10, "Markdown recovery diagnostic delivered in the order issue."),
    ProductOffer("automation_blueprint", "Automation Blueprint", "A practical implementation blueprint for turning a public repository workflow into a measurable automation system.", 299000, 20.0, 60, "Markdown implementation blueprint delivered in the order issue."),
)

STRONG_SIGNALS: tuple[tuple[str, int], ...] = (
    ("need help", 32), ("looking for", 30), ("how to automate", 30), ("automate", 26),
    ("automation", 26), ("manual process", 24), ("repetitive", 22), ("workflow automation", 22),
    ("webhook integration", 20), ("reduce manual", 20), ("script this", 20), ("want to automate", 28),
    ("is there a way to automate", 30), ("automating", 24), ("github actions failed", 36),
    ("actions failed", 34), ("workflow failed", 34), ("failing workflow", 34), ("ci failed", 32),
    ("build failed", 32), ("deployment failed", 34), ("deploy failed", 32), ("pipeline failed", 30),
    ("cant deploy", 30), ("cannot deploy", 30),
)

WEAK_SIGNALS: tuple[tuple[str, int], ...] = (
    ("webhook", 8), ("integration", 7), ("workflow", 6), ("api", 4), ("bot", 4), ("ai", 3),
    ("cron", 3), ("github actions", 8), ("deployment", 6), ("build", 5), ("failed", 5),
)

PROMOTIONAL_NOISE: tuple[str, ...] = (
    "best ", "best-in-class", "seo", "guest post", "link building", "link exchange",
    "development company", "software company", "web development company",
    "hire us", "our services", "agency", "digital marketing", "sponsored",
)


def offers() -> dict[str, ProductOffer]:
    return {offer.product_id: offer for offer in DEFAULT_OFFERS}


def score_lead(title: str, body: str, comments: int = 0) -> tuple[int, tuple[str, ...]]:
    text = f"{title}\\n{body}".lower()
    score = 0
    evidence: list[str] = []
    strong_hit = False
    for phrase, weight in STRONG_SIGNALS:
        if re.search(r"\\b" + re.escape(phrase) + r"\\b", text):
            score += weight
            evidence.append(phrase)
            strong_hit = True
    for phrase, weight in WEAK_SIGNALS:
        if re.search(r"\\b" + re.escape(phrase) + r"\\b", text):
            score += weight
            evidence.append(phrase)
    score += min(max(int(comments), 0) * 2, 8)
    if comments:
        evidence.append(f"{comments} comments")
    if not strong_hit:
        return 0, tuple(evidence)
    return min(score, 100), tuple(evidence)


def is_commercial_noise(title: str, body: str) -> bool:
    text = f"{title}
{body}".lower()
    return any(signal in text for signal in PROMOTIONAL_NOISE)


def buyer_intent_score(lead: Lead) -> int:
    evidence = set(lead.evidence)
    score = 0
    failure = {"github actions failed", "actions failed", "workflow failed", "failing workflow", "ci failed", "build failed", "deployment failed", "deploy failed", "pipeline failed", "cant deploy", "cannot deploy"}
    if evidence & failure:
        score += 45
    if "need help" in evidence:
        score += 35
    if "looking for" in evidence:
        score += 30
    if "want to automate" in evidence or "is there a way to automate" in evidence:
        score += 25
    if "manual process" in evidence or "reduce manual" in evidence:
        score += 20
    if any(item.endswith(" comments") and int(item.split()[0]) >= 10 for item in evidence):
        score += 10
    return min(score, 100)


def commercial_relevance_score(lead: Lead) -> int:
    evidence = set(lead.evidence)
    score = lead.score + buyer_intent_score(lead) // 2
    failure = {
        "github actions failed", "actions failed", "workflow failed", "failing workflow",
        "ci failed", "build failed", "deployment failed", "deploy failed",
        "pipeline failed", "cant deploy", "cannot deploy",
    }
    if evidence & failure:
        score += 25
    if "need help" in evidence or "looking for" in evidence:
        score += 20
    if "manual process" in evidence or "reduce manual" in evidence or "want to automate" in evidence:
        score += 15
    if any(item.endswith(" comments") and int(item.split()[0]) >= 10 for item in evidence):
        score += 8
    if lead.offer_id == "ci_failure_recovery":
        score += 10
    return min(score, 100)


def rank_outreach_leads(leads: list[Lead], limit: int = 10) -> list[Lead]:
    deduped: dict[str, Lead] = {}
    for lead in leads:
        if is_commercial_noise(lead.title, ""):
            continue
        current = deduped.get(lead.url)
        if current is None or commercial_relevance_score(lead) > commercial_relevance_score(current):
            deduped[lead.url] = lead
    return sorted(
        deduped.values(),
        key=lambda lead: (buyer_intent_score(lead), commercial_relevance_score(lead), lead.score, lead.discovered_at),
        reverse=True,
    )[: max(limit, 0)]


def select_offer(score: int, evidence: tuple[str, ...] = ()) -> ProductOffer:
    failure_signals = {
        "github actions failed", "actions failed", "workflow failed", "failing workflow",
        "ci failed", "build failed", "deployment failed", "deploy failed", "pipeline failed",
        "cant deploy", "cannot deploy",
    }
    if failure_signals.intersection(evidence):
        return offers()["ci_failure_recovery"]
    return offers()["automation_blueprint"] if score >= 55 else offers()["public_repo_audit"]


def make_opportunity(lead: Lead, prior_conversion: float = 0.02) -> Opportunity:
    offer = offers()[lead.offer_id]
    probability = min(max(float(prior_conversion) + commercial_relevance_score(lead) / 1000.0, 0.01), 0.20)
    return Opportunity(
        name=f"{offer.name}: {lead.repository}#{lead.external_id}",
        kind="service",
        expected_value=offer.price_usdt,
        cost=0.0,
        probability=probability,
        effort_minutes=offer.effort_minutes,
        risk=max(0.0, 1.0 - commercial_relevance_score(lead) / 100.0),
        evidence={"source": lead.source, "lead_url": lead.url, "lead_score": lead.score, "commercial_score": commercial_relevance_score(lead), "buyer_intent_score": buyer_intent_score(lead), "prior_conversion": prior_conversion, "estimated": True},
    )


class GitHubLeadScout:
    def __init__(self, token: str | None = None, timeout: float = 20.0) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.timeout = timeout

    def _get(self, url: str) -> dict[str, Any]:
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2026-03-10", "User-Agent": "Zorathvael-Revenue-Engine"}
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
        params = urllib.parse.urlencode({"q": query, "sort": "updated", "order": "desc", "per_page": min(max(limit, 1), 50)})
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
            repository = repository_url.rsplit("/repos/", 1)[-1] if "/repos/" in repository_url else item.get("repository", {}).get("full_name", "")
            score, evidence = score_lead(item.get("title", ""), item.get("body") or "", item.get("comments", 0))
            if score < 30 or is_commercial_noise(item.get("title", ""), item.get("body") or ""):
                continue
            offer = select_offer(score, evidence)
            results.append(Lead("github_issue_search", str(item.get("number")), item.get("title", "").strip(), item.get("html_url", ""), repository, author, evidence, score, offer.product_id, item.get("user", {}).get("html_url", ""), now))
        return sorted(results, key=lambda lead: (buyer_intent_score(lead), commercial_relevance_score(lead), lead.score, lead.discovered_at), reverse=True)


def load_conversion_prior(path: str = "data/revenue_metrics.json") -> float:
    default = 0.02
    file = Path(path)
    if not file.exists():
        return default
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        qualified = int(data.get("commercially_relevant_leads", data.get("qualified_leads", 0)))
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
            handle.write(json.dumps(asdict(lead), sort_keys=True) + "
")


def render_drafts(leads: list[Lead], path: str = "data/outreach_drafts.md") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Zorathvael Revenue Acquisition Queue", "", "> Drafts only. Zorathvael does not automatically contact third parties.", ""]
    for index, lead in enumerate(leads, 1):
        offer = offers()[lead.offer_id]
        evidence = ", ".join(lead.evidence) if lead.evidence else "intent signal"
        if offer.product_id == "ci_failure_recovery":
            message = (
                f"I found your public issue: {lead.title}. The issue contains a concrete CI/deployment failure signal. "
                "I can diagnose the failing workflow/job/step, identify the error fingerprint and likely cause, and give you a concrete remediation path. "
                f"Fixed price: {offer.price_usdt:g} USDT or Rp{offer.price_idr:,}. If you want the recovery diagnostic, open the Zorathvael order form."
            )
        elif offer.product_id == "automation_blueprint":
            message = (
                f"I found your public issue: {lead.title}. The issue shows a concrete automation/integration need. "
                "I can map the current workflow, prioritize the highest-value automation opportunities, and provide implementation steps. "
                f"Fixed price: {offer.price_usdt:g} USDT or Rp{offer.price_idr:,}. If you want the blueprint, open the Zorathvael order form."
            )
        else:
            message = (
                f"I found your public issue: {lead.title}. I can audit this public repository for concrete automation bottlenecks, "
                "prioritize the highest-value opportunities, and give you an actionable report. "
                f"Fixed price: {offer.price_usdt:g} USDT or Rp{offer.price_idr:,}. If you want the audit, open the Zorathvael order form."
            )
        lines.extend([
            f"## {index}. {lead.repository}#{lead.external_id} — score {lead.score}/100",
            f"- Commercial score: {commercial_relevance_score(lead)}/100",
            f"- Buyer-intent score: {buyer_intent_score(lead)}/100",
            f"- Issue: {lead.url}",
            f"- Public profile: {lead.contact_url}",
            f"- Offer: {offer.name} — {offer.price_usdt:g} USDT / Rp{offer.price_idr:,}",
            f"- Evidence: {evidence}", "", "Suggested message:",
            f"> {message}", "",
        ])
    target.write_text("
".join(lines), encoding="utf-8")
