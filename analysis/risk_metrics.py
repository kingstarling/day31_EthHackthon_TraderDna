"""
TraderDNA 风险指标计算模块

计算夏普比率、最大回撤、盈亏比等风险调整指标
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional

# 不再使用 empyrical，改为手动计算以提高环境兼容性


def calculate_risk_metrics(
    returns_series: pd.Series,
    risk_free_rate: float = 0.04,
    periods_per_year: int = 252
) -> Dict[str, float]:
    """
    计算风险调整指标
    
    Args:
        returns_series: 日收益率序列
        risk_free_rate: 年化无风险利率
        periods_per_year: 每年交易日数
        
    Returns:
        包含各项风险指标的字典
    """
    if returns_series.empty or len(returns_series) < 2:
        return _empty_metrics()
    
    returns = returns_series.dropna()
    
    if len(returns) < 2:
        return _empty_metrics()
    
    # 直接使用手动计算
    metrics = _calculate_manually(returns, risk_free_rate, periods_per_year)
    
    # 添加额外指标
    metrics.update(_calculate_additional_metrics(returns))
    
    return metrics


def _calculate_with_empyrical(
    returns: pd.Series,
    risk_free_rate: float,
    periods_per_year: int
) -> Dict[str, float]:
    """使用 empyrical 库计算指标"""
    daily_rf = risk_free_rate / periods_per_year
    
    return {
        "sharpe_ratio": float(ep.sharpe_ratio(returns, risk_free=daily_rf, annualization=periods_per_year) or 0),
        "sortino_ratio": float(ep.sortino_ratio(returns, required_return=daily_rf, annualization=periods_per_year) or 0),
        "max_drawdown": float(ep.max_drawdown(returns) or 0),
        "calmar_ratio": float(ep.calmar_ratio(returns) or 0),
        "annual_return": float(ep.annual_return(returns, annualization=periods_per_year) or 0),
        "annual_volatility": float(ep.annual_volatility(returns, annualization=periods_per_year) or 0),
    }


def _calculate_manually(
    returns: pd.Series,
    risk_free_rate: float,
    periods_per_year: int
) -> Dict[str, float]:
    """手动计算风险指标"""
    daily_rf = risk_free_rate / periods_per_year
    
    # 年化收益
    total_return = (1 + returns).prod() - 1
    n_periods = len(returns)
    annual_return = (1 + total_return) ** (periods_per_year / n_periods) - 1
    
    # 年化波动率
    annual_volatility = returns.std() * np.sqrt(periods_per_year)
    
    # 夏普比率
    excess_returns = returns - daily_rf
    if annual_volatility > 0:
        sharpe_ratio = (excess_returns.mean() * periods_per_year) / annual_volatility
    else:
        sharpe_ratio = 0.0
    
    # 下行波动率（用于 Sortino）
    downside_returns = returns[returns < daily_rf]
    if len(downside_returns) > 0:
        downside_std = downside_returns.std() * np.sqrt(periods_per_year)
        sortino_ratio = (excess_returns.mean() * periods_per_year) / downside_std if downside_std > 0 else 0
    else:
        sortino_ratio = 0.0
    
    # 最大回撤
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Calmar 比率
    calmar_ratio = annual_return / abs(max_drawdown) if abs(max_drawdown) > 0.0001 else 0.0
    
    return {
        "sharpe_ratio": float(sharpe_ratio),
        "sortino_ratio": float(sortino_ratio),
        "max_drawdown": float(max_drawdown),
        "calmar_ratio": float(calmar_ratio),
        "annual_return": float(annual_return),
        "annual_volatility": float(annual_volatility),
    }


def _calculate_additional_metrics(returns: pd.Series) -> Dict[str, float]:
    """计算额外指标"""
    # 胜率
    win_rate = (returns > 0).mean()
    
    # 盈亏比
    winning_returns = returns[returns > 0]
    losing_returns = returns[returns < 0]
    
    if len(winning_returns) > 0 and len(losing_returns) > 0:
        avg_win = winning_returns.mean()
        avg_loss = abs(losing_returns.mean())
        profit_factor = avg_win / avg_loss if avg_loss > 0 else float('inf')
    else:
        profit_factor = 0.0
    
    # 期望值
    expected_value = returns.mean()
    
    # 最大连续盈利/亏损
    win_streak, loss_streak = _calculate_streaks(returns)
    
    return {
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor),
        "expected_value": float(expected_value),
        "max_win_streak": win_streak,
        "max_loss_streak": loss_streak,
    }


def _calculate_streaks(returns: pd.Series) -> tuple:
    """计算最大连续盈亏次数"""
    wins = (returns > 0).astype(int)
    losses = (returns < 0).astype(int)
    
    def max_streak(series):
        if series.empty:
            return 0
        groups = (series != series.shift()).cumsum()
        counts = series.groupby(groups).sum()
        return int(counts.max()) if not counts.empty else 0
    
    return max_streak(wins), max_streak(losses)


def _empty_metrics() -> Dict[str, float]:
    """返回空指标"""
    return {
        "sharpe_ratio": 0.0,
        "sortino_ratio": 0.0,
        "max_drawdown": 0.0,
        "calmar_ratio": 0.0,
        "annual_return": 0.0,
        "annual_volatility": 0.0,
        "win_rate": 0.0,
        "profit_factor": 0.0,
        "expected_value": 0.0,
        "max_win_streak": 0,
        "max_loss_streak": 0,
    }


def interpret_risk_metrics(metrics: Dict[str, float]) -> Dict[str, str]:
    """
    解读风险指标
    
    Args:
        metrics: calculate_risk_metrics 的返回结果
        
    Returns:
        包含解读文本的字典
    """
    interpretations = {}
    
    # 夏普比率解读
    sharpe = metrics.get("sharpe_ratio", 0)
    if sharpe > 2:
        interpretations["sharpe_text"] = "优秀"
        interpretations["sharpe_level"] = "excellent"
    elif sharpe > 1:
        interpretations["sharpe_text"] = "良好"
        interpretations["sharpe_level"] = "good"
    elif sharpe > 0.5:
        interpretations["sharpe_text"] = "一般"
        interpretations["sharpe_level"] = "average"
    else:
        interpretations["sharpe_text"] = "较差"
        interpretations["sharpe_level"] = "poor"
    
    # 最大回撤解读
    mdd = abs(metrics.get("max_drawdown", 0))
    if mdd < 0.1:
        interpretations["drawdown_text"] = "极低"
        interpretations["drawdown_level"] = "excellent"
    elif mdd < 0.2:
        interpretations["drawdown_text"] = "较低"
        interpretations["drawdown_level"] = "good"
    elif mdd < 0.4:
        interpretations["drawdown_text"] = "中等"
        interpretations["drawdown_level"] = "average"
    else:
        interpretations["drawdown_text"] = "较高"
        interpretations["drawdown_level"] = "poor"
    
    # 盈亏比解读
    profit_factor = metrics.get("profit_factor", 0)
    if profit_factor > 2:
        interpretations["profit_factor_text"] = "优秀"
        interpretations["profit_factor_level"] = "excellent"
    elif profit_factor > 1.5:
        interpretations["profit_factor_text"] = "良好"
        interpretations["profit_factor_level"] = "good"
    elif profit_factor > 1:
        interpretations["profit_factor_text"] = "一般"
        interpretations["profit_factor_level"] = "average"
    else:
        interpretations["profit_factor_text"] = "较差"
        interpretations["profit_factor_level"] = "poor"
    
    # 风险画像
    if sharpe > 1.5 and mdd < 0.2:
        interpretations["risk_profile"] = "稳健收益型：低风险高回报"
    elif sharpe > 1 and mdd > 0.4:
        interpretations["risk_profile"] = "高风险高收益型：愿意承担大回撤"
    elif sharpe < 0.5 and mdd > 0.3:
        interpretations["risk_profile"] = "高风险低收益型：风险收益不匹配"
    else:
        interpretations["risk_profile"] = "均衡型：风险收益适中"
    
    return interpretations
