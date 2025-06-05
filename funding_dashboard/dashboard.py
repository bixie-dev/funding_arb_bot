import os

# DEBUG_MODE = os.getenv("DEBUG_MODE", "0") == "0"

# if DEBUG_MODE:
# from modules.data_feeder import fetch_funding_data
#     print("📊 Using mock funding data (data_feeder)")
# else:
from modules.real_feeder import fetch_funding_data
    # print("📡 Using real-time funding data (real_feeder)")

def fetch_realtime_funding_data():
    funding_data = fetch_funding_data()
    return funding_data