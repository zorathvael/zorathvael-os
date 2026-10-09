from __future__ import annotations

import re


def classify_customer_response(text: str) -> str:
    """Classify a public reply as a demand signal; keyword rules are heuristic, not proof."""
    body = re.sub(r"\s+", " ", (text or "").lower()).strip()
    if not body:
        return "neutral"

    if any(phrase in body for phrase in (
        "not interested", "no thanks", "no thank you", "stop contacting",
        "don't contact", "do not contact", "irrelevant", "spam", "remove me",
    )):
        return "not_interested"
    if any(phrase in body for phrase in (
        "too expensive", "can't afford", "cannot afford", "price is too high",
        "outside my budget", "over budget", "cheaper",
    )):
        return "price_objection"
    if any(phrase in body for phrase in (
        "already fixed", "already solved", "we solved", "not our problem",
        "doesn't apply", "does not apply", "wrong repository", "not relevant",
    )):
        return "fit_objection"
    if any(phrase in body for phrase in (
        "not now", "maybe later", "next quarter", "no budget this month",
        "after release", "later this year",
    )):
        return "timing_objection"
    if any(phrase in body for phrase in (
        "how does it work", "can you explain", "send details", "more details",
        "what is included", "what's included", "scope of work", "sample report",
        "can you share", "could you share",
    )):
        return "request_for_details"
    if any(phrase in body for phrase in (
        "interested", "please send", "let's do it", "lets do it", "sounds good",
        "yes, please", "yes please", "how do i order", "how can i pay",
        "where do i pay", "i want this", "can you help",
    )):
        return "positive_interest"
    return "neutral"
