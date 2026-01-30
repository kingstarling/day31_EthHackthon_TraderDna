
import pandas as pd
import sys
import os
from data.processor import DataProcessor
from analysis.behavior_tags import generate_behavior_tags

# Mock Data
print("Testing Analysis Modules...")
processor = DataProcessor()

# 1. Test One Token Pony
print("\n--- Test 1: One Token Pony ---")
trades_pony = pd.DataFrame([
    {"token_symbol": "TOKEN_A", "realized_pnl": 10000},
    {"token_symbol": "TOKEN_B", "realized_pnl": 100},
    {"token_symbol": "TOKEN_C", "realized_pnl": -50},
])
conc = processor.calculate_token_concentration(trades_pony)
print(f"Concentration Stats: {conc}")

analysis_results = {
    "top_token_contribution": conc["top_token_contribution"],
    "profit_factor": 1.0
}
tags = generate_behavior_tags(analysis_results)
print(f"Tags: {tags}")
pony_tag_found = any(t[1] == "单币战士" for t in tags)
print(f"Found 'One Token Pony' tag: {pony_tag_found}")

# 2. Test Gambler vs Sniper (High PF)
print("\n--- Test 2: Gambler vs Sniper ---")
analysis_results_sniper = {
    "trade_frequency": 20,       # High Freq
    "win_rate": 0.3,             # Low Win Rate
    "profit_factor": 2.5,        # High Profit Factor!
    "top_token_contribution": 0.1
}
tags = generate_behavior_tags(analysis_results_sniper)
print(f"Sniper Scenario Tags: {tags}")

gambler_tag_found = any(t[1] == "高频赌徒" for t in tags)
print(f"Is 'Gambler' (Should be False): {gambler_tag_found}")

analysis_results_gambler = {
    "trade_frequency": 20,
    "win_rate": 0.3,
    "profit_factor": 0.5,        # Low Profit Factor
    "top_token_contribution": 0.1
}
tags = generate_behavior_tags(analysis_results_gambler)
print(f"Gambler Scenario Tags: {tags}")
is_gambler = any(t[1] == "高频赌徒" for t in tags)
print(f"Is 'Gambler' (Should be True): {is_gambler}")

print("\nTests Completed.")
