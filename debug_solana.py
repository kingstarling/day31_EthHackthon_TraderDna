
from data.fetcher import DuneFetcher
import pandas as pd

print("Testing Solana Fetcher...")
try:
    fetcher = DuneFetcher()
    
    # Test Solana Simulation
    wallet = "So11111111111111111111111111111111111111112"
    print(f"Fetching trades for {wallet} on Solana...")
    
    df = fetcher.get_wallet_trades(wallet, chain="Solana")
    
    if not df.empty:
        print(f"Success! Got {len(df)} trades.")
        print("Sample data:")
        print(df[["token_symbol", "amount_usd", "tx_hash"]].head(3))
        
        # Check if symbols look like Solana
        symbols = df["token_symbol"].unique()
        print(f"Token symbols found: {symbols}")
        if "SOL" in symbols or "BONK" in symbols:
            print("✅ Solana tokens confirmed.")
        else:
            print("❌ Warning: Solana tokens not found (Simulation logic assumption failed?)")
            
        # Check tx hash format
        tx_hash = df.iloc[0]["tx_hash"]
        print(f"Sample Tx Hash: {tx_hash}")
        if not tx_hash.startswith("0x"):
            print("✅ Tx Hash format looks correct (Not 0x).")
        else:
            print(f"❌ Tx Hash starts with 0x: {tx_hash}")
            
    else:
        print("❌ Error: Empty DataFrame returned.")

except Exception as e:
    print(f"❌ Critical Error: {e}")
    import traceback
    traceback.print_exc()

print("\n(Note: This uses simulation because config.py has query_id=0 for Solana)")
