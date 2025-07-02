## 💸 Funding Arb Bot

This bot helps detect and optionally auto-execute funding or price arbitrage opportunities across decentralized and exchanges.


## 🎯 Project Goal

- Execute funding arbitrage strategies across exchanges.
- Provide a simple **terminal interface** to:
  - Open/close positions using limit orders,
  - Select coin, leverage, size, and exchange,
  - View funding rate data and current positions,
  - Trigger a “nuke” command to close all positions instantly.


## ⚙️ Features

✅ **Open & Close Positions**
- Limit orders supported.
- Manual selection of coin, size, leverage, and exchange.

✅ **Live Position Tracking**
- View open positions across exchanges.
- Show PnL, price spread, and accumulated funding.

✅ **Nuke Command**
- Close all open positions across all connected exchanges with a single command.

✅ **Funding Dashboard**
- Displays current funding rates and spreads (uses prebuilt dashboard logic).

✅ **Balance Check**
- View wallet balances on connected exchanges.

✅ **Logging**
- Logs every transaction for full audit and debugging.

✅ **Code Documentation**
- Code is well-commented and beginner-friendly for learning purposes.


## 🔄 Supported Exchanges

-Hyperliquid
-Bybit
-Dydx
-Drift
-GMX
-Derive
-Lighter
-Gate.io 

## 📁 Project Structure

funding_arb_bot/
├── main.py                  # CLI entry point
├── config/                  # API keys and settings
├── exchanges/               # Per-exchange wrappers
├── commands/                # CLI commands: trade, nuke, positions, etc.
├── funding_dashboard/       # Dashboard logic
├── utils/                   # Helpers, logger, config loader
├── logs/                    # Log output
├── tests/                   # Unit tests
└── README.md
