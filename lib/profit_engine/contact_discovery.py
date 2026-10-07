from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from .revenue import Lead

EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Za-z0-9.!#$%&'*+/=?^_\`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+)")
URL_RE = re.compile(r"https?://[^\s<>]+")
MAILTO_RE = re.compile(r"mailto:([^?\s<>]+)", re.IGNORECASE)
CONTACT_PATHS = ("/contact", "/contact-us", "/about", "/about-us", "/support")

@dataclass(frozen=True)
class Contact:
    email: str | None
    urls: tuple[str, ...]
    source: str

def extract_public_email(user_payload: dict[str, Any]) -> str | None:
    value = user_payload.get("email")
    if not isinstance(value, str):
        return None
    match = EMAIL_RE.fullmatch(value.strip())
    return match.group(1).lower() if match else None

def extract_contact_urls(user_payload: dict[str, Any]) -> list[str]:
    candidates = [user_payload.get("blog"), user_payload.get("html_url")]
    urls: list[str] = []
    for value in candidates:
        if not isinstance(value, str) or not value.strip():
            continue
        value = value.strip()
        if not re.match(r"^https?://", value):
            value = "https://" + value
        if value not in urls:
            urls.append(value)
    return urls

def choose_contact_route(email: str | None, github_url: str | None) -> str:
    if email:
        return "email"
    if github_url:
        return "github"
    return "none"

def _get(url: str, timeout: float = 15.0, accept: str = "application/json") -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "Zorathvael-Revenue-Engine",
            "X-GitHub-Api-Version": "2026-03-10",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")

def _github_json(url: str, timeout: float = 15.0) -> dict[str, Any]:
    import json
    return json.loads(_get(url, timeout))

def _read_public_repo_text(repository: str, token: str = "", timeout: float = 15.0) -> str:
    import base64
    import json
    url = f"https://api.github.com/repos/${repository}/readme"
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "Zorathvael-Revenue-Engine",
    }
    if token:
        headers["Authorization"] = f"Bearer ${token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
        return ""
    if payload.get("encoding") == "base64" and payload.get("content"):
        try:
            return base64.b64decode(payload["content"]).decode("utf-8", errors="replace")
        except (ValueError, TypeError):
            return ""
    return payload.get("content", "") if isinstance(payload.get("content"), str) else ""

def _extract_email(text: str) -> str | None:
    for match in MAILTO_RE.findall(text):
        candidate = match.strip().lower()
        if EMAIL_RE.fullmatch(candidate) and not candidate.endswith(("@users.noreply.github.com", "@github.com")):
            return candidate
    for match in EMAIL_RE.findall(text):
        candidate = match.lower()
        if not candidate.endswith(("@users.noreply.github.com", "@github.com")):
            return candidate
    return None

def _website_pages(base_url: str) -> list[str]:
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return []
    root = f"{parsed.scheme}://{parsed.netloc}"
    return [base_url.rstrip("/")] + [root + path for path in CONTACT_PATHS]

def _discover_website_email(urls: list[str], timeout: float = 10.0) -> tuple[str | None, str | None]:
    seen: set[str] = set()
    for base in urls:
        for page in _website_pages(base):
            if page in seen:
                continue
            seen.add(page)
            try:
                html = _get(page, timeout=timeout, accept="text/html,application/xhtml+xml")
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
                continue
            email = _extract_email(html)
            if email:
                return email, page
    return None, None

def discover_contact(lead: Lead, token: str = "") -> Contact:
    try:
        user = _github_json(f"https://api.github.com/users/{urllib.parse.quote(lead.author, safe='')}")
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
        user = {}
    email = extract_public_email(user)
    urls = extract_contact_urls(user)
    if email:
        return Contact(email=email, urls=tuple(urls), source="github_public_profile")
    readme = _read_public_repo_text(lead.repository, token=token)
    email = _extract_email(readme)
    if email:
        return Contact(email=email, urls=tuple(urls), source="public_repository_readme")
    for match in URL_RE.findall(readme):
        cleaned = match.rstrip(".,;:)'\"")
        if cleaned not in urls and "github.com" not in cleaned:
            urls.append(cleaned)
    email, source_url = _discover_website_email(urls)
    if email:
        if source_url and source_url not in urls:
            urls.insert(0, source_url)
        return Contact(email=email, urls=tuple(urls), source="public_website")
    return Contact(email=None, urls=tuple(urls), source="public_profile_or_repository")

def enrich_lead(lead: Lead, token: str = "") -> Lead:
    contact = discover_contact(lead, token=token)
    return Lead(
        source=lead.source,
        external_id=lead.external_id,
        title=lead.title,
        url=lead.url,
        repository=lead.repository,
        author=lead.author,
        evidence=lead.evidence,
        score=lead.score,
        offer_id=lead.offer_id,
        contact_url=contact.urls[0] if contact.urls else lead.contact_url,
        discovered_at=lead.discovered_at,
        contact_email=contact.email,
        contact_source=contact.source,
    )

def enrich_leads(leads: list[Lead], token: str = "") -> list[Lead]:
    return [enrich_lead(lead, token=token) for lead in leads]
