# Zorathvael Revenue Engine

## Purpose

The Revenue Engine is the first economic acquisition loop of Zorathvael OS.

It automatically:
1. discovers public high-intent automation problems;
2. ranks opportunities against measurable assumptions;
3. exposes fixed-price products with a deterministic checkout path;
4. verifies USDT BEP20 payments before revenue is recorded;
5. generates and delivers a public-repository automation audit after verified payment.

## Products

| Product | IDR | USDT | Delivery |
|---|---:|---:|---|
| AI Automation Audit | Rp149,000 | 10 USDT | Automated Markdown audit |
| Automation Blueprint | Rp299,000 | 20 USDT | Automated implementation blueprint |

Pricing is launch pricing and can be changed in the catalog.

## Acquisition

The revenue-cycle workflow runs every two hours. It searches GitHub issues for explicit automation and integration pain signals and writes a ranked acquisition queue.

Outbound contact is guarded by explicit problem-intent checks, repository health, duplicate prevention, repository cooldown, and a daily send cap. When an external outreach token or email transport is configured, the workflow can send the selected message automatically. Messages must stay problem-specific and transparent about scope and price; they must not claim a diagnosis has already been completed.

GitHub issue comments are flat rather than threaded. The response observer therefore treats post-outreach comments as heuristic evidence, records only demand-relevant classifications, and does not count neutral discussion as customer interest.

## Checkout

A buyer opens the Buy a Zorathvael Automation Product issue form.

The order workflow creates a unique order ID and posts payment instructions.

USDT BEP20 is the autonomous path:

order -> payment -> BSC receipt -> confirmations -> ERC20 Transfer verification -> ledger -> delivery.

QRIS is supported, but automatic verification requires a trusted merchant/provider feed. A static QR reference is not sufficient evidence of settlement.

## Customer-demand validation

The issue title alone is not sufficient product research. The scout retains a bounded excerpt from the public issue body so outreach can name the actual pain and explain the matching deliverable. Product assignment now requires evidence that fits a supported problem category: active CI/deployment failure, an explicit automation implementation request, or a stated bottleneck/manual-process audit need. Generic help requests and low-quality signals do not receive a product assignment; repository intake requests with no clear fit are sent back for problem clarification.

These categories are weak qualitative evidence, not statistically validated customer research. Small samples are labeled inconclusive. A product hypothesis should be strengthened by repeated independent problem instances, specific customer replies, and—most importantly—verified paid orders. Keyword matches, issue comments, or outreach sends are not proof of product-market fit.

## Economic integrity

Expected profit is never recorded as revenue. The ledger records revenue only after verified payment.

Lead conversion starts with a conservative prior and is recalibrated from actual paid orders.

## Safety boundary

The acquisition engine discovers public opportunities but does not automatically contact third parties. The customer-initiated checkout is the transaction boundary.

The delivery engine uses public GitHub repository data only and does not request private credentials.

## Zero-budget architecture

The engine runs on standard GitHub-hosted runners. GitHub documents standard runners as free for public repositories. The repository can therefore run the acquisition and payment-verification loops without a paid server.
