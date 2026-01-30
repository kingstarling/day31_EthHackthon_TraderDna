"""
TraderDNA 数据处理模块

提供交易数据清洗、持仓计算、收益归因等功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class DataProcessor:
    """
    数据处理器
    
    负责清洗原始交易数据，计算持仓和收益
    """
    
    def __init__(self):
        """初始化数据处理器"""
        pass
    
    def clean_trades(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗交易数据
        
        Args:
            trades_df: 原始交易 DataFrame
            
        Returns:
            清洗后的 DataFrame
        """
        if trades_df.empty:
            return trades_df
        
        df = trades_df.copy()
        
        # 确保时间戳是 datetime 类型
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # 移除无效交易
        df = df.dropna(subset=["token_address", "amount", "price_usd"])
        
        # 确保数值类型正确
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["price_usd"] = pd.to_numeric(df["price_usd"], errors="coerce")
        
        # 计算交易价值
        df["value_usd"] = df["amount"] * df["price_usd"]
        
        # 按时间排序
        df = df.sort_values("timestamp")
        
        return df
    
    def calculate_positions(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """
        计算持仓
        
        Args:
            trades_df: 交易 DataFrame
            
        Returns:
            持仓 DataFrame
        """
        if trades_df.empty:
            return pd.DataFrame()
        
        positions = []
        
        for token in trades_df["token_address"].unique():
            token_trades = trades_df[trades_df["token_address"] == token]
            
            # 计算买入和卖出
            buys = token_trades[token_trades["action"] == "buy"]
            sells = token_trades[token_trades["action"] == "sell"]
            
            total_bought = buys["amount"].sum()
            total_sold = sells["amount"].sum()
            current_position = total_bought - total_sold
            
            # 计算平均买入价格
            if total_bought > 0:
                avg_buy_price = buys["value_usd"].sum() / total_bought
            else:
                avg_buy_price = 0
            
            positions.append({
                "token_address": token,
                "token_symbol": token_trades["token_symbol"].iloc[0],
                "total_bought": total_bought,
                "total_sold": total_sold,
                "current_position": current_position,
                "avg_buy_price": avg_buy_price,
                "cost_basis": total_bought * avg_buy_price,
            })
        
        return pd.DataFrame(positions)
    
    def calculate_realized_pnl(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """
        计算已实现盈亏
        
        使用 FIFO 方法计算
        
        Args:
            trades_df: 交易 DataFrame
            
        Returns:
            带 PnL 的交易 DataFrame
        """
        if trades_df.empty:
            return trades_df
        
        df = trades_df.copy()
        pnl_records = []
        
        for token in df["token_address"].unique():
            token_trades = df[df["token_address"] == token].sort_values("timestamp")
            
            buy_queue = []  # FIFO 队列: [(amount, price)]
            
            for _, trade in token_trades.iterrows():
                if trade["action"] == "buy":
                    buy_queue.append((trade["amount"], trade["price_usd"]))
                elif trade["action"] == "sell":
                    sell_amount = trade["amount"]
                    sell_price = trade["price_usd"]
                    trade_pnl = 0
                    
                    while sell_amount > 0 and buy_queue:
                        buy_amount, buy_price = buy_queue[0]
                        
                        if buy_amount <= sell_amount:
                            # 用完这批买入
                            trade_pnl += buy_amount * (sell_price - buy_price)
                            sell_amount -= buy_amount
                            buy_queue.pop(0)
                        else:
                            # 部分使用这批买入
                            trade_pnl += sell_amount * (sell_price - buy_price)
                            buy_queue[0] = (buy_amount - sell_amount, buy_price)
                            sell_amount = 0
                    
                    pnl_records.append({
                        "timestamp": trade["timestamp"],
                        "token_address": token,
                        "token_symbol": trade["token_symbol"],
                        "realized_pnl": trade_pnl,
                        "tx_hash": trade.get("tx_hash", "")
                    })
        
        return pd.DataFrame(pnl_records)
    
    def calculate_daily_returns(
        self,
        pnl_df: pd.DataFrame,
        initial_capital: float = 10000
    ) -> pd.Series:
        """
        计算日收益率序列
        
        Args:
            pnl_df: PnL DataFrame
            initial_capital: 初始资本
            
        Returns:
            日收益率 Series
        """
        if pnl_df.empty:
            return pd.Series(dtype=float)
        
        # 按日汇总 PnL
        daily_pnl = pnl_df.set_index("timestamp").resample("D")["realized_pnl"].sum()
        
        # 计算累计资本
        cumulative_capital = initial_capital + daily_pnl.cumsum()
        
        # 计算日收益率
        daily_returns = cumulative_capital.pct_change().dropna()
        
        return daily_returns
    
    def calculate_trade_stats(self, trades_df: pd.DataFrame) -> Dict:
        """
        计算交易统计数据
        
        Args:
            trades_df: 交易 DataFrame
            
        Returns:
            统计数据字典
        """
        if trades_df.empty:
            return {
                "total_trades": 0,
                "buy_trades": 0,
                "sell_trades": 0,
                "unique_tokens": 0,
                "first_trade": None,
                "last_trade": None,
                "trading_days": 0,
            }
        
        return {
            "total_trades": len(trades_df),
            "buy_trades": len(trades_df[trades_df["action"] == "buy"]),
            "sell_trades": len(trades_df[trades_df["action"] == "sell"]),
            "unique_tokens": trades_df["token_address"].nunique(),
            "first_trade": trades_df["timestamp"].min(),
            "last_trade": trades_df["timestamp"].max(),
            "trading_days": trades_df["timestamp"].dt.date.nunique(),
        }
    
    def calculate_hold_times(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """
        计算每笔交易的持仓时间
        
        Args:
            trades_df: 交易 DataFrame
            
        Returns:
            持仓时间 DataFrame
        """
        if trades_df.empty:
            return pd.DataFrame()
        
        hold_times = []
        
        for token in trades_df["token_address"].unique():
            token_trades = trades_df[trades_df["token_address"] == token].sort_values("timestamp")
            
            buy_times = []
            
            for _, trade in token_trades.iterrows():
                if trade["action"] == "buy":
                    buy_times.append((trade["timestamp"], trade["amount"]))
                elif trade["action"] == "sell" and buy_times:
                    sell_time = trade["timestamp"]
                    sell_amount = trade["amount"]
                    
                    while sell_amount > 0 and buy_times:
                        buy_time, buy_amount = buy_times[0]
                        
                        if buy_amount <= sell_amount:
                            hold_hours = (sell_time - buy_time).total_seconds() / 3600
                            hold_times.append({
                                "token_address": token,
                                "token_symbol": trade["token_symbol"],
                                "hold_hours": hold_hours,
                                "amount": buy_amount,
                            })
                            sell_amount -= buy_amount
                            buy_times.pop(0)
                        else:
                            hold_hours = (sell_time - buy_time).total_seconds() / 3600
                            hold_times.append({
                                "token_address": token,
                                "token_symbol": trade["token_symbol"],
                                "hold_hours": hold_hours,
                                "amount": sell_amount,
                            })
                            buy_times[0] = (buy_time, buy_amount - sell_amount)
                            sell_amount = 0
        
        return pd.DataFrame(hold_times)
    
    def get_time_window_data(
        self,
        df: pd.DataFrame,
        days: int,
        timestamp_col: str = "timestamp"
    ) -> pd.DataFrame:
        """
        获取指定时间窗口的数据
        
        Args:
            df: 数据 DataFrame
            days: 天数
            timestamp_col: 时间戳列名
            
        Returns:
            筛选后的 DataFrame
        """
        if df.empty:
            return df
        
        cutoff = datetime.now() - timedelta(days=days)
        return df[df[timestamp_col] >= cutoff]
    
    def calculate_token_concentration(self, trades_df: pd.DataFrame) -> Dict[str, float]:
        """
        计算代币盈亏集中度
        
        Args:
            trades_df: 交易 DataFrame (需包含 realized_pnl)
            
        Returns:
            包含集中度指标的字典
        """
        if trades_df.empty or "realized_pnl" not in trades_df.columns:
            return {
                "top_trade_contribution": 0.0,
                "top_token_contribution": 0.0,
                "hhi_index": 0.0,
                "profitable_tokens_count": 0,
            }
        
        # 1. 单笔最大贡献
        total_positive_pnl = trades_df[trades_df["realized_pnl"] > 0]["realized_pnl"].sum()
        if total_positive_pnl > 0:
            max_single_trade_pnl = trades_df["realized_pnl"].max()
            top_trade_contribution = max_single_trade_pnl / total_positive_pnl
        else:
            top_trade_contribution = 0.0
            
        # 2. 代币集中度
        token_pnl = trades_df.groupby("token_symbol")["realized_pnl"].sum()
        positive_token_pnl = token_pnl[token_pnl > 0]
        
        if not positive_token_pnl.empty:
            max_token_pnl = positive_token_pnl.max()
            top_token_contribution = max_token_pnl / positive_token_pnl.sum()
            profitable_tokens_count = len(positive_token_pnl)
            
            # HHI 指数 (Herfindahl-Hirschman Index)
            # 计算各盈利代币占比的平方和
            shares = positive_token_pnl / positive_token_pnl.sum()
            hhi_index = (shares ** 2).sum()
        else:
            top_token_contribution = 0.0
            profitable_tokens_count = 0
            hhi_index = 0.0
            
        return {
            "top_trade_contribution": float(top_trade_contribution),
            "top_token_contribution": float(top_token_contribution),
            "hhi_index": float(hhi_index),
            "profitable_tokens_count": int(profitable_tokens_count),
        }
