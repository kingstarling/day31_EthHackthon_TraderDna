"""
TraderDNA Alpha/Beta 分离模块

核心功能：区分真实投资能力（Alpha）和市场跟随（Beta）
这是与 GMGN 最大的差异化功能
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

# 不再使用 empyrical，因为它在 Python 3.12+ 中存在兼容性问题
# 直接使用下方实现的手动计算逻辑


def calculate_alpha_beta(
    wallet_returns: pd.Series,
    eth_returns: pd.Series,
    risk_free_rate: float = 0.04
) -> Dict[str, float]:
    """
    计算 Alpha 和 Beta
    
    Args:
        wallet_returns: 钱包日收益率序列
        eth_returns: ETH 基准日收益率序列
        risk_free_rate: 无风险年化利率（默认 4%）
        
    Returns:
        包含 alpha, beta, alpha_pct, beta_pct 的字典
    """
    if wallet_returns.empty or eth_returns.empty:
        return {
            "alpha": 0.0,
            "beta": 0.0,
            "alpha_pct": 0.0,
            "beta_pct": 0.0,
            "alpha_contribution": 0.0,
            "beta_contribution": 0.0,
            "total_return": 0.0,
        }
    
    # 对齐时间序列
    aligned = pd.concat([wallet_returns, eth_returns], axis=1, keys=["wallet", "eth"]).dropna()
    
    if len(aligned) < 2:
        return {
            "alpha": 0.0,
            "beta": 0.0,
            "alpha_pct": 0.0,
            "beta_pct": 0.0,
            "alpha_contribution": 0.0,
            "beta_contribution": 0.0,
            "total_return": 0.0,
        }
    
    wallet_ret = aligned["wallet"]
    eth_ret = aligned["eth"]
    
    # 直接使用手动计算
    beta, alpha = _calculate_alpha_beta_manual(wallet_ret, eth_ret, risk_free_rate)
    
    # 收益归因
    total_return = (1 + wallet_ret).prod() - 1
    eth_total_return = (1 + eth_ret).prod() - 1
    
    # Beta 贡献 = Beta × 市场收益
    beta_contribution = beta * eth_total_return
    
    # Alpha 贡献 = 总收益 - Beta 贡献
    alpha_contribution = total_return - beta_contribution
    
    # 计算占比
    if abs(total_return) > 0.0001:
        alpha_pct = (alpha_contribution / total_return) * 100
        beta_pct = (beta_contribution / total_return) * 100
    else:
        alpha_pct = 0.0
        beta_pct = 0.0
    
    return {
        "alpha": float(alpha) if alpha is not None else 0.0,
        "beta": float(beta) if beta is not None else 0.0,
        "alpha_pct": float(alpha_pct),
        "beta_pct": float(beta_pct),
        "alpha_contribution": float(alpha_contribution),
        "beta_contribution": float(beta_contribution),
        "total_return": float(total_return),
    }


def _calculate_alpha_beta_manual(
    wallet_returns: pd.Series,
    eth_returns: pd.Series,
    risk_free_rate: float = 0.04
) -> Tuple[float, float]:
    """
    手动计算 Alpha 和 Beta（当 empyrical 不可用时）
    
    使用 CAPM 模型:
    - Beta = Cov(Rp, Rm) / Var(Rm)
    - Alpha = Rp - Rf - Beta × (Rm - Rf)
    
    Args:
        wallet_returns: 钱包日收益率
        eth_returns: ETH 日收益率
        risk_free_rate: 无风险年化利率
        
    Returns:
        (beta, alpha) 元组
    """
    # 日化无风险利率
    rf_daily = risk_free_rate / 252
    
    # 超额收益
    wallet_excess = wallet_returns - rf_daily
    eth_excess = eth_returns - rf_daily
    
    # Beta = Cov(Rp, Rm) / Var(Rm)
    covariance = np.cov(wallet_excess, eth_excess)[0, 1]
    variance = np.var(eth_excess, ddof=1)
    
    if variance > 0:
        beta = covariance / variance
    else:
        beta = 0.0
    
    # Alpha = 平均超额收益 - Beta × 市场平均超额收益
    # 年化
    alpha = (wallet_excess.mean() - beta * eth_excess.mean()) * 252
    
    return beta, alpha


def interpret_alpha_beta(result: Dict[str, float]) -> Dict[str, str]:
    """
    解读 Alpha/Beta 结果
    
    Args:
        result: calculate_alpha_beta 的返回结果
        
    Returns:
        包含解读文本的字典
    """
    interpretations = {}
    
    # Beta 解读
    beta = result.get("beta", 0)
    if beta > 1.5:
        interpretations["beta_text"] = "高杠杆型：比 ETH 波动更大"
        interpretations["beta_level"] = "high"
    elif beta > 1:
        interpretations["beta_text"] = "激进型：略高于市场波动"
        interpretations["beta_level"] = "medium_high"
    elif beta > 0.5:
        interpretations["beta_text"] = "稳健型：与市场适度相关"
        interpretations["beta_level"] = "medium"
    else:
        interpretations["beta_text"] = "独立型：与 ETH 相关性低"
        interpretations["beta_level"] = "low"
    
    # Alpha 解读
    alpha = result.get("alpha", 0)
    if alpha > 0.3:
        interpretations["alpha_text"] = "超强 Alpha：真正的顶级交易员"
        interpretations["alpha_level"] = "excellent"
    elif alpha > 0.1:
        interpretations["alpha_text"] = "优秀 Alpha：有真实的超额能力"
        interpretations["alpha_level"] = "good"
    elif alpha > 0:
        interpretations["alpha_text"] = "正向 Alpha：略有超额表现"
        interpretations["alpha_level"] = "positive"
    elif alpha > -0.1:
        interpretations["alpha_text"] = "接近零 Alpha：基本跟随市场"
        interpretations["alpha_level"] = "neutral"
    else:
        interpretations["alpha_text"] = "负向 Alpha：跑输大盘"
        interpretations["alpha_level"] = "negative"
    
    # Alpha 占比解读
    alpha_pct = result.get("alpha_pct", 0)
    total_return = result.get("total_return", 0)
    is_positive = total_return >= 0
    
    if is_positive:
        if alpha_pct > 70:
            interpretations["attribution_text"] = f"True Skill! {alpha_pct:.0f}% of gains from Alpha (真实力！{alpha_pct:.0f}% 的收益来自 Alpha)"
            interpretations["is_skill_based"] = True
        elif alpha_pct > 50:
            interpretations["attribution_text"] = f"Skilled: {alpha_pct:.0f}% of gains from Alpha (有实力，{alpha_pct:.0f}% 的收益靠能力获得)"
            interpretations["is_skill_based"] = True
        elif alpha_pct > 30:
            interpretations["attribution_text"] = f"Limited Skill: {result.get('beta_pct', 0):.0f}% of gains from Market (能力有限，{result.get('beta_pct', 0):.0f}% 的收益来自跟大盘)"
            interpretations["is_skill_based"] = False
        else:
            interpretations["attribution_text"] = f"Lucky! {result.get('beta_pct', 0):.0f}% of gains from Market Beta (主要靠运气！{result.get('beta_pct', 0):.0f}% 是 Beta 收益)"
            interpretations["is_skill_based"] = False
    else:
        # 负收益情况
        if alpha_pct > 70:
            interpretations["attribution_text"] = f"Strategy Failure: {alpha_pct:.0f}% of losses from decisions (决策失误！{alpha_pct:.0f}% 的亏损源于交易策略)"
            interpretations["is_skill_based"] = True  # 仍然是"个人原因"
        elif alpha_pct > 30:
            interpretations["attribution_text"] = f"Poor Execution: Mixed losses from strategy and market (执行不力：亏损源于策略与市场波动)"
            interpretations["is_skill_based"] = True
        else:
            interpretations["attribution_text"] = f"Market Victim: {result.get('beta_pct', 0):.0f}% of losses from Market (大盘受害者：{result.get('beta_pct', 0):.0f}% 的亏损来自系统性风险)"
            interpretations["is_skill_based"] = False
    
    return interpretations
