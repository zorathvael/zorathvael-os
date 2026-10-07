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
Candidate problems are evaluated using evidence such as problem clarity, active failures, commercial relevance, expected value, effort, risk, and measured conversion results.

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

Depending on the service, this can be a diagnostic report, automation blueprint, recovery analysis, implementation guidance, or evidence package.

### Learn from outcomes
The Core records measurable events such as leads, outreach, responses, orders, verified payments, deliveries, and realized revenue. These measurements are used to improve future opportunity selection.

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
Deliver the result
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

### What do I provide?

The current services primarily work from publicly accessible evidence.

For example, CI Failure Recovery can analyze a public GitHub repository where workflows are failing.

### What happens after ordering?

1. Select a service.
2. Provide the target public repository.
3. Receive payment instructions.
4. Payment is verified through the configured verification process.
5. The Core executes the selected analysis.
6. The result is generated from repository evidence.
7. The result is delivered through the available delivery channel.

### Do I need to give access to a private repository?

Not for the current public-repository services.

The Core does not assume private repository access. A different access model would require explicit authorization.

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
                          Report Engine            Delivery & Learning
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
- The Core does not custody or transfer customer funds.
- Secrets are supplied through secure environment variables or GitHub Actions secrets.
- Public contact discovery uses only publicly supplied contact information.
- The system does not attempt to reveal private email addresses.
- External GitHub outreach requires appropriate write authorization.
- Customer repository access is not assumed when it has not been granted.
- Payment and delivery states are tracked separately.

---

## Current Status

The repository currently contains an executable foundation for:

- AI-assisted routing and orchestration
- Persistent memory
- Automated workflows
- Public-problem discovery
- Commercial qualification
- Customer order intake
- USDT payment verification
- Evidence-based delivery generation
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

[Open a Zorathvael order](https://github.com/zorathvael/zorathvael-os/issues/new?template=order.yml)

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

MIT License.

Created by Zorathvael.
