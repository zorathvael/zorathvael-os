# Customer-Demand Research: Zorathvael Core

**Research date:** 2026-10-09  
**Purpose:** Separate evidence of a real problem from evidence that a customer will pay Zorathvael to solve it.

## Executive conclusion

There is credible qualitative evidence that CI/CD reliability and workflow automation are recurring pain areas. That is **problem evidence**, not proof of demand for Zorathvael's current products. Public competitor pages also show that some buyers are offered substantially broader automation audits and implementation services at prices far above Zorathvael's entry-level offers. The comparison is not like-for-like: Zorathvael currently promises automated, public-repository-based Markdown deliverables, while many competitors include process mapping, ROI estimates, consultations, and multi-day engagements.

**Current decision:** retain the existing low-friction prices for controlled validation; do not claim product-market fit; improve offer-to-problem matching and measure customer replies, objections, checkout behavior, and verified paid orders before changing prices or expanding the catalog.

## 1. Evidence of recurring customer pain

### CI/CD failure and debugging friction

A February 2026 discussion in r/devops lists recurring frustrations including slow feedback loops, flaky tests, YAML/syntax problems, workflows breaking unexpectedly, difficulty testing workflows locally, and secret management. Multiple commenters describe repeated reruns and debugging delays. [Source: r/devops discussion, 24 February 2026](https://www.reddit.com/r/devops/comments/1rdrpzz/whats_your_biggest_frustration_with_github/)

A March 2026 discussion describes the cycle of waiting for CI, seeing a failure, making a small change, and waiting again; commenters discuss the time cost and context switching. [Source: r/devops discussion, 12 March 2026](https://www.reddit.com/r/devops/comments/1rrvqyt/the_cicd_feedback_loop_from_hell_push_wait_8_min/)

A September 2026 discussion describes GitHub Actions as cumbersome in some environments and mentions slow infrastructure, permission friction, runner startup, and caching problems. [Source: r/devops discussion, 29 September 2026](https://www.reddit.com/r/devops/comments/1wtnlus/is_it_just_me_or_github_actions_is_overrated/)

**Implication:** a focused CI Failure Recovery offer has a clear problem category when the issue is recent, active, reproducible, and blocks a release or deployment. Outreach should mention the actual failure evidence and promise a specific diagnostic artifact—not generic “AI automation.”

**Limitation:** Reddit comments are self-selected community posts. Votes and anecdotes are not representative market sizing, and they do not prove willingness to buy from Zorathvael.

## 2. Public competitor price benchmarks

These are advertised prices, not verified transaction prices. They are directional benchmarks only.

| Provider / offer | Publicly advertised price | Scope described publicly | Comparability |
|---|---:|---|---|
| [Whispers Lab — Automation Audit](https://www.whisperslab.com/pricing) | $250 | Entry audit; audit fee credited toward a larger build | Broader business automation scope |
| [Benri — Workflow Audit](https://www.benri.to/pricing) | $500–$2,000 | Workflow map, automation candidates ranked by ROI and risk, integration requirements, proposed build scope | Broader process consulting |
| [Rama Digital Indonesia — AI Workflow Audit](https://ramadigital.id/services/ai-workflow-audit) | Rp4,000,000 | Workflow and bottleneck review, use-case prioritization, effort/risk/impact estimates, implementation roadmap | Broader business workflow audit |
| [SYSTMC — AI Workflow Audit](https://systmc.solutions/audit) | $960 early access / $1,260 listed | Multi-day workflow mapping, time-leak ledger, and deployment blueprint | Broader operational engagement |
| [SEOKRU — Automation Audit](https://www.seokru.com/pricing/automation-audit/) | $2,500–$4,500 starter tier | Process mapping, ranked opportunities, ROI estimates, and implementation cost ranges | Enterprise-oriented audit scope |

### What this means for Zorathvael

Current offers are:

- **CI Failure Recovery:** 10 USDT / Rp149,000
- **AI Automation Audit:** 10 USDT / Rp149,000
- **Automation Blueprint:** 20 USDT / Rp299,000

The low price may reduce the risk of trying a narrowly scoped, automated deliverable. It does **not** by itself make the offer attractive. The deliverable, credibility, turnaround, and relevance to the exact problem must be obvious.

There is also a naming/scope risk: “AI Automation Audit” can sound like a business-process consulting engagement, while Zorathvael's current product is a public-repository audit. The customer-facing copy should make that distinction explicit. Do not imply interviews, company-wide process mapping, quantified ROI, or production fixes unless the product actually provides them.

## 3. Problem-to-offer hypotheses

These are hypotheses to test, not validated findings.

### Hypothesis A — CI Failure Recovery

- **Buyer/problem trigger:** an active failed workflow, repeated CI failure, blocked deployment, or release delay.
- **Likely buyer:** a repository owner or maintainer responsible for shipping a working build; prioritize commercial or production repositories when evidence supports that classification.
- **Core value proposition:** identify the failing job/step, error fingerprint, likely cause, and prioritized remediation based on public logs/evidence.
- **Proof required:** the delivered report must cite the exact log/error evidence and clearly distinguish confirmed facts from hypotheses.
- **Main objection risks:** “I can fix this myself,” trust in an unknown provider, public issue not actually asking for help, or the service diagnosing without applying the fix.
- **Validation signal:** a reply asking for help/details, followed by a paid order—not merely a matching CI keyword.

### Hypothesis B — Repository Automation Audit

- **Buyer/problem trigger:** a stated bottleneck, repetitive/manual workflow, or explicit request to identify automation opportunities.
- **Likely buyer:** a maintainer or small team who can describe the current process and desired outcome.
- **Core value proposition:** a prioritized list of repository-level automation opportunities with evidence, expected benefit, effort, and risk.
- **Proof required:** each recommendation links to repository evidence and explains why it matters.
- **Main objection risks:** vague “AI audit” language, recommendations that are too generic, or a mismatch between a public-code review and the customer's actual business process.
- **Validation signal:** the prospect requests scope/details or uses the report to define a follow-on task.

### Hypothesis C — Automation Blueprint

- **Buyer/problem trigger:** an explicit request to automate a named workflow or integrate specific systems.
- **Likely buyer:** someone who already knows the workflow they want to improve and needs an implementation path.
- **Core value proposition:** a buildable sequence of steps, dependencies, data flows, failure handling, and acceptance criteria for one defined workflow.
- **Proof required:** the blueprint must be specific enough for an engineer to implement without inventing the missing requirements.
- **Main objection risks:** the customer expects working implementation rather than a plan, or the requested workflow is too underspecified.
- **Validation signal:** the prospect confirms that the scope matches their intended workflow and pays for the blueprint.

## 4. What outreach should test

The first message should make four things clear:

1. **Evidence:** quote a short, accurate detail from the issue or public repository.
2. **Consequence:** explain the operational problem only when the public evidence supports it; do not invent lost revenue, downtime, or hours wasted.
3. **Concrete outcome:** name the exact artifact the buyer receives and what it does not include.
4. **Low-friction next step:** ask whether that outcome addresses the problem, while keeping the price and order path transparent.

Test message variants by problem category, not by sending the same generic pitch to every lead. Keep the existing send cap and quality gates while collecting initial evidence.

## 5. Required research record per candidate

For each potential customer, capture these fields when evidence is publicly available:

- Problem category and short verbatim evidence excerpt
- Issue state and last-update date
- Severity/urgency evidence: release blocked, production impact, repeated failure, or deadline
- Current workaround and its cost, if explicitly stated
- Commercial context: organization/product/production use, only when supported by public evidence
- Supported offer and reason for fit
- Missing information that prevents a confident fit
- Outreach variant and date
- Response intent and any stated objection
- Checkout/order event, verified payment, delivery status, and outcome

Unknown fields must remain unknown. The engine must not infer a budget, company size, lost revenue, or willingness to pay from repository stars or keywords alone.

## 6. Measurement and decision rules

Track the funnel separately for each offer and problem segment:

1. Qualified problem instances
2. Leads with an evidence-backed offer fit
3. Outreach sent
4. Demand-relevant replies
5. Positive interest / request for details
6. Price, fit, timing, or trust objections
7. Checkout started (not currently proven by existing metrics)
8. Verified paid orders
9. Delivered results and customer feedback

Use the following interpretation:

- **Keyword match:** discovery evidence only.
- **Outreach sent:** a test exposure, not demand.
- **Reply:** engagement, not necessarily positive interest.
- **Request for details / explicit interest:** early demand signal.
- **Verified paid order:** evidence of willingness to pay.
- **Repeat purchase or a measurable successful outcome:** stronger evidence of durable value.

Do not make price or product decisions from a tiny sample. Compare cohorts only when the problem type and audience are sufficiently similar. Keep objections as first-class data so the system can learn whether the problem, offer scope, trust, or price is the main barrier.

## 7. Current evidence gap

The latest repository snapshot available during this research showed 130 qualified leads, 85 commercially relevant leads, 10 outreach-ready leads, 0 paid orders, and 0 USDT revenue. The previous outreach audit also showed 10 historical outreach events and no observed responses. This is insufficient to validate customer interest or willingness to pay.

The new code records response intent and prevents generic keyword-only product assignment, but it does not replace market research. The next decision should be driven by fresh, attributable responses and paid outcomes from the revised offers.

## Sources and interpretation limits

- [r/devops — recurring GitHub Actions frustrations (February 2026)](https://www.reddit.com/r/devops/comments/1rdrpzz/whats_your_biggest_frustration_with_github/)
- [r/devops — CI/CD feedback-loop pain (March 2026)](https://www.reddit.com/r/devops/comments/1rrvqyt/the_cicd_feedback_loop_from_hell_push_wait_8_min/)
- [r/devops — GitHub Actions experience (September 2026)](https://www.reddit.com/r/devops/comments/1wtnlus/is_it_just_me_or_github_actions_is_overrated/)
- [Whispers Lab pricing](https://www.whisperslab.com/pricing)
- [Benri pricing](https://www.benri.to/pricing)
- [Rama Digital Indonesia AI Workflow Audit](https://ramadigital.id/services/ai-workflow-audit)
- [SYSTMC AI Workflow Audit](https://systmc.solutions/audit)
- [SEOKRU Automation Audit pricing](https://www.seokru.com/pricing/automation-audit/)

Public posts and advertised prices provide directional evidence only. They are not a representative survey, and they do not establish that Zorathvael's specific products have demand.
