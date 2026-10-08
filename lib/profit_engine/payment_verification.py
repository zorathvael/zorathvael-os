from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55aebf7f2d7"
DEFAULT_USDT_BEP20_CONTRACT = "0x55d398326f99059fF775485246999027B3197955"
DEFAULT_RPCS = ("https://bsc-rpc.publicnode.com", "https://bsc.nodereal.io", "https://bsc-dataseed.bnbchain.org")
DEFAULT_PAYMENT_ADDRESS = "0x4ce7004e7127f8b2386eb355e088f127c24b3fac"
ZERO = Decimal("0")
TX_HASH_PATTERN = re.compile(r"^0x[a-fA-F0-9]{64}$")


@dataclass(frozen=True)
class PaymentIntent:
    order_id: str
    amount: Decimal
    currency: str
    method: str
    destination: str
    created_at: str
    expires_at: str


@dataclass(frozen=True)
class VerificationResult:
    verified: bool
    order_id: str
    method: str
    amount: Decimal
    tx_hash: str | None
    status: str
    reason: str


class BscRpcClient:
    def __init__(self, urls: tuple[str, ...] = DEFAULT_RPCS, timeout: float = 15.0) -> None:
        self.urls, self.timeout = tuple(urls), timeout

    def call(self, method: str, params: list[Any]) -> Any:
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        last_error: Exception | None = None
        for url in self.urls:
            try:
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    body = json.loads(response.read().decode())
                if "error" in body:
                    raise RuntimeError(str(body["error"]))
                return body["result"]
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"all BSC RPC endpoints failed: {last_error}")

    def chain_id(self) -> int:
        return int(self.call("eth_chainId", []), 16)

    def latest_block(self) -> int:
        return int(self.call("eth_blockNumber", []), 16)

    def finalized_block(self) -> int | None:
        try:
            block = self.call("eth_getBlockByNumber", ["finalized", False])
            if block and block.get("number"):
                return int(block["number"], 16)
        except Exception:
            return None
        return None

    def receipt(self, tx_hash: str) -> dict[str, Any] | None:
        return self.call("eth_getTransactionReceipt", [tx_hash])

    def transaction(self, tx_hash: str) -> dict[str, Any] | None:
        return self.call("eth_getTransactionByHash", [tx_hash])

    def logs(self, from_block: int, to_block: int, token_contract: str, destination: str) -> list[dict[str, Any]]:
        padded = "0x" + destination.lower().replace("0x", "").rjust(64, "0")
        return self.call("eth_getLogs", [{"fromBlock": hex(from_block), "toBlock": hex(to_block), "address": token_contract, "topics": [TRANSFER_TOPIC, None, padded]}])


class PaymentVerifier:
    def __init__(self, rpc: BscRpcClient | None = None, token_contract: str = DEFAULT_USDT_BEP20_CONTRACT, token_decimals: int = 18, confirmations: int = 2, payment_address: str = DEFAULT_PAYMENT_ADDRESS) -> None:
        self.rpc = rpc or BscRpcClient()
        self.token_contract = token_contract.lower()
        self.token_decimals = token_decimals
        self.confirmations = confirmations
        self.payment_address = payment_address.lower()

    def discover_usdt(self, destination: str, from_block: int, to_block: int, minimum_amount: Decimal = ZERO) -> list[dict[str, Any]]:
        matches = []
        for log in self.rpc.logs(from_block, to_block, self.token_contract, destination):
            topics = log.get("topics", [])
            if len(topics) < 3 or topics[0].lower() != TRANSFER_TOPIC:
                continue
            try:
                amount = Decimal(int(log.get("data", "0x0"), 16)) / (Decimal(10) ** self.token_decimals)
            except (ValueError, TypeError):
                continue
            if amount < minimum_amount:
                continue
            tx_hash = log.get("transactionHash")
            if tx_hash:
                matches.append({"tx_hash": tx_hash, "amount": amount, "block_number": int(log.get("blockNumber", "0x0"), 16)})
        return matches

    def verify_usdt_tx(self, intent: PaymentIntent, tx_hash: str) -> VerificationResult:
        tx_hash = tx_hash.strip()
        if intent.method != "usdt_bep20":
            return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "intent method is not USDT BEP20")
        if not TX_HASH_PATTERN.fullmatch(tx_hash):
            return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "invalid transaction hash format")
        if intent.destination.lower() != self.payment_address:
            return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "payment destination does not match configured wallet")
        if intent.expires_at:
            try:
                expires = datetime.fromisoformat(intent.expires_at.replace("Z", "+00:00"))
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > expires:
                    return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "payment order expired")
            except ValueError:
                return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "invalid payment order expiry")

        if self.rpc.chain_id() != 56:
            return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "RPC is not connected to BNB Smart Chain mainnet")

        receipt = self.rpc.receipt(tx_hash)
        if not receipt:
            return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "pending", "transaction not found")
        if receipt.get("status") != "0x1":
            return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "transaction execution failed")

        tx = self.rpc.transaction(tx_hash)
        if tx and (tx.get("to") or "").lower() != self.token_contract:
            return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "transaction target is not the configured USDT contract")

        tx_block = int(receipt.get("blockNumber", "0x0"), 16)
        latest = self.rpc.latest_block()
        finalized = self.rpc.finalized_block()
        if finalized is not None:
            if tx_block > finalized:
                return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "pending", "transaction is confirmed but not yet in a finalized BSC block")
        elif latest - tx_block + 1 < self.confirmations:
            return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "pending", "waiting for required BSC confirmations")

        for log in receipt.get("logs", []):
            if log.get("address", "").lower() != self.token_contract:
                continue
            topics = log.get("topics", [])
            if len(topics) < 3 or topics[0].lower() != TRANSFER_TOPIC:
                continue
            if ("0x" + topics[2][-40:]).lower() != intent.destination.lower():
                continue
            try:
                received = Decimal(int(log.get("data", "0x0"), 16)) / (Decimal(10) ** self.token_decimals)
            except (ValueError, TypeError):
                continue
            if received >= intent.amount:
                return VerificationResult(True, intent.order_id, intent.method, received, tx_hash, "verified", "finalized USDT transfer to configured destination")

        return VerificationResult(False, intent.order_id, intent.method, ZERO, tx_hash, "rejected", "no matching finalized USDT transfer found")


def intent_from_env() -> PaymentIntent:
    return PaymentIntent(
        order_id=os.environ["ZORATHVAEL_ORDER_ID"],
        amount=Decimal(os.environ["ZORATHVAEL_PAYMENT_AMOUNT"]),
        currency=os.getenv("ZORATHVAEL_PAYMENT_CURRENCY", "USDT"),
        method=os.getenv("ZORATHVAEL_PAYMENT_METHOD", "usdt_bep20"),
        destination=os.getenv("ZORATHVAEL_USDT_BEP20_ADDRESS", DEFAULT_PAYMENT_ADDRESS),
        created_at=os.getenv("ZORATHVAEL_ORDER_CREATED_AT", ""),
        expires_at=os.getenv("ZORATHVAEL_ORDER_EXPIRES_AT", ""),
    )
