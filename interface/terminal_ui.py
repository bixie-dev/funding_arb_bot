
import asyncio
from modules.real_feeder import fetch_funding_data

def print_funding_update(data):
    print(f"[{data['exchange'].upper()}] {data['coin']}: Funding {data['funding_rate']} | Spread {data['spread']}")

async def main():
    feeder = fetch_funding_data(print_funding_update)
    await feeder.start()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
