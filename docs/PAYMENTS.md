# Zorathvael Payment Routing

Zorathvael Core now has one payment-routing layer with two settlement options supplied by the owner:

- **QRIS**: the supplied merchant QRIS is represented by the payment reference in `assets/payment_qris_reference.txt`.
- **USDT (BEP20)**: the configured settlement address is the destination for USDT payments on BNB Smart Chain.

## Settlement principle

The payment network settles funds directly to the configured merchant/wallet destination. Zorathvael does not custody funds and does not move funds between accounts.

A payment instruction is not revenue. The Profit Ledger must receive a confirmed outcome before it counts revenue or net profit.

## Environment overrides

- `ZORATHVAEL_QRIS_IMAGE`
- `ZORATHVAEL_USDT_BEP20_ADDRESS`

The default USDT address is configured from the owner-supplied payment destination. Treat the network as **BEP20 only**.

## Operational boundary

QRIS confirmation requires the merchant/payment provider's transaction confirmation unless a provider webhook/API is later connected.

USDT confirmation requires an on-chain transaction check before recording revenue. The current router intentionally does not fabricate confirmation.