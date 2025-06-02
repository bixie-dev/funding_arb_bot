from exchanges.hyperliquid import Hyperliquid
from exchanges.bybit import Bybit
from exchanges.dydx import Dydx
from exchanges.gmx import Gmx
from exchanges.drift import Drift
from exchanges.derive import Derive
from exchanges.lighter import Lighter
from exchanges.mexc import Mexc

def get_exchange(name):
    name = name.lower()
    if name == "hyperliquid":
        return Hyperliquid()
    elif name == "bybit":
        return Bybit()
    elif name == "dydx":
        return Dydx()
    elif name == "gmx":
        return Gmx()
    elif name == "drift":
        return Drift()
    elif name == "derive":
        return Derive()
    elif name == "lighter":
        return Lighter()
    elif name == "mexc":
        return Mexc()
    else:
        raise ValueError(f"Exchange '{name}' is not supported.")
