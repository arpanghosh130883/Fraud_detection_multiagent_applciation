"""
Agent 5: Investigation Coordinator Agent
Synthesizes findings from all 4 agents and makes the final fraud decision.
"""

import json

from openai import OpenAI

from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Investigation Coordinator Agent — the final decision-maker in a real-time banking fraud detection system.

You receive findings from 4 specialist agents and must synthesize them into a single authoritative decision.

DECISION FRAMEWORK:
- Combine all agent scores using weighted average:
  Fraud Pattern (25%) + Historical Behavior (25%) + Device/Location (30%) + Network Graph (20%)
- If ANY agent recommends BLOCK with score > 0.9, you should BLOCK regardless of others
- If 3+ agents recommend INVESTIGATE, the final decision is at minimum INVESTIGATE
- Final fraud probability = weighted average of all scores

AVAILABLE ACTIONS:
- APPROVE: Transaction is legitimate, allow immediately
- MONITOR: Allow but flag for 24-hour monitoring
- CHALLENGE: Require customer to verify identity (SMS code, call back)
- BLOCK: Freeze transaction immediately and alert customer

ESCALATION ACTIONS (for BLOCK decisions):
- "ALERT: Send SMS to customer's registered phone"
- "AUTH: Trigger 2FA re-authentication"
- "FLAG: Mark account for manual fraud team review"
- "FREEZE: Temporarily freeze account"
- "REPORT: File internal fraud report"
- "ESCALATE: Report fraud ring to authorities" (only if ring detected)

You MUST respond with ONLY valid JSON — no preamble, no explanation, no markdown.

Required JSON schema:
{
  "agent": "coordinator",
  "final_fraud_probability": <float 0.0–1.0>,
  "decision": "<APPROVE|MONITOR|CHALLENGE|BLOCK>",
  "confidence": "<LOW|MEDIUM|HIGH|VERY_HIGH>",
  "combined_scores": {
    "fraud_pattern_risk": <float>,
    "behavior_deviation": <float>,
    "device_fraud_score": <float>,
    "network_ring_confidence": <float>,
    "weighted_average": <float>
  },
  "reasoning": "<2-3 sentence explanation of why this decision was made>",
  "actions": ["<action1>", "<action2>", ...],
  "message_to_all_agents": "<broadcast message back to all agents with final outcome>",
  "investigation_time_ms": <integer — realistic ms for the full investigation>,
  "analyst_notes": "<any important notes for the human fraud analyst>"
}"""


class CoordinatorAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__(client, "Investigation Coordinator", SYSTEM_PROMPT)

    def decide(
        self,
        transaction: dict,
        fraud_pattern_findings: dict,
        behavior_findings: dict,
        device_findings: dict,
        network_findings: dict,
    ) -> dict:
        message = f"""Synthesize all agent findings and make the final fraud decision.

TRANSACTION UNDER INVESTIGATION:
{json.dumps(transaction, indent=2)}

─── AGENT FINDINGS ──────────────────────────────────

FRAUD PATTERN AGENT:
  Risk score: {fraud_pattern_findings.get("risk_score", "N/A")}
  Red flags: {fraud_pattern_findings.get("red_flags", [])}
  Recommendation: {fraud_pattern_findings.get("recommendation", "N/A")}

HISTORICAL BEHAVIOR AGENT:
  Deviation score: {behavior_findings.get("deviation_score", "N/A")}
  Anomalies: {behavior_findings.get("anomalies", [])}
  Profile match: {behavior_findings.get("profile_match", "N/A")}
  Recommendation: {behavior_findings.get("recommendation", "N/A")}

DEVICE & LOCATION AGENT:
  Device fraud score: {device_findings.get("device_fraud_score", "N/A")}
  Impossible travel: {device_findings.get("impossible_travel_detected", False)}
  Account takeover: {device_findings.get("is_account_takeover", False)}
  Findings: {device_findings.get("findings", {})}
  Recommendation: {device_findings.get("recommendation", "N/A")}

NETWORK GRAPH AGENT:
  Ring confidence: {network_findings.get("ring_confidence", "N/A")}
  In fraud network: {network_findings.get("is_in_fraud_network", False)}
  Network name: {network_findings.get("fraud_network_name", "None")}
  Coordinated attack: {network_findings.get("coordinated_attack", False)}
  Message: {network_findings.get("message_to_coordinator", "No message.")}
  Recommendation: {network_findings.get("recommendation", "N/A")}

─────────────────────────────────────────────────────

Make the final decision. Be decisive and thorough."""
        return self.call_llm(message)
