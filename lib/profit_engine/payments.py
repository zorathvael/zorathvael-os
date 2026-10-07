from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

PaymentMethod = Literal["qris", "usdt_bep20"]

@dataclass(frozen=True)
class PaymentOption:
    method: PaymentMethod
    label: str
    destination: str
    instructions: str

class PaymentRouter:
    """Single source of truth for Zorathvael payment destinations.

    Funds settle directly through the selected payment network/provider.
    Zorathvael creates payment instructions and records/reconciles outcomes;
    it never treats an unconfirmed instruction as revenue.
    """

    QRIS_IMAGE = os.getenv("ZORATHVAEL_QRIS_IMAGE", "assets/payment_qris_reference.txt")
    USDT_BEP20_ADDRESS = os.getenv(
        "ZORATHVAEL_USDT_BEP20_ADDRESS",
        "0x4ce7004e7127f8b2386eb355e088f127c24b3fac",
    )

    @classmethod
    def options(cls) -> tuple[PaymentOption, ...]:
        return (
            PaymentOption(method="qris", label="QRIS", destination=cls.QRIS_IMAGE,
                instructions="Scan the configured QRIS merchant code and verify the displayed merchant before paying."),
            PaymentOption(method="usdt_bep20", label="USDT (BEP20)", destination=cls.USDT_BEP20_ADDRESS,
                instructions="Send USDT on BNB Smart Chain (BEP20) only. Verify the network and destination address before confirming."),
        )

    @classmethod
    def get(cls, method: PaymentMethod) -> PaymentOption:
        for option in cls.options():
            if option.method == method:
                return option
        raise ValueError(f"Unsupported payment method: {method}")

    @classmethod
    def checkout_instructions(cls, amount: float, currency: str, method: PaymentMethod) -> dict[str, object]:
        if amount <= 0:
            raise ValueError("amount must be positive")
        option = cls.get(method)
        return {
            "amount": float(amount),
            "currency": currency.upper(),
            "method": option.method,
            "label": option.label,
            "destination": option.destination,
            "instructions": option.instructions,
            "verification": (
                "provider/manual confirmation required for QRIS"
                if method == "qris" else "on-chain confirmation required for USDT BEP20"
            ),
        }