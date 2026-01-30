
import sys
import os
import pandas as pd
from data.fetcher import DuneFetcher

# Setup
fetcher = DuneFetcher()
wallet = "0xab5801a7d398351b8be11c439e05c5b3259aec9b" # Using the address from the screenshot

print(f"Testing Dune API for wallet: {wallet}")
print(f"API Key present: {bool(fetcher.api_key)}")

try:
    df = fetcher.get_wallet_trades(wallet)
    print("Success!")
    print(df.head())
except Exception as e:
    print(f"Caught exception in main: {e}")
