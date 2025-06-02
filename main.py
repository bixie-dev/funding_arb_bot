import argparse
import os

def run_terminal_ui():
    os.system("python -m interface.terminal_ui")

def run_web_dashboard():
    os.system("python -m web_dashboard.app")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Funding Arbitrage Bot")
    parser.add_argument("--mode", choices=["terminal", "web"], default="terminal", help="UI mode")

    args = parser.parse_args()

    if args.mode == "terminal":
        run_terminal_ui()
    elif args.mode == "web":
        run_web_dashboard()
