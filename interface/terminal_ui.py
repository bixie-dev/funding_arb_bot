
import asyncio
from modules.real_feeder import RealFundingFeeder

def print_funding_update(data):
    print(f"[{data['exchange'].upper()}] {data['coin']}: Funding {data['funding_rate']} | Spread {data['spread']}")

async def main():
    feeder = RealFundingFeeder(print_funding_update)
    await feeder.start()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
