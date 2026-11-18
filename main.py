"""
Real-Time Fraud Detection & Investigation System
Multi-Agent AI System using OpenAI GPT-4o-mini

Usage:
    python main.py                 # Interactive menu
    python main.py --demo 1        # Run demo scenario 1 (clear fraud)
    python main.py --demo 2        # Run demo scenario 2 (legitimate)
    python main.py --demo 3        # Run demo scenario 3 (edge case)
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from data.sample_data import CUSTOMER_PROFILES, SAMPLE_TRANSACTIONS
from pipeline import FraudInvestigationPipeline

console = Console()


def check_api_key():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key or key == " ":
        console.print(Panel(
            "[bold red]OPENAI_API_KEY not set or is empty.[/bold red]\n\n"
            "Edit [bold].env[/bold] in this directory and set your key:\n"
            "  [bold]OPENAI_API_KEY = \"sk-...\"[/bold]\n\n"
            "Get your key at: https://platform.openai.com/api-keys",
            title="Missing API Key",
            border_style="red",
        ))
        sys.exit(1)


def print_banner():
    console.print(Panel(
        "[bold red]FRAUD DETECTION & REAL-TIME INVESTIGATION[/bold red]\n"
        "[white]Multi-Agent AI System  |  5 Specialized Agents  |  Powered by OpenAI GPT-4o-mini[/white]\n\n"
        "[dim]Agents:[/dim]\n"
        "  [cyan]1.[/cyan] Fraud Pattern Agent       — detects suspicious transaction patterns\n"
        "  [cyan]2.[/cyan] Historical Behavior Agent — compares against customer baseline\n"
        "  [cyan]3.[/cyan] Device & Location Agent   — verifies device and checks travel\n"
        "  [cyan]4.[/cyan] Network Graph Agent       — detects fraud rings & connections\n"
        "  [cyan]5.[/cyan] Investigation Coordinator — synthesizes findings, makes decision",
        border_style="red",
    ))


def show_demo_menu() -> int:
    table = Table(title="Available Demo Scenarios", show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold", width=4)
    table.add_column("Scenario", width=42)
    table.add_column("Description")

    for i, s in enumerate(SAMPLE_TRANSACTIONS, 1):
        table.add_row(str(i), s["name"], s["description"])
    table.add_row("4", "Custom Transaction", "Enter your own transaction details")
    table.add_row("0", "Exit", "Quit the program")

    console.print(table)
    choice = Prompt.ask(
        "\nChoose a scenario",
        choices=["0", "1", "2", "3", "4"],
        default="1",
    )
    return int(choice)


def build_custom_transaction() -> dict:
    console.print("\n[bold cyan]Enter custom transaction details[/bold cyan]")
    console.print("[dim]Press Enter to use the default value shown in brackets.[/dim]\n")

    customer_id = Prompt.ask("Customer ID", default="CUST_789")
    profile = CUSTOMER_PROFILES.get(customer_id)
    if profile:
        console.print(f"[dim]Found customer: {profile['name']} (avg txn: ${profile['avg_transaction_usd']})[/dim]")
    else:
        console.print(f"[dim]No profile found for {customer_id} — agents will note missing history.[/dim]")

    amount = Prompt.ask("Amount (USD)", default="5000")
    destination_country = Prompt.ask("Destination country", default="Russia")
    payment_method = Prompt.ask(
        "Payment method",
        choices=["debit_card", "credit_card", "bank_transfer", "cryptocurrency", "wire"],
        default="cryptocurrency",
    )
    timestamp = Prompt.ask("Timestamp (ISO 8601)", default="2024-11-17T02:00:00Z")
    current_device = Prompt.ask("Current device", default="Unknown Android")
    current_location = Prompt.ask("Current location", default="Moscow, Russia")
    current_ip = Prompt.ask("Current IP address", default="195.206.107.123")

    return {
        "transaction_id": f"TXN_CUSTOM_{int(__import__('time').time())}",
        "customer_id": customer_id,
        "amount_usd": int(amount),
        "currency": "USD",
        "destination_country": destination_country,
        "destination_account": f"{destination_country.upper()[:2]}_ACC_CUSTOM",
        "payment_method": payment_method,
        "timestamp": timestamp,
        "current_device": current_device,
        "current_device_id": "CUSTOM_DEVICE",
        "current_ip": current_ip,
        "current_location": current_location,
        "merchant_category": "international_wire" if destination_country.lower() not in ("usa", "us", "united states") else "domestic",
    }


def run_investigation(transaction: dict, interactive: bool = True):
    pipeline = FraudInvestigationPipeline()
    result = pipeline.investigate(transaction)

    if interactive:
        console.print()
        save = Prompt.ask(
            "Save full JSON report to file?",
            choices=["y", "n"],
            default="n",
        )
        if save == "y":
            filename = f"report_{transaction.get('transaction_id', 'unknown')}.json"
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)
            console.print(f"[green]Report saved to {filename}[/green]")

    return result


def main():
    parser = argparse.ArgumentParser(description="Fraud Detection Multi-Agent System")
    parser.add_argument("--demo", type=int, choices=[1, 2, 3], help="Run a specific demo scenario directly")
    args = parser.parse_args()

    check_api_key()
    print_banner()

    if args.demo:
        txn_data = SAMPLE_TRANSACTIONS[args.demo - 1]
        console.print(f"\n[bold]Running demo: {txn_data['name']}[/bold]")
        run_investigation(txn_data["transaction"], interactive=False)
        return

    while True:
        choice = show_demo_menu()

        if choice == 0:
            console.print("[dim]Goodbye.[/dim]")
            break
        elif choice == 4:
            txn = build_custom_transaction()
            run_investigation(txn)
        else:
            txn_data = SAMPLE_TRANSACTIONS[choice - 1]
            console.print(f"\n[bold]Running: {txn_data['name']}[/bold]")
            run_investigation(txn_data["transaction"])

        console.print()
        again = Prompt.ask("Run another investigation?", choices=["y", "n"], default="y")
        if again == "n":
            console.print("[dim]Goodbye.[/dim]")
            break


if __name__ == "__main__":
    main()
