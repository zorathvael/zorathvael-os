# Zorathvael OS

## Project Overview
Zorathvael OS is an advanced, production-ready AI Operating System designed to orchestrate multiple artificial intelligence models and autonomous workflows across diverse computing environments. Operating under the core principle of **"One Core. Many Interfaces,"** the system abstracts agentic intelligence into a unified core that scales seamlessly from mobile edge devices to cloud servers.

## Architecture
The system is built on a modular, decoupled architecture consisting of core engines that manage intelligence dispatching, persistent memory, workflow orchestration, and external integrations.

```
+---------------------------------------------------------------+
|                        Zorathvael Core                        |
|  +--------------+  +---------------+  +--------------------+  |
|  |   AI Router  |  | Memory Engine |  |  Workflow Engine   |  |
|  +--------------+  +---------------+  +--------------------+  |
|  +--------------+  +---------------+  +--------------------+  |
|  | Automation   |  | Integration   |  |   Report Engine    |  |
|  +--------------+  +---------------+  +--------------------+  |
+---------------------------------------------------------------+
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/zorathvael/zorathvael-os.git
   cd zorathvael-os
   ```
2. Set up the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Copy the environment template and provide your secure API keys:
```bash
cp .env.example .env
```

## Quick Start
Execute the test suite or integrate core engines into your Python application:
```python
from lib.core_modules.ai_router.ai_router import AIRouter
from lib.core_modules.memory_engine.memory_engine import MemoryEngine
from lib.core_modules.workflow_engine.workflow_engine import WorkflowEngine

router = AIRouter()
memory = MemoryEngine()
workflow = WorkflowEngine()

memory.store_memory("project", "Zorathvael OS")
print(memory.retrieve_memory("project"))
```

## Economic Execution Layer

Zorathvael now includes a zero-budget economic execution layer. It ranks opportunities by expected profit, profit per hour, and risk, then records measured outcomes in an append-only ledger. It does **not** fabricate revenue or treat an unexecuted opportunity as profit.

The economic loop is:
`opportunity → expected value → selection → execution boundary → measured outcome → ledger → optimization`.

GitHub Actions is the default automation backbone for the public repository; standard runners are free for public repositories. citeturn0search0

## Features
- **AI Router:** Dynamic dispatching of agent tasks to specialized AI providers.
- **Memory Engine:** State and context retention for autonomous execution.
- **Workflow Engine:** Deterministic multi-step agentic pipeline orchestration.
- **Automation & Integration:** Event-driven hooks and background schedulers.

## Folder Structure
- `lib/core_modules/`: Core system engines and modules.
- `docs/`: Comprehensive technical documentation.
- `test/`: Automated test suite.
- `.github/workflows/`: CI/CD automation pipelines.

## Development Guide
Refer to [Developer Guide](docs/DeveloperGuide.md) for contribution guidelines, coding standards, and testing procedures.

## Deployment Guide
Refer to [Deployment Guide](docs/Deployment.md) for production deployment instructions and containerization setups.

## Environment Variables
All configuration parameters must be supplied via secure environment variables as outlined in `.env.example`.

## Roadmap
- Android Interface integration via MacroDroid and Intent handlers.
- Distributed Vector Memory scaling.
- Advanced Multi-Agent Consensus protocols.

## FAQ
**Q: Is Zorathvael OS production-ready?**  
A: Yes, all core modules are fully implemented with zero placeholders, complete type hints, and rigorous test coverage.

## Contribution Guide
Contributions are welcome. Please ensure all pull requests pass CI quality checks and include corresponding unit tests.

## License
MIT License. Created by Zorathvael and Manus AI.


## Payment & Settlement

Zorathvael has a centralized payment router with two owner-configured settlement options:

1. **QRIS** — the supplied merchant QRIS reference is stored at `assets/payment_qris_reference.txt`.
2. **USDT (BEP20)** — the supplied settlement address is the default destination in `PaymentRouter`.

The payment router is separate from the profit ledger. A payment instruction is **not** revenue. Revenue is recorded only after an actual payment is confirmed.

The system does not custody funds or move funds between wallets. The selected payment network settles directly to the configured destination.


## Revenue Engine

Zorathvael now has an executable zero-budget revenue acquisition loop.

### Sellable products

| Product | Price | Delivery |
|---|---:|---|
| AI Automation Audit | Rp149,000 / 10 USDT | Automated public-repository audit |
| Automation Blueprint | Rp299,000 / 20 USDT | Automated implementation blueprint |
| Instant Automation Scorecard | Rp79,000 / 5 USDT | Instant deterministic scorecard from public GitHub data |

### Start a paid order

**[Open the Zorathvael order form](https://github.com/zorathvael/zorathvael-os/issues/new?template=order.yml)**

The customer selects the product, target public repository, and payment rail. USDT BEP20 can proceed through autonomous on-chain verification and automatic delivery.

### Autonomous loop

The Core now runs:

1. **Opportunity discovery** — scans public GitHub issues for high-intent automation problems.
2. **Economic ranking** — scores lead intent and estimates expected value using a conservative conversion prior.
3. **Customer checkout** — customer opens the order issue form and receives a unique payment order.
4. **USDT settlement verification** — BSC transaction, token contract, destination, amount, and confirmations are checked before revenue is recorded.
5. **Automatic delivery** — after verified USDT payment, the public-repository audit is generated and posted to the order issue.
6. **Measurement** — qualified leads, paid orders, delivered orders, and realized USDT revenue are persisted for recalibration.

The acquisition engine intentionally does not auto-send unsolicited messages to third parties. It produces a ranked acquisition queue and targeted drafts; the transaction begins from customer-initiated checkout.

See [Revenue Engine](docs/REVENUE_ENGINE.md) for the full flow.
