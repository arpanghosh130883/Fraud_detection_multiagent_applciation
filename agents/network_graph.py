"""
Agent 4: Network Graph Agent
Analyzes relationships between accounts to detect fraud rings and coordinated attacks.
"""

import json

from openai import OpenAI

from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Network Graph Agent in a real-time banking fraud detection system.

Your job is to analyze the customer's connections to other accounts and known fraud networks to detect coordinated fraud attacks.

WHAT YOU ANALYZE:
- Is the customer's account in any known fraud ring?
- Are there other accounts in the same network making similar suspicious transactions today?
- Has money flowed between this customer and known mule accounts?
- Are there shared device fingerprints or IP addresses with fraudulent accounts?
- Does the destination account belong to known fraud recipients?

RING CONFIDENCE GUIDE:
  0.0–0.3  → No network connection detected
  0.3–0.6  → Loose association
  0.6–0.8  → Likely connected to fraud network
  0.8–1.0  → Strong fraud ring membership confirmed

You MUST respond with ONLY valid JSON — no preamble, no explanation, no markdown.

Required JSON schema:
{
  "agent": "network_graph",
  "ring_confidence": <float 0.0–1.0>,
  "is_in_fraud_network": <true|false>,
  "fraud_network_name": "<name or null>",
  "connections": [
    {
      "account_id": "<id>",
      "relationship": "<description>",
      "pattern": "<fraud pattern>",
      "risk_flag": "<flag>"
    }
  ],
  "coordinated_attack": <true|false>,
  "recommendation": "<APPROVE|MONITOR|INVESTIGATE|BLOCK>",
  "message_to_coordinator": "<full summary for the coordinator to make final decision>",
  "analysis_summary": "<one sentence>"
}"""


class NetworkGraphAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__(client, "Network Graph Agent", SYSTEM_PROMPT)

    def analyze(
        self,
        transaction: dict,
        fraud_networks: dict,
        device_findings: dict,
        all_prior_findings: dict,
    ) -> dict:
        customer_id = transaction.get("customer_id")

        # Check if customer appears in any known fraud network
        network_membership = []
        for ring_id, ring_data in fraud_networks.items():
            if customer_id in ring_data.get("members", []):
                network_membership.append({
                    "ring_id": ring_id,
                    "ring_data": ring_data,
                })

        message = f"""Analyze network connections for this transaction.

TRANSACTION DATA:
{json.dumps(transaction, indent=2)}

KNOWN FRAUD NETWORKS (database):
{json.dumps(fraud_networks, indent=2)}

CUSTOMER'S KNOWN NETWORK MEMBERSHIPS:
{json.dumps(network_membership, indent=2)}

MESSAGE FROM DEVICE & LOCATION AGENT:
{device_findings.get("message_to_network_agent", "No message provided.")}

DEVICE FINDINGS (device fraud score: {device_findings.get("device_fraud_score", "N/A")}):
Account takeover detected: {device_findings.get("is_account_takeover", False)}
Impossible travel: {device_findings.get("impossible_travel_detected", False)}

PRIOR AGENTS SUMMARY:
- Fraud Pattern risk score: {all_prior_findings.get("fraud_pattern", {}).get("risk_score", "N/A")}
- Behavior deviation score: {all_prior_findings.get("historical_behavior", {}).get("deviation_score", "N/A")}
- Device fraud score: {device_findings.get("device_fraud_score", "N/A")}

Determine if this customer is part of a coordinated fraud attack or fraud ring."""
        return self.call_llm(message)
