# Payment Verification

## USDT (BEP20)

Zorathvael verifies a payment from a BNB Smart Chain transaction hash by checking:

1. receipt exists;
2. transaction execution succeeded;
3. the transaction has the required confirmations;
4. the configured USDT contract emitted a Transfer event;
5. the Transfer destination equals the configured wallet; and
6. the received amount is at least the order amount.

No private key is required. Zorathvael only reads public blockchain data.

BNB Chain documents BSC mainnet chain ID 56 and public RPC endpoints. The verifier reads logs embedded in the transaction receipt, so it does not require an explorer API key.

## QRIS

QRIS cannot be marked paid from the existence of an order or a screenshot. Automatic confirmation requires a provider API/webhook or trusted merchant transaction feed. Until that exists, QRIS remains a payment option with explicit confirmation required.

## Revenue boundary

Only a verified payment may be converted into a won Profit Ledger outcome. Pending or rejected payments are never revenue.