# Fraud Detection & Real-Time Investigation System

A **multi-agent AI system** that detects and investigates suspicious financial transactions in real time. Five specialized AI agents collaborate — each passing findings to the next — and reach a final BLOCK/APPROVE decision in seconds, before money moves.

---

## The Problem

Fraud happens in milliseconds. By the time a human reviews an alert, the money is already gone. Manual investigation is too slow, and rule-based systems produce too many false positives.

## The Solution

Five AI agents work together in a sequential investigation pipeline, each contributing a different lens:

```
Incoming Transaction
        │
        ▼
┌───────────────────┐
│  Fraud Pattern    │  ← risk score from amount, country, method, timing
│  Agent            │
└────────┬──────────┘
         │  findings + message
         ▼
┌───────────────────┐
│  Historical       │  ← deviation from customer's 3-year baseline
│  Behavior Agent   │
└────────┬──────────┘
         │  findings + message
         ▼
┌───────────────────┐
│  Device &         │  ← impossible travel, device fingerprint mismatch
│  Location Agent   │
└────────┬──────────┘
         │  findings + message
         ▼
┌───────────────────┐
│  Network Graph    │  ← fraud ring detection, mule account connections
│  Agent            │
└────────┬──────────┘
         │  all findings
         ▼
┌───────────────────┐
│  Investigation    │  ← weighted decision: APPROVE / MONITOR / BLOCK
│  Coordinator      │
└────────┬──────────┘
         │
    Block / Approve
    Transaction
```

---

## The 5 Agents

### Agent 1 — Fraud Pattern Agent
Detects suspicious transaction characteristics against known fraud rules:
- High-risk destination countries (Russia, North Korea, Iran, etc.)
- High-risk payment methods (cryptocurrency, anonymous wire)
- Amount anomaly (>3x customer average = suspicious, >10x = critical)
- Unusual transaction timing (11 PM – 6 AM)

Returns a **risk score (0.0 – 1.0)** and a list of red flags.

### Agent 2 — Historical Behavior Agent
Compares the current transaction against the customer's established profile:
- Average transaction amount over account lifetime
- Geographic destinations historically used
- Payment methods previously used
- Transaction timing patterns

Returns a **deviation score (0.0 – 1.0)** indicating how anomalous the transaction is.

### Agent 3 — Device & Location Agent
Verifies device authenticity and checks for impossible travel:
- Is the current device one of the customer's registered devices?
- Does the IP geolocation match the stated location?
- Could the customer physically travel from their last known location to the current one in the elapsed time?

Returns a **device fraud score** and an impossible travel verdict.

### Agent 4 — Network Graph Agent
Analyses connections between accounts to detect coordinated fraud:
- Is this customer in a known fraud ring?
- Are connected accounts making similar suspicious transfers today?
- Are there shared devices or IPs with flagged accounts?
- Does the destination account belong to known money mules?

Returns a **ring confidence score** and connection details.

### Agent 5 — Investigation Coordinator
Synthesises all four agents' findings into a final decision:
- Weighted average of all scores (Device/Location carries highest weight at 30%)
- Triggers appropriate actions: SMS alert, 2FA challenge, account freeze, authority report
- Broadcasts outcome back to all agents for continued monitoring

---

## Agent-to-Agent Communication

Each agent returns a structured JSON response that includes a **plain-text message addressed to the next agent**. The pipeline injects this message verbatim into the next agent's prompt, simulating real inter-agent communication:

```
Agent 1 → "Customer just tried $5K to Russia via crypto at 2AM.
            Their history shows avg $320 US-only transfers.
            Is this consistent with their profile?"

Agent 2 → "HIGHLY anomalous — no international transfers in 3 years,
            amount is 15x their average. Never transacted at 2AM.
            Please verify device and location immediately."

Agent 3 → "CRITICAL: Device changed from iPhone in California to
            unknown Android in Moscow within 2 hours — physically
            impossible. Account takeover likely. Check fraud network."

Agent 4 → "ALERT: Customer is in the Russian Wire Fraud Ring.
            Two connected accounts made similar transfers TODAY.
            This is a coordinated attack. Confidence: 87%."

Coordinator → "BLOCK — 97% fraud probability. Alerting customer,
               freezing account, reporting to authorities."
```

---

## Project Structure

```
fraud-detection-realtime-investigation/
│
├── .env                        # OPENAI_API_KEY (not committed — keep private)
├── main.py                     # CLI entry point
├── pipeline.py                 # Orchestrates agents + rich terminal UI
├── pyproject.toml              # Dependencies
├── uv.lock                     # Locked dependency versions
│
├── agents/
│   ├── base_agent.py           # OpenAI API wrapper + JSON response parser
│   ├── fraud_pattern.py        # Agent 1 — pattern risk scoring
│   ├── historical_behavior.py  # Agent 2 — behavioral baseline deviation
│   ├── device_location.py      # Agent 3 — device verification & travel check
│   ├── network_graph.py        # Agent 4 — fraud ring & connection analysis
│   └── coordinator.py          # Agent 5 — final weighted decision
│
└── data/
    └── sample_data.py          # Synthetic customer profiles, fraud networks,
                                #   device database, demo transactions
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An OpenAI API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Installation

```bash
# Clone the repository
git clone https://github.com/arpanghosh130883/Fraud_detection_multiagent_applciation.git
cd Fraud_detection_multiagent_applciation

# Install dependencies
uv sync
# or: pip install openai python-dotenv rich
```

### Configuration

Create a `.env` file in the project root:

```
OPENAI_API_KEY = "sk-..."
```

### Running

```bash
# Interactive menu (choose from 3 demo scenarios or enter a custom transaction)
python main.py

# Run a specific demo directly
python main.py --demo 1    # Clear fraud: account takeover + Russia wire transfer
python main.py --demo 2    # Legitimate: normal grocery purchase
python main.py --demo 3    # Edge case: unusual but possibly legitimate transfer
```

---

## Demo Scenarios

| # | Scenario | Expected Decision |
|---|----------|-------------------|
| 1 | $5,000 crypto transfer to Russia at 2 AM — device changed from iPhone in California to unknown Android in Moscow (2 hrs apart) — customer is in known fraud ring | **BLOCK** (97% fraud) |
| 2 | $650 grocery purchase in New York — same device, same city, matches customer's daily spending pattern | **APPROVE** |
| 3 | $800 bank transfer to Mexico — new account, no international history, but same device and location | **INVESTIGATE / CHALLENGE** |

---

## Sample Output (Demo 1)

```
⚡ TRANSACTION FLAGGED FOR INVESTIGATION
  Transaction ID : TXN_12345
  Customer       : CUST_789 — John Smith
  Amount         : $5,000
  Destination    : Russia
  Method         : cryptocurrency
  Current Device : Unknown Android
  Current Location: Moscow, Russia

── Step 1/5: Fraud Pattern Agent ──────────────────────────
  Risk Score      ████████████████████ 1.00    BLOCK
  Red Flags       ⚑ Russia (high-risk country)
                  ⚑ Cryptocurrency (high-risk method)
                  ⚑ Amount is 15x customer average
                  ⚑ Transaction at 2:00 AM

── Step 2/5: Historical Behavior Agent ────────────────────
  Deviation Score ████████████████████ 1.00    EXTREMELY_ANOMALOUS
  Anomalies       ⚠ No international transfers in 3-year history
                  ⚠ Amount 15x the average ($320)
                  ⚠ Never transacted at this hour

── Step 3/5: Device & Location Agent ──────────────────────
  Device Score    ██████████████████░░ 0.90
  Travel Verdict  IMPOSSIBLE  (California → Moscow in 2 hours)
  Account Takeover YES

── Step 4/5: Network Graph Agent ──────────────────────────
  Ring Confidence █████████████████░░░ 0.87
  Fraud Network   Russian Wire Fraud Ring
  Coordinated     YES — 2 linked accounts transferred to Russia today

── Step 5/5: Investigation Coordinator ────────────────────
  🚫 FINAL DECISION : BLOCK
  Fraud Probability : 96%
  Confidence        : VERY HIGH

  Actions →  SMS alert to customer
          →  2FA re-authentication required
          →  Account flagged for manual review
          →  Account frozen
          →  Report filed with fraud team & authorities
```

---

## How Data Flows Between Agents

```
                     ┌─ STATIC DATABASE ─────────────────────────┐
                     │  Customer profiles  (3-year history)       │
                     │  Device database    (registered devices)   │
                     │  Fraud network DB   (known fraud rings)    │
                     └───────────────────────────────────────────┘
                                        │
Transaction ──► Agent 1 ──► fp_findings ─┼──► Agent 2 ──► hb_findings ──► Agent 3
                                         │                                      │
                                         │                          dl_findings ▼
                                         └──────────────────────────────► Agent 4
                                                                               │
                                                               ng_findings ────▼
                                                                          Agent 5
                                                                    (Coordinator)
                                                                          │
                                                                   FINAL DECISION
```

Each agent receives the **raw transaction** + **its own specialist data** + **the previous agent's JSON findings and message**. By the time the Coordinator runs, it has the complete picture from all four investigators.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Model | OpenAI `gpt-4o-mini` |
| Agent Framework | Custom pipeline (no LangChain — pure OpenAI SDK) |
| Terminal UI | [Rich](https://github.com/Textualize/rich) |
| Environment | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| Package Manager | [uv](https://docs.astral.sh/uv/) |
| Python | 3.11+ |

---

## Key Design Decisions

**Why no LangChain / LlamaIndex?**
Pure OpenAI SDK keeps the code readable and educational. Each agent is a single `chat.completions.create` call — easy to understand, easy to extend.

**Why sequential (not parallel) agents?**
Each agent needs the previous agent's findings to provide richer context. The chain builds an ever-more-complete picture of the fraud.

**Why JSON responses?**
Structured JSON from each agent makes inter-agent communication reliable and machine-readable. The `base_agent.py` parser handles both bare JSON and markdown-fenced code blocks.

---

## Educational Use

This project is designed for teaching multi-agent AI system design. All customer data, transaction data, fraud networks, and device information are **entirely synthetic and fictional**.
