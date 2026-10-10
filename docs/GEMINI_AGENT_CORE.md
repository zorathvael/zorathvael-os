# Gemini Agent Core

`lib/core_modules/ai_router/agent_core.py` implements a bounded Gemini function-calling loop. Gemini can choose among host-registered tools, receive their results, and continue until it returns a final status or reaches a step limit.

Register only narrow, authorized adapters. Start with read-only operations. Write-capable actions such as publishing, sending email, payment handling, or production changes must use `requires_approval=True` and an explicit approval callback. Never expose unrestricted shell, filesystem, or network access.

HTTP 429 is not retried; quota failures return a structured fallback. Tool events are returned in an audit list, and an optional callback can persist them. The fallback is not equivalent to Gemini reasoning. Each workflow still needs its own least-privilege adapter, input validation, idempotency, and result verification. Crypto-Signal's deterministic score and Entry/SL/TP calculations remain authoritative.
