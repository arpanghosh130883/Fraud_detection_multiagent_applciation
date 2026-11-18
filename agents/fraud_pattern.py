"""
Agent 1: Fraud Pattern Agent
Detects suspicious transaction patterns and calculates an initial risk score.
"""

import json

from openai import OpenAI

from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Fraud Pattern Agent in a real-time banking fraud detection system.

Your job is to analyze a transaction against known fraud patterns and produce a risk score.

FRAUD RULES YOU ENFORCE:
- HIGH-RISK COUNTRIES: Russia, North Korea, Iran, Belarus, Myanmar, Syria, Somalia, Venezuela, Cuba
- HIGH-RISK PAYMENT METHODS: cryptocurrency, anonymous wire, prepaid cards
- AMOUNT ANOMALY: >3x customer average = suspicious; >5x = high risk; >10x = critical
- UNUSUAL TIMING: Transactions between 23:00–06:00 local time are suspicious
- HIGH-RISK MERCHANT CATEGORIES: international_wire, crypto_exchange, gambling

RISK SCORE GUIDE:
  0.0–0.3  → Low risk   → APPROVE
  0.3–0.6  → Medium     → MONITOR
  0.6–0.8  → High risk  → INVESTIGATE
  0.8–1.0  → Critical   → BLOCK

You MUST respond with ONLY valid JSON — no preamble, no explanation, no markdown.

Required JSON schema:
{
  "agent": "fraud_pattern",
  "transaction_id": "<id>",
  "risk_score": <float 0.0–1.0>,
  "red_flags": ["<flag>", ...],
  "recommendation": "<APPROVE|MONITOR|INVESTIGATE|BLOCK>",
  "message_to_historical_agent": "<what you found, asking agent 2 to verify customer profile>",
  "analysis_summary": "<one sentence>"
}"""


class FraudPatternAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__(client, "Fraud Pattern Agent", SYSTEM_PROMPT)

    def analyze(self, transaction: dict, customer_profile: dict) -> dict:
        message = f"""Analyze this transaction for fraud patterns.

TRANSACTION DATA:
{json.dumps(transaction, indent=2)}

CUSTOMER PROFILE:
{json.dumps(customer_profile, indent=2)}

Identify every red flag and produce an accurate risk score."""
        return self.call_llm(message)
