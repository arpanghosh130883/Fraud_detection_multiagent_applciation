"""
Fraud Investigation Pipeline
Orchestrates the 5 agents and renders real-time investigation output.
"""

import time
from datetime import datetime

from openai import OpenAI
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from agents.coordinator import CoordinatorAgent
from agents.device_location import DeviceLocationAgent
from agents.fraud_pattern import FraudPatternAgent
from agents.historical_behavior import HistoricalBehaviorAgent
from agents.network_graph import NetworkGraphAgent
from data.sample_data import (
    CUSTOMER_PROFILES,
    DEVICE_DATABASE,
    FRAUD_NETWORKS,
)

console = Console()

DECISION_STYLES = {
    "APPROVE": ("bold green", "✅"),
    "MONITOR": ("bold yellow", "👁️ "),
    "CHALLENGE": ("bold yellow", "⚠️ "),
    "BLOCK": ("bold red", "🚫"),
}

SCORE_COLOR = lambda s: "green" if s < 0.4 else ("yellow" if s < 0.7 else "red")


def _score_bar(score: float, width: int = 20) -> str:
    filled = int(score * width)
    bar = "█" * filled + "░" * (width - filled)
    color = SCORE_COLOR(score)
    return f"[{color}]{bar}[/{color}] [{color}]{score:.2f}[/{color}]"


def _print_agent_header(agent_name: str, step: int, total: int = 5):
    console.print()
    console.print(Rule(
        f"[bold cyan]Step {step}/{total}: {agent_name}[/bold cyan]",
        style="cyan",
    ))


def _print_fraud_pattern(findings: dict):
    score = findings.get("risk_score", 0)
    color = SCORE_COLOR(score)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="bold white", width=22)
    table.add_column("Value")

    table.add_row("Risk Score", _score_bar(score))
    table.add_row("Recommendation", f"[bold {color}]{findings.get('recommendation', 'N/A')}[/bold {color}]")

    flags = findings.get("red_flags", [])
    for i, flag in enumerate(flags):
        table.add_row(f"Red Flag {i+1}" if i > 0 else "Red Flags", f"[red]⚑ {flag}[/red]")

    console.print(Panel(table, title="[bold]Fraud Pattern Agent[/bold]", border_style=color))

    msg = findings.get("message_to_historical_agent", "")
    if msg:
        console.print(Panel(
            f"[italic]{msg}[/italic]",
            title="[dim]→ Message to Historical Behavior Agent[/dim]",
            border_style="dim",
        ))


def _print_behavior(findings: dict):
    score = findings.get("deviation_score", 0)
    color = SCORE_COLOR(score)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="bold white", width=22)
    table.add_column("Value")

    table.add_row("Deviation Score", _score_bar(score))
    table.add_row("Profile Match", f"[bold {color}]{findings.get('profile_match', 'N/A')}[/bold {color}]")
    table.add_row("Recommendation", f"[bold {color}]{findings.get('recommendation', 'N/A')}[/bold {color}]")

    anomalies = findings.get("anomalies", [])
    for i, a in enumerate(anomalies):
        table.add_row(f"Anomaly {i+1}" if i > 0 else "Anomalies", f"[yellow]⚠ {a}[/yellow]")

    console.print(Panel(table, title="[bold]Historical Behavior Agent[/bold]", border_style=color))

    msg = findings.get("message_to_device_agent", "")
    if msg:
        console.print(Panel(
            f"[italic]{msg}[/italic]",
            title="[dim]→ Message to Device & Location Agent[/dim]",
            border_style="dim",
        ))


def _print_device(findings: dict):
    score = findings.get("device_fraud_score", 0)
    color = SCORE_COLOR(score)
    f = findings.get("findings", {})

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="bold white", width=22)
    table.add_column("Value")

    table.add_row("Device Fraud Score", _score_bar(score))
    table.add_row("Previous Device", str(f.get("previous_device", "Unknown")))
    table.add_row("Current Device", f"[red]{f.get('current_device', 'Unknown')}[/red]")
    table.add_row("Last Location", str(f.get("last_known_location", "Unknown")))
    table.add_row("Current Location", f"[red]{f.get('current_location', 'Unknown')}[/red]")

    travel = f.get("travel_verdict", "UNKNOWN")
    travel_color = "green" if travel == "POSSIBLE" else ("yellow" if travel == "SUSPICIOUS" else "red")
    table.add_row("Travel Verdict", f"[bold {travel_color}]{travel}[/bold {travel_color}]")

    ato = findings.get("is_account_takeover", False)
    table.add_row("Account Takeover", f"[bold red]YES[/bold red]" if ato else "[bold green]NO[/bold green]")
    table.add_row("Recommendation", f"[bold {color}]{findings.get('recommendation', 'N/A')}[/bold {color}]")

    console.print(Panel(table, title="[bold]Device & Location Agent[/bold]", border_style=color))

    msg = findings.get("message_to_network_agent", "")
    if msg:
        console.print(Panel(
            f"[italic]{msg}[/italic]",
            title="[dim]→ Message to Network Graph Agent[/dim]",
            border_style="dim",
        ))


def _print_network(findings: dict):
    score = findings.get("ring_confidence", 0)
    color = SCORE_COLOR(score)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="bold white", width=22)
    table.add_column("Value")

    table.add_row("Ring Confidence", _score_bar(score))
    in_net = findings.get("is_in_fraud_network", False)
    table.add_row("In Fraud Network", f"[bold red]YES[/bold red]" if in_net else "[bold green]NO[/bold green]")
    if in_net:
        table.add_row("Network Name", f"[red]{findings.get('fraud_network_name', 'Unknown')}[/red]")
    coord = findings.get("coordinated_attack", False)
    table.add_row("Coordinated Attack", f"[bold red]YES[/bold red]" if coord else "[bold green]NO[/bold green]")
    table.add_row("Recommendation", f"[bold {color}]{findings.get('recommendation', 'N/A')}[/bold {color}]")

    connections = findings.get("connections", [])
    for i, c in enumerate(connections):
        table.add_row(
            f"Connection {i+1}",
            f"[red]{c.get('account_id')}[/red] — {c.get('risk_flag', '')}",
        )

    console.print(Panel(table, title="[bold]Network Graph Agent[/bold]", border_style=color))

    msg = findings.get("message_to_coordinator", "")
    if msg:
        console.print(Panel(
            f"[italic]{msg}[/italic]",
            title="[dim]→ Message to Investigation Coordinator[/dim]",
            border_style="dim",
        ))


def _print_coordinator(findings: dict):
    decision = findings.get("decision", "UNKNOWN")
    style, icon = DECISION_STYLES.get(decision, ("bold white", "?"))
    prob = findings.get("final_fraud_probability", 0)

    console.print()
    console.print(Rule(style="bold white"))

    # Score summary table
    scores = findings.get("combined_scores", {})
    score_table = Table(title="Combined Agent Scores", show_header=True, header_style="bold cyan")
    score_table.add_column("Agent", style="white")
    score_table.add_column("Score", justify="right")
    score_table.add_column("Bar")

    rows = [
        ("Fraud Pattern", scores.get("fraud_pattern_risk", 0)),
        ("Historical Behavior", scores.get("behavior_deviation", 0)),
        ("Device & Location", scores.get("device_fraud_score", 0)),
        ("Network Graph", scores.get("network_ring_confidence", 0)),
    ]
    for name, s in rows:
        score_table.add_row(name, f"{s:.2f}", _score_bar(s))

    wa = scores.get("weighted_average", prob)
    score_table.add_row(
        "[bold]WEIGHTED AVERAGE[/bold]",
        f"[bold]{wa:.2f}[/bold]",
        _score_bar(wa),
    )

    console.print(score_table)
    console.print()

    # Final decision panel
    decision_text = Text()
    decision_text.append(f"\n  {icon} FINAL DECISION: ", style="bold white")
    decision_text.append(decision, style=style)
    decision_text.append(f"\n  Fraud Probability: ", style="white")
    decision_text.append(f"{prob:.0%}", style=style)
    decision_text.append(f"\n  Confidence: ", style="white")
    decision_text.append(findings.get("confidence", "N/A"), style=style)
    decision_text.append(f"\n\n  Reasoning:\n  ", style="white")
    decision_text.append(findings.get("reasoning", ""), style="italic")
    decision_text.append("\n")

    console.print(Panel(
        decision_text,
        title=f"[{style}] Investigation Coordinator — FINAL VERDICT [/{style}]",
        border_style=style,
    ))

    # Actions
    actions = findings.get("actions", [])
    if actions:
        action_table = Table(show_header=False, box=None, padding=(0, 1))
        action_table.add_column("", width=2)
        action_table.add_column("Action")
        for action in actions:
            action_table.add_row("→", action)
        console.print(Panel(action_table, title="[bold]Triggered Actions[/bold]", border_style="yellow"))

    ms = findings.get("investigation_time_ms", 0)
    console.print(f"\n[dim]Investigation completed in {ms}ms[/dim]")


class FraudInvestigationPipeline:
    def __init__(self):
        self.client = OpenAI()
        self.fraud_pattern_agent = FraudPatternAgent(self.client)
        self.historical_behavior_agent = HistoricalBehaviorAgent(self.client)
        self.device_location_agent = DeviceLocationAgent(self.client)
        self.network_graph_agent = NetworkGraphAgent(self.client)
        self.coordinator_agent = CoordinatorAgent(self.client)

    def investigate(self, transaction: dict) -> dict:
        customer_id = transaction.get("customer_id", "UNKNOWN")
        customer_profile = CUSTOMER_PROFILES.get(customer_id, {})
        txn_id = transaction.get("transaction_id", "UNKNOWN")

        console.print()
        console.print(Panel(
            f"[bold white]Transaction ID:[/bold white] {txn_id}\n"
            f"[bold white]Customer:[/bold white] {customer_id}"
            + (f" — {customer_profile.get('name', '')}" if customer_profile else "") + "\n"
            f"[bold white]Amount:[/bold white] [bold yellow]${transaction.get('amount_usd', 0):,}[/bold yellow]\n"
            f"[bold white]Destination:[/bold white] {transaction.get('destination_country', 'N/A')}\n"
            f"[bold white]Method:[/bold white] {transaction.get('payment_method', 'N/A')}\n"
            f"[bold white]Time:[/bold white] {transaction.get('timestamp', 'N/A')}\n"
            f"[bold white]Current Location:[/bold white] {transaction.get('current_location', 'N/A')}\n"
            f"[bold white]Current Device:[/bold white] {transaction.get('current_device', 'N/A')}",
            title="[bold red]⚡ TRANSACTION FLAGGED FOR INVESTIGATION[/bold red]",
            border_style="red",
        ))

        start_time = time.time()

        # ── Agent 1: Fraud Pattern ─────────────────────────────────────────
        _print_agent_header("Fraud Pattern Agent", 1)
        console.print("[dim]Analyzing transaction patterns...[/dim]")
        fp_findings = self.fraud_pattern_agent.analyze(transaction, customer_profile)
        _print_fraud_pattern(fp_findings)

        # ── Agent 2: Historical Behavior ───────────────────────────────────
        _print_agent_header("Historical Behavior Agent", 2)
        console.print("[dim]Comparing against customer behavioral baseline...[/dim]")
        hb_findings = self.historical_behavior_agent.analyze(
            transaction, customer_profile, fp_findings
        )
        _print_behavior(hb_findings)

        # ── Agent 3: Device & Location ─────────────────────────────────────
        _print_agent_header("Device & Location Agent", 3)
        console.print("[dim]Verifying device and checking for impossible travel...[/dim]")
        dl_findings = self.device_location_agent.analyze(
            transaction, customer_profile, DEVICE_DATABASE, hb_findings
        )
        _print_device(dl_findings)

        # ── Agent 4: Network Graph ─────────────────────────────────────────
        _print_agent_header("Network Graph Agent", 4)
        console.print("[dim]Scanning fraud network connections...[/dim]")
        ng_findings = self.network_graph_agent.analyze(
            transaction,
            FRAUD_NETWORKS,
            dl_findings,
            {"fraud_pattern": fp_findings, "historical_behavior": hb_findings},
        )
        _print_network(ng_findings)

        # ── Agent 5: Investigation Coordinator ─────────────────────────────
        _print_agent_header("Investigation Coordinator — Final Decision", 5)
        console.print("[dim]Synthesizing all agent findings...[/dim]")
        coord_findings = self.coordinator_agent.decide(
            transaction, fp_findings, hb_findings, dl_findings, ng_findings
        )
        elapsed_ms = int((time.time() - start_time) * 1000)
        # Override with real elapsed time
        coord_findings["investigation_time_ms"] = elapsed_ms
        _print_coordinator(coord_findings)

        return {
            "transaction": transaction,
            "fraud_pattern": fp_findings,
            "historical_behavior": hb_findings,
            "device_location": dl_findings,
            "network_graph": ng_findings,
            "coordinator": coord_findings,
            "decision": coord_findings.get("decision"),
            "fraud_probability": coord_findings.get("final_fraud_probability"),
            "elapsed_ms": elapsed_ms,
        }
