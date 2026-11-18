"""
Agent 3: Device & Location Agent
Verifies device authenticity and detects impossible travel scenarios.
"""

import json

from openai import OpenAI

from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Device & Location Agent in a real-time banking fraud detection system.

Your job is to verify that the device and location of the current transaction are consistent with the customer's known devices and recent locations.

WHAT YOU CHECK:
- Device match: is the current device one of the customer's registered devices?
- Location match: does the current location match the customer's normal location?
- Impossible travel: compare last known location + time vs current location + time
  - San Francisco → Moscow minimum flight time: ~11 hours
  - New York → London minimum: ~7 hours
  - Any cross-continental move in <4 hours = IMPOSSIBLE
- IP geolocation: does the IP address match the stated location?
- Device fingerprint: is this a known, trusted device?

DEVICE FRAUD SCORE GUIDE:
  0.0–0.3  → Legitimate device/location
  0.3–0.6  → Minor inconsistency
  0.6–0.8  → Suspicious (possible account sharing)
  0.8–1.0  → Compromised — account takeover likely

You MUST respond with ONLY valid JSON — no preamble, no explanation, no markdown.

Required JSON schema:
{
  "agent": "device_location",
  "device_fraud_score": <float 0.0–1.0>,
  "device_match": <true|false>,
  "location_match": <true|false>,
  "impossible_travel_detected": <true|false>,
  "findings": {
    "previous_device": "<device name and location>",
    "current_device": "<device name and location>",
    "last_known_location": "<city, country, time>",
    "current_location": "<city, country>",
    "travel_verdict": "<POSSIBLE|SUSPICIOUS|IMPOSSIBLE>"
  },
  "is_account_takeover": <true|false>,
  "recommendation": "<APPROVE|MONITOR|INVESTIGATE|BLOCK>",
  "message_to_network_agent": "<findings, asking agent 4 to check fraud network connections>",
  "analysis_summary": "<one sentence>"
}"""


class DeviceLocationAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__(client, "Device & Location Agent", SYSTEM_PROMPT)

    def analyze(
        self,
        transaction: dict,
        customer_profile: dict,
        device_database: dict,
        behavior_findings: dict,
    ) -> dict:
        customer_device_info = device_database.get(transaction.get("customer_id"), {})
        message = f"""Verify the device and location for this transaction.

TRANSACTION DATA:
{json.dumps(transaction, indent=2)}

CUSTOMER'S REGISTERED DEVICE:
{json.dumps(customer_device_info, indent=2)}

CUSTOMER PROFILE (normal location/device):
Normal location: {customer_profile.get("normal_location")}
Known devices: {customer_profile.get("known_devices")}

MESSAGE FROM HISTORICAL BEHAVIOR AGENT:
{behavior_findings.get("message_to_device_agent", "No message provided.")}

BEHAVIOR FINDINGS (deviation score: {behavior_findings.get("deviation_score", "N/A")}):
Anomalies detected: {behavior_findings.get("anomalies", [])}

Verify device authenticity and check for impossible travel."""
        return self.call_llm(message)
