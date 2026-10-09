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

### Email response observation setup

The manual 9-stage workflow must receive these repository **Actions secrets** for IMAP response observation:

- `ZORATHVAEL_IMAP_HOST`
- `ZORATHVAEL_IMAP_USERNAME`
- `ZORATHVAEL_IMAP_PASSWORD`
- `ZORATHVAEL_IMAP_PORT` (optional; defaults to `993`)

`ZORATHVAEL_IMAP_FOLDER` is an optional Actions variable (defaults to `INBOX`). Configure the inbox credentials for the mailbox that receives replies to the configured SMTP sender. Do not put credentials in repository files. The workflow now passes these values into the observer and the observer emits structured status when configuration is missing or no email outreach events exist. A configured IMAP connection still needs a successful manual run to validate credentials, mailbox access, and actual response matching. GitHub issue-comment response observation remains a separate channel.

## Checkout

A buyer opens the Buy a Zorathvael Automation Product issue form.

The order workflow creates a unique order ID and posts payment instructions.

USDT BEP20 is the autonomous path:

order -> payment -> BSC receipt -> confirmations -> ERC20 Transfer verification -> ledger -> delivery.

QRIS is supported, but automatic verification requires a trusted merchant/provider feed. A static QR reference is not sufficient evidence of settlement.

## Customer-demand validation

The issue title alone is not sufficient product research. The scout retains a bounded excerpt from the public issue body so outreach can name the actual pain and explain the matching deliverable. Product assignment now requires evidence that fits a supported problem category: active CI/deployment failure, an explicit automation implementation request, or a stated bottleneck/manual-process audit need. Generic help requests and low-quality signals do not receive a product assignment; repository intake requests with no clear fit are sent back for problem clarification. Outreach excerpts must be problem-focused; arbitrary first-paragraph text and known operational recaps are rejected in favor of the issue title. Legacy lead records are revalidated during queue retention: records without a supported offer fit are removed from the qualified queue, and retained records have their offer assignment recalculated from current evidence. This prevents old generic keyword matches from inflating qualified-lead metrics or reappearing in drafts. Cleanup runs when the acquisition cycle next refreshes persisted lead state; it does not rewrite historical outreach events.

These categories are weak qualitative evidence, not statistically validated customer research. Small samples are labeled inconclusive. A product hypothesis should be strengthened by repeated independent problem instances, specific customer replies, and—most importantly—verified paid orders. Keyword matches, issue comments, or outreach sends are not proof of product-market fit.

## Economic integrity

Expected profit is never recorded as revenue. The ledger records revenue only after verified payment.

Lead conversion starts with a conservative prior and is recalibrated from actual paid orders.

## Safety boundary

Public issue discovery can lead to automated, problem-specific GitHub issue-comment outreach when the required write token is configured. Outreach is gated by offer fit, buyer intent, repository health, duplicate prevention, repository cooldown, and daily limits. The customer-initiated checkout remains the transaction boundary; a public comment is not an order, consent to private contact, or proof of demand.

The delivery engine uses public GitHub repository data only and does not request private credentials.

## Zero-budget architecture

The engine runs on standard GitHub-hosted runners. GitHub documents standard runners as free for public repositories. The repository can therefore run the acquisition and payment-verification loops without a paid server.


## Outreach publication quality gate

Before a lead can enter the outreach queue or be sent by email/GitHub, its title and extracted context must contain a concrete symptom or operational pain aligned with the assigned offer. CI recovery requires a failure symptom; repository audit requires explicit operational pain (for example manual/repetitive work or a bottleneck); automation blueprint requires an explicit implementation request. Workspace recaps, execution checklists, and repository-operating instructions are rejected. The same guard is applied at selection and again immediately before external delivery.
