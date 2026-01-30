"""
TraderDNA 时间衰减分析模块

分析交易员近期表现是否下滑，发现"当年勇"型选手
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def time_decay_analysis(
    trades_df: pd.DataFrame,
    pnl_column: str = "realized_pnl",
    timestamp_column: str = "timestamp"
) -> Dict[str, Dict]:
    """
    按时间窗口分析表现衰减
    
    Args:
        trades_df: 交易 DataFrame，必须包含 timestamp 和 realized_pnl 列
        pnl_column: PnL 列名
        timestamp_column: 时间戳列名
        
    Returns:
        包含各时间窗口分析结果的字典
        
    Example:
        >>> result = time_decay_analysis(trades_df)
        >>> print(f"全周期胜率: {result['all_time']['win_rate']:.1%}")
        >>> print(f"近30天胜率: {result['30d']['win_rate']:.1%}")
    """
    if trades_df.empty:
        return _empty_result()
    
    df = trades_df.copy()
    df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    
    now = datetime.now()
    
    # 定义时间窗口
    windows = {
        "all_time": None,  # 全部
        "90d": timedelta(days=90),
        "30d": timedelta(days=30),
        "7d": timedelta(days=7),
    }
    
    results = {}
    
    for period, delta in windows.items():
        if delta is None:
            period_df = df
        else:
            cutoff = now - delta
            period_df = df[df[timestamp_column] >= cutoff]
        
        if period_df.empty:
            results[period] = {
                "pnl": 0.0,
                "win_rate": 0.0,
                "trade_count": 0,
                "avg_pnl_per_trade": 0.0,
            }
        else:
            pnl_series = period_df[pnl_column]
            winning_trades = (pnl_series > 0).sum()
            total_trades = len(pnl_series)
            
            results[period] = {
                "pnl": float(pnl_series.sum()),
                "win_rate": winning_trades / total_trades if total_trades > 0 else 0.0,
                "trade_count": total_trades,
                "avg_pnl_per_trade": float(pnl_series.mean()) if total_trades > 0 else 0.0,
            }
    
    # 计算衰减指标
    results["decay_metrics"] = _calculate_decay_metrics(results)
    
    return results


def _calculate_decay_metrics(results: Dict[str, Dict]) -> Dict[str, any]:
    """
    计算衰减相关指标
    
    Args:
        results: 各时间窗口的分析结果
        
    Returns:
        衰减指标字典
    """
    all_time = results.get("all_time", {})
    recent_30d = results.get("30d", {})
    recent_7d = results.get("7d", {})
    
    all_time_wr = all_time.get("win_rate", 0)
    recent_30d_wr = recent_30d.get("win_rate", 0)
    recent_7d_wr = recent_7d.get("win_rate", 0)
    
    # 胜率衰减检测
    win_rate_decay_30d = all_time_wr - recent_30d_wr if all_time_wr > 0 else 0
    win_rate_decay_7d = all_time_wr - recent_7d_wr if all_time_wr > 0 else 0
    
    # 严重衰减警告（近期胜率低于历史的70%）
    severe_decay = recent_30d_wr < all_time_wr * 0.7 if all_time_wr > 0 else False
    
    # PnL 趋势
    all_time_pnl = all_time.get("pnl", 0)
    recent_30d_pnl = recent_30d.get("pnl", 0)
    recent_7d_pnl = recent_7d.get("pnl", 0)
    
    # 近期是否亏损
    recent_losing = recent_30d_pnl < 0
    
    # 活跃度趋势
    all_time_count = all_time.get("trade_count", 0)
    recent_30d_count = recent_30d.get("trade_count", 0)
    
    # 估算30天应有的交易数（如果保持一致）
    if all_time_count > 0:
        # 获取历史天数（简化计算）
        expected_30d_count = all_time_count * 30 / 365  # 假设一年的数据
        activity_ratio = recent_30d_count / expected_30d_count if expected_30d_count > 0 else 1
    else:
        activity_ratio = 0
    
    return {
        "win_rate_decay_30d": float(win_rate_decay_30d),
        "win_rate_decay_7d": float(win_rate_decay_7d),
        "severe_decay_alert": severe_decay,
        "recent_losing": recent_losing,
        "recent_30d_pnl": float(recent_30d_pnl),
        "activity_ratio": float(activity_ratio),
    }


def _empty_result() -> Dict[str, Dict]:
    """返回空结果"""
    empty_period = {
        "pnl": 0.0,
        "win_rate": 0.0,
        "trade_count": 0,
        "avg_pnl_per_trade": 0.0,
    }
    
    return {
        "all_time": empty_period.copy(),
        "90d": empty_period.copy(),
        "30d": empty_period.copy(),
        "7d": empty_period.copy(),
        "decay_metrics": {
            "win_rate_decay_30d": 0.0,
            "win_rate_decay_7d": 0.0,
            "severe_decay_alert": False,
            "recent_losing": False,
            "recent_30d_pnl": 0.0,
            "activity_ratio": 0.0,
        }
    }


def interpret_time_decay(result: Dict[str, Dict]) -> Dict[str, str]:
    """
    解读时间衰减分析结果
    
    Args:
        result: time_decay_analysis 的返回结果
        
    Returns:
        包含解读文本的字典
    """
    decay = result.get("decay_metrics", {})
    
    interpretations = {}
    
    # 主要警告
    if decay.get("severe_decay_alert", False):
        interpretations["main_alert"] = "⚠️ 警告：该钱包近期表现显著下滑"
        interpretations["alert_level"] = "high"
    elif decay.get("recent_losing", False):
        interpretations["main_alert"] = "⚠️ 注意：该钱包近 30 天处于亏损状态"
        interpretations["alert_level"] = "medium"
    else:
        interpretations["main_alert"] = "✅ 表现稳定：近期与历史表现一致"
        interpretations["alert_level"] = "low"
    
    # 胜率趋势
    wr_decay = decay.get("win_rate_decay_30d", 0)
    if wr_decay > 0.2:
        interpretations["win_rate_trend"] = f"胜率大幅下降 {wr_decay:.0%}"
    elif wr_decay > 0.1:
        interpretations["win_rate_trend"] = f"胜率有所下降 {wr_decay:.0%}"
    elif wr_decay < -0.1:
        interpretations["win_rate_trend"] = f"胜率上升 {abs(wr_decay):.0%}"
    else:
        interpretations["win_rate_trend"] = "胜率稳定"
    
    # 活跃度
    activity = decay.get("activity_ratio", 1)
    if activity < 0.3:
        interpretations["activity_text"] = "交易频率大幅降低，可能已不活跃"
    elif activity < 0.7:
        interpretations["activity_text"] = "交易频率有所下降"
    elif activity > 1.5:
        interpretations["activity_text"] = "交易频率上升"
    else:
        interpretations["activity_text"] = "交易频率正常"
    
    # 综合建议
    all_time_pnl = result.get("all_time", {}).get("pnl", 0)
    recent_pnl = result.get("30d", {}).get("pnl", 0)
    
    if all_time_pnl > 0 and recent_pnl < 0:
        interpretations["summary"] = f"历史收益主要来自早期，近期表现不佳。近 30 天亏损 ${abs(recent_pnl):,.0f}"
    elif all_time_pnl > 0 and recent_pnl > 0:
        interpretations["summary"] = f"持续盈利中。近 30 天盈利 ${recent_pnl:,.0f}"
    elif all_time_pnl < 0:
        interpretations["summary"] = "历史总体亏损，不建议跟单"
    else:
        interpretations["summary"] = "数据不足，无法做出判断"
    
    return interpretations
