import time
import threading
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from commands.funding import detect_arbitrage_opportunities

auto_trade_enabled = False
console = Console()

def render_table(opportunities):
    table = Table(title="Funding Arbitrage Opportunities", show_lines=True)
    table.add_column("Symbol", justify="left", style="cyan", no_wrap=True)
    table.add_column("Hyperliquid", justify="left", style="magenta")
    table.add_column("Bybit", justify="center", style="yellow")
    table.add_column("Dydx", justify="center", style="green")
    table.add_column("Drift", justify="center", style="bold")
    table.add_column("GMX", justify="center", style="bold")
    table.add_column("Derive", justify="center", style="bold")
    table.add_column("Lighter", justify="center", style="bold")
    table.add_column("Mexc", justify="center", style="bold")

    for opp in opportunities:
        # status = "[green]PROFITABLE[/green]" if opp["price_diff"] > 1 or opp["funding_diff"] > 0.01 else "[red]SKIP[/red]"
        table.add_row(
            f"{opp['coin']}",
            f"{opp['price1']}",
            f"{opp['price2']}",
            f"{opp['price3']}",
            f"{opp['coin']}",
            f"{opp['coin']}",
            f"{opp['coin']}",
            f"{opp['coin']}",
            f"{opp['coin']}",
        )
    return table

def toggle_auto_trade():
    global auto_trade_enabled
    auto_trade_enabled = not auto_trade_enabled
    status = "ENABLED" if auto_trade_enabled else "DISABLED"
    console.log(f"[bold yellow]Auto-trading is now {status}[/]")

def start_dashboard():
    def update():
        with Live(console=console, refresh_per_second=0.5) as live:
            while True:
                opportunities = detect_arbitrage_opportunities()
                live.update(Panel(render_table(opportunities)))
                time.sleep(5)

    thread = threading.Thread(target=update, daemon=True)
    thread.start()

    while True:
        key = console.input("[bold blue]Press [T] to toggle auto-trade, [Q] to quit: ").strip().lower()
        if key == "t":
            toggle_auto_trade()
        elif key == "q":
            console.print("[bold red]Exiting dashboard...[/]")
            break

if __name__ == "__main__":
    try:
        start_dashboard()
    except KeyboardInterrupt:
        console.print("[bold red]Dashboard interrupted by user[/]")