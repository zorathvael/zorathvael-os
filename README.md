# Zorathvael Core

> An AI execution system designed to turn real problems into verified, deliverable outcomes.

Zorathvael Core is the operational engine behind Zorathvael OS. It is designed to do more than generate answers: it can discover real problems, evaluate their value, execute defined workflows, verify results, deliver outputs, and learn from measurable outcomes.

**Operating loop:** Problem → Evidence → Solution → Verification → Delivery → Learning

---

## What Zorathvael Core Does

### Discover real problems
The Core can inspect public sources such as GitHub repositories and issues to identify concrete technical problems, including failed CI/CD workflows, build or deployment failures, repetitive manual processes, and explicit requests for technical help.

It filters low-intent and promotional noise before an opportunity enters the commercial workflow.

### Qualify opportunities
Candidate problems are evaluated using evidence such as problem clarity, active failures, commercial relevance, expected value, effort, risk, and measured conversion results. The acquisition engine also preserves a short excerpt from the public issue body so an offer can refer to the actual problem rather than only the issue title.

### Execute useful work
When a customer orders a supported service, the Core runs the appropriate workflow against the available evidence.

Current examples include:
- Diagnosing failed GitHub Actions
- Identifying failure patterns
- Auditing public repositories for automation opportunities
- Producing implementation blueprints
- Generating evidence-based reports

### Verify outcomes
The Core separates instructions, opportunities, payments, and completed outcomes.

A payment instruction is not revenue. Revenue is recorded only after the configured payment verification process confirms the transaction.

Likewise, a proposed fix is not treated as a verified result without evidence.

### Deliver results
The system produces a concrete deliverable rather than only a conversational answer.

For paid orders, the delivery lifecycle is:

```
TX hash submitted
      ↓
Deterministic BSC USDT verification
      ↓
paid
      ↓
processing
      ↓
Product generated
      ↓
delivery_ready
      ↓
Immediate AgentMail delivery attempt
      ↓
Customer email + report attachment
      ↓
delivered
```

AgentMail is used as the autonomous email transport; SMTP configuration is not required.

### Learn from outcomes
The Core records measurable events such as leads, outreach, response intent, objections, orders, verified payments, deliveries, and realized revenue. Response categories are heuristic signals, not proof of willingness to pay. A product is not considered market-validated merely because an issue matches its keywords; paid orders are the strongest demand evidence.

---

## How It Works

~~~
Discover real need
        ↓
Qualify with evidence
        ↓
Select the right service
        ↓
Customer orders
        ↓
Verify payment
        ↓
Core executes
        ↓
Verify the outcome
        ↓
Autonomous email delivery
        ↓
Measure and improve
~~~

This execution loop is the central operating model of Zorathvael Core.

---

## Current Services

| Service | Price | Customer receives |
|---|---:|---|
| **CI Failure Recovery** | Rp149,000 / 10 USDT | Evidence-based analysis of failed GitHub Actions and recovery recommendations |
| **AI Automation Audit** | Rp149,000 / 10 USDT | Analysis of a public repository for practical automation opportunities |
| **Automation Blueprint** | Rp299,000 / 20 USDT | Structured implementation blueprint for an identified automation problem |

These are the current offers. They are intentionally narrow so demand and delivery quality can be measured.

---

## For Customers

### Current customer order portal

Customers should use the GitHub Pages order portal:

**Order portal:** https://zorathvael.github.io/zorathvael-os/order/

The portal supports **English and Bahasa Indonesia**. It detects the browser language and also provides a manual language selector. GitHub Issues is used only as the order-record transport behind the portal; the customer-facing flow starts on the dedicated order page.

The current catalog uses fixed USDT prices:

- **CI Failure Recovery:** 10 USDT
- **AI Automation Audit:** 10 USDT
- **Automation Blueprint:** 20 USDT

IDR amounts shown in the portal are reference prices only; they are not converted dynamically into USDT.

### Payment

The customer-facing payment rail is **USDT on BNB Smart Chain (BEP20)**.

The official payment address is displayed directly on the customer order portal. Customers must send the exact USDT amount for the selected service through **BEP20 / BNB Smart Chain only**. ERC20, TRC20, or other networks must not be used.

The portal requires the customer to submit the **BSC transaction hash** after payment. The page validates the hash format and opens a structured GitHub order record. The Core then verifies the hash deterministically against BSC: chain ID, transaction success, USDT contract, recipient wallet, finalized block state, and received amount.

A transaction hash cannot be reused as a second payment because the profit ledger records verified transaction hashes idempotently.

Submitting the form is therefore a payment-verification request, not blind proof of payment. Revenue is recorded only after on-chain verification.

### Share a repository for Core analysis

If you want Zorathvael Core to inspect a specific public repository instead of waiting for automatic discovery, open the repository intake form:

[Share a repository with Zorathvael](https://github.com/zorathvael/zorathvael-os/issues/new?template=repository-intake.yml)

You can provide the repository URL, an optional issue URL, and optional problem context. The intake workflow records the request, fetches public repository/issue evidence, scores the commercial signal using the same revenue qualification logic, and keeps the request in measured state. The intake path does not require repository credentials.

### What do I provide?

The current services primarily work from publicly accessible evidence.

For example, CI Failure Recovery can analyze a public GitHub repository where workflows are failing.

### What happens after ordering?

1. Select a service.
2. Provide the target public repository.
3. Provide the delivery email.
4. Send the exact USDT amount shown by the portal.
5. Paste the BSC transaction hash into the portal and submit it.
6. Core verifies the transaction on-chain.
7. A valid payment moves the order directly to `paid` → `processing`.
8. The Core generates the requested product from repository evidence.
9. AgentMail delivery is attempted immediately; the scheduled delivery worker remains the recovery path if the first send cannot complete.
10. After successful email delivery, the order becomes `delivered`.

### Do I need to give access to a private repository?

Not for the current public-repository services.

The Core does not assume private repository access. A different access model would require explicit authorization.

---

## Autonomous Customer Delivery

Zorathvael Core now separates **product generation** from **customer delivery**.

- `delivery_ready` means payment is verified and the product artifact exists.
- The autonomous email worker picks up `delivery_ready` orders.
- AgentMail sends the report to the customer's submitted email address.
- The AgentMail message ID and delivery event are persisted.
- Only after the email send succeeds does the order become `delivered`.
- AgentMail's send idempotency key prevents workflow retries from sending the same order twice.

The GitHub Actions delivery worker requires these repository secrets:

- `AGENTMAIL_API_KEY`
- `AGENTMAIL_INBOX_ID`

### Outreach reply tracking

The manual Core workflow passes the IMAP response-observer configuration from GitHub Actions secrets. To track replies sent to the outreach mailbox, configure `ZORATHVAEL_IMAP_HOST`, `ZORATHVAEL_IMAP_USERNAME`, and `ZORATHVAEL_IMAP_PASSWORD`; `ZORATHVAEL_IMAP_PORT` is optional (default `993`). Optionally set the Actions variable `ZORATHVAEL_IMAP_FOLDER` (default `INBOX`). These must refer to the inbox that receives replies for the configured SMTP sender. The workflow reports a structured disabled status when required configuration is missing; successful workflow execution alone does not prove the mailbox connection or reply matching works.

The customer order portal does not require a WebsitePublisher account or `WPS_TOKEN`. Order intake is handled by GitHub Pages + GitHub Issues + GitHub Actions.

The AgentMail free tier currently supports 3 inboxes and 3,000 emails/month without a credit card. The Core does not require a paid AI API or SMTP server for this delivery path.

---

## Why This Is More Than an AI Chat

A conventional AI interaction usually ends with an answer.

Zorathvael Core is designed around an outcome lifecycle:

| Conventional AI interaction | Zorathvael Core |
|---|---|
| User asks a question | System can discover a real problem |
| Generates an answer | Executes a defined workflow |
| Result may remain unverified | Uses explicit verification stages |
| Conversation ends | Result is delivered and recorded |
| Little economic feedback | Measures demand and revenue |
| No durable operating loop | Persistent state and automated workflows |

The goal is not to claim universal superiority over every AI assistant.

The goal is to be better at turning specific real-world problems into measurable outcomes.

---

## Core Architecture

~~~
                         ZORATHVAEL CORE
                                │
       ┌────────────────────────┼────────────────────────┐
       │                        │                        │
   Intelligence              Execution               Business
       │                        │                        │
   AI Router              Workflow Engine          Profit Engine
   Memory Engine          Automation Engine        Revenue Engine
                          Integration Engine       Payment & Settlement
                          Report Engine            Delivery + AgentMail
~~~

### AI Router
Routes AI tasks to the appropriate model or capability.

### Memory Engine
Maintains persistent project and execution context.

### Workflow Engine
Runs deterministic multi-step processes.

### Automation Engine
Handles scheduled and event-driven execution.

### Integration Engine
Connects the Core to external systems.

### Report Engine
Produces structured evidence and results.

### Profit & Revenue Engine
Discovers opportunities, qualifies demand, manages offers, tracks orders, verifies configured payments, measures revenue, and learns from outcomes.

---

## Trust, Verification & Security

Zorathvael Core follows explicit operational boundaries:

- Payment instructions are not revenue.
- Revenue is recorded only after payment verification.
- Product generation and customer delivery are separate states.
- An order becomes `delivered` only after successful AgentMail submission.
- AgentMail credentials are supplied through GitHub Actions secrets.
- The Core does not custody or transfer customer funds.
- Public contact discovery uses only publicly supplied contact information.
- The system does not attempt to reveal private email addresses.
- External GitHub outreach requires appropriate write authorization.
- Customer repository access is not assumed when it has not been granted.
- Payment and delivery states are tracked separately.

---

## Current Status

### Customer-demand validation and outreach

Outreach copy is problem-first: it references the issue context, states a concrete deliverable and fixed price, and asks whether that outcome is useful. Replies are classified conservatively into positive interest, requests for details, price/fit/timing objections, and explicit disinterest. Neutral comments are not counted as demand responses. GitHub issue comments are not threaded, so response attribution remains heuristic and is labeled accordingly.

Product-demand status remains inconclusive until enough outreach and response evidence exists. The system must not manufacture products solely because a keyword was found; offers should be prioritized using repeated problem patterns, explicit buyer intent, response/objection data, and paid-order outcomes.

The repository currently contains an executable foundation for:

- AI-assisted routing and orchestration
- Persistent memory
- Automated workflows
- Public-problem discovery
- Commercial qualification
- Customer order intake through GitHub Pages with BSC transaction-hash submission
- Deterministic USDT BEP20 payment verification and TX-hash idempotency
- Evidence-based delivery generation
- Autonomous AgentMail email delivery
- Idempotent delivery tracking
- Revenue and conversion measurement
- Automated learning from outreach and delivery events
- GitHub Actions CI/CD

### Important reality check

**Actual customer revenue is not yet proven.**

The repository contains the machinery required to discover opportunities, acquire customers, process orders, verify configured payments, execute services, and measure outcomes. An implemented revenue pipeline is not the same thing as market validation.

The next proof point is:

**Real customer → Real order → Verified payment → Delivered result → Measurable outcome**

---

## Getting Started

### Customers

Open the current order form:

[Open the Zorathvael customer order portal](https://zorathvael.github.io/zorathvael-os/order/)

### Developers

Clone the repository:

~~~bash
git clone https://github.com/zorathvael/zorathvael-os.git
cd zorathvael-os
~~~

Create a virtual environment:

~~~bash
python3 -m venv venv
source venv/bin/activate
~~~

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Run the test suite:

~~~bash
PYTHONPATH=. pytest --cov=lib test/
~~~

For local environment configuration:

~~~bash
cp .env.example .env
~~~

Never commit secrets to the repository.

---

## Repository Structure

~~~
zorathvael-os/
├── lib/
│   ├── core_modules/       # Core intelligence and execution modules
│   └── profit_engine/      # Revenue, orders, payment, delivery, learning
├── scripts/                # Operational entry points
├── test/                   # Automated tests
├── docs/                   # Detailed technical documentation
├── data/                   # Runtime state and measured outcomes
└── .github/workflows/      # Automated CI/CD and scheduled operations
~~~

The README stays at the product and system level. Detailed implementation behavior belongs in the technical documentation.

---

## Documentation

- Developer Guide: [docs/DeveloperGuide.md](docs/DeveloperGuide.md)
- Deployment Guide: [docs/Deployment.md](docs/Deployment.md)
- Revenue Engine: [docs/REVENUE_ENGINE.md](docs/REVENUE_ENGINE.md)
- Customer Demand Research: [docs/CUSTOMER_DEMAND_RESEARCH.md](docs/CUSTOMER_DEMAND_RESEARCH.md)

See the [docs directory](docs/) for deeper technical and operational details.

---

## Roadmap

The Core is being developed toward a broader AI operating system that can scale across interfaces and execution environments.

Planned areas include:
- More autonomous customer communication
- More delivery channels
- Stronger outcome verification
- More domain-specific execution engines
- Android and edge interfaces
- Distributed memory
- Multi-agent consensus
- More robust economic optimization

Roadmap items are development goals, not claims of existing functionality.

---

## Contributing

Contributions are welcome.

Changes should:
1. Have a clear purpose.
2. Include tests when behavior changes.
3. Pass repository CI checks.
4. Avoid unsupported claims in customer-facing documentation.

---

## License

Zorathvael Core is licensed under the **Business Source License 1.1 (BSL 1.1)**.

This is a source-available business license, not an Open Source license before the Change Date. It permits copying, modification, derivative works, redistribution, and non-production use, while production use requires a separate commercial license because the Additional Use Grant is **None**.

For this release line:
- **Licensor:** Zorathvael
- **Licensed Work:** Zorathvael Core
- **Additional Use Grant:** None
- **Change Date:** 2028-10-08
- **Change License:** GNU GPL v2 or later

The Change Date is subject to the BSL 1.1 rule that the Change License takes effect on the stated Change Date or the fourth anniversary of the first public distribution of a specific version, whichever comes first.

Third-party components and dependencies remain subject to their own licenses. The repository's LICENSE file applies to Zorathvael-authored work.

Created by Zorathvael.
