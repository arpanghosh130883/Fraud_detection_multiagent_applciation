"""
Agent 2: Historical Behavior Agent
Compares current transaction against the customer's established behavioral baseline.
"""

import json

from openai import OpenAI

from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Historical Behavior Agent in a real-time banking fraud detection system.

Your job is to compare the current transaction against the customer's historical profile to detect behavioral anomalies.

WHAT YOU ANALYZE:
- Amount deviation: how much the transaction differs from the customer's average
- Geographic deviation: is the destination country new for this customer?
- Timing deviation: does the time match their usual transaction hours?
- Payment method: have they used this method before?
- Frequency: is this unusual in terms of transaction frequency?

DEVIATION SCORE GUIDE:
  0.0–0.3  → Normal behavior       → consistent with profile
  0.3–0.6  → Mildly anomalous      → worth noting
  0.6–0.8  → Highly anomalous      → strong deviation
  0.8–1.0  → Extremely anomalous   → never-seen-before behavior

You MUST respond with ONLY valid JSON — no preamble, no explanation, no markdown.

Required JSON schema:
{
  "agent": "historical_behavior",
  "customer_id": "<id>",
  "deviation_score": <float 0.0–1.0>,
  "anomalies": ["<anomaly>", ...],
  "profile_match": "<NORMAL|MILDLY_ANOMALOUS|HIGHLY_ANOMALOUS|EXTREMELY_ANOMALOUS>",
  "recommendation": "<APPROVE|MONITOR|INVESTIGATE|BLOCK>",
  "message_to_device_agent": "<summary of anomalies, requesting device/location verification>",
  "analysis_summary": "<one sentence>"
}"""


class HistoricalBehaviorAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__(client, "Historical Behavior Agent", SYSTEM_PROMPT)

    def analyze(
        self,
        transaction: dict,
        customer_profile: dict,
        fraud_pattern_findings: dict,
    ) -> dict:
        message = f"""Analyze this transaction against the customer's historical profile.

TRANSACTION DATA:
{json.dumps(transaction, indent=2)}

CUSTOMER PROFILE (full history):
{json.dumps(customer_profile, indent=2)}

MESSAGE FROM FRAUD PATTERN AGENT:
{fraud_pattern_findings.get("message_to_historical_agent", "No message provided.")}

FRAUD PATTERN FINDINGS (risk score: {fraud_pattern_findings.get("risk_score", "N/A")}):
Red flags found: {fraud_pattern_findings.get("red_flags", [])}

Calculate how anomalous this transaction is relative to the customer's normal behavior."""
        return self.call_llm(message)
