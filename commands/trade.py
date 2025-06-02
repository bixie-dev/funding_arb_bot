from commands.funding import detect_arbitrage_opportunities
from exchanges.exchange_factory import get_exchange
from utils.logger import setup_logger
import time

logger = setup_logger()

def execute_real_trade(opp):
    try:
        ex1 = get_exchange(opp["exchange_1"])
        ex2 = get_exchange(opp["exchange_2"])

        logger.info(f"EXECUTING TRADE:")
        logger.info(f"  Long on {opp['exchange_1']} at ${opp['price_1']} (Funding: {opp['funding_rate_1']})")
        logger.info(f"  Short on {opp['exchange_2']} at ${opp['price_2']} (Funding: {opp['funding_rate_2']})")

        id1 = ex1.open_position("ETH", size=100, leverage=5)
        id2 = ex2.open_position("ETH", size=100, leverage=5)

        logger.info(f"  Opened positions: {id1} and {id2}")
    except Exception as e:
        logger.error(f"Trade failed: {str(e)}")

def auto_trade_loop(interval=5):
    logger.info("Auto-trading started.")
    while True:
        opportunities = detect_arbitrage_opportunities()
        if opportunities:
            best = opportunities[0]
            execute_real_trade(best)
        else:
            logger.info("No profitable arbitrage opportunities found.")
        time.sleep(interval)

if __name__ == "__main__":
    try:
        auto_trade_loop()
    except KeyboardInterrupt:
        logger.info("Auto-trading stopped by user.")