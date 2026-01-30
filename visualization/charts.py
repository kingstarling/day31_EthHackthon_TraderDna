"""
TraderDNA 图表组件模块

使用 Plotly 创建交互式可视化图表
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


# 颜色主题
COLORS = {
    "alpha": "#10B981",      # 绿色 - Alpha 收益
    "beta": "#6B7280",       # 灰色 - Beta 收益
    "positive": "#22C55E",   # 浅绿 - 正向
    "negative": "#EF4444",   # 红色 - 负向
    "warning": "#F59E0B",    # 橙色 - 警告
    "neutral": "#3B82F6",    # 蓝色 - 中性
    "background": "#1F2937", # 深色背景
    "text": "#F9FAFB",       # 浅色文字
}


def create_alpha_beta_chart(
    alpha_contribution: float,
    beta_contribution: float,
    total_return: float
) -> go.Figure:
    """
    创建 Alpha/Beta 收益归因图
    
    Args:
        alpha_contribution: Alpha 贡献值
        beta_contribution: Beta 贡献值
        total_return: 总收益
        
    Returns:
        Plotly Figure 对象
    """
    # 计算百分比
    if abs(total_return) > 0.0001:
        alpha_pct = (alpha_contribution / total_return) * 100
        beta_pct = (beta_contribution / total_return) * 100
    else:
        alpha_pct = beta_pct = 0
    
    fig = go.Figure()
    
    # 添加条形图
    fig.add_trace(go.Bar(
        x=["收益归因"],
        y=[alpha_pct],
        name=f"Alpha {alpha_pct:.1f}%",
        marker_color=COLORS["alpha"],
        text=[f"Alpha: {alpha_pct:.1f}%"],
        textposition="inside",
    ))
    
    fig.add_trace(go.Bar(
        x=["收益归因"],
        y=[beta_pct],
        name=f"Beta {beta_pct:.1f}%",
        marker_color=COLORS["beta"],
        text=[f"Beta: {beta_pct:.1f}%"],
        textposition="inside",
    ))
    
    fig.update_layout(
        barmode="stack",
        title={
            "text": f"收益归因分析 | 总收益: {total_return * 100:.1f}%",
            "font": {"size": 16, "color": COLORS["text"]},
        },
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["background"],
        font={"color": COLORS["text"]},
        showlegend=True,
        legend={"orientation": "h", "y": -0.2},
        height=300,
    )
    
    return fig


def create_time_decay_chart(time_decay_data: Dict[str, Dict]) -> go.Figure:
    """
    创建时间衰减对比图
    
    Args:
        time_decay_data: time_decay_analysis 的返回结果
        
    Returns:
        Plotly Figure 对象
    """
    periods = ["全周期", "近90天", "近30天", "近7天"]
    period_keys = ["all_time", "90d", "30d", "7d"]
    
    pnl_values = [time_decay_data.get(k, {}).get("pnl", 0) for k in period_keys]
    win_rates = [time_decay_data.get(k, {}).get("win_rate", 0) * 100 for k in period_keys]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("PnL 对比", "胜率对比"),
        specs=[[{"type": "bar"}, {"type": "bar"}]],
        horizontal_spacing=0.15,  # 增加子图间距
    )
    
    # PnL 条形图
    pnl_colors = [COLORS["positive"] if v >= 0 else COLORS["negative"] for v in pnl_values]
    fig.add_trace(
        go.Bar(
            x=periods,
            y=pnl_values,
            marker_color=pnl_colors,
            text=[f"${v:,.0f}" for v in pnl_values],
            textposition="inside",  # 改为内部显示避免截断
            textfont={"size": 10},
            name="PnL",
        ),
        row=1, col=1
    )
    
    # 胜率条形图
    fig.add_trace(
        go.Bar(
            x=periods,
            y=win_rates,
            marker_color=COLORS["neutral"],
            text=[f"{v:.0f}%" for v in win_rates],
            textposition="inside",  # 改为内部显示避免截断
            textfont={"size": 10},
            name="胜率",
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title={
            "text": "时间衰减分析",
            "font": {"size": 16, "color": COLORS["text"]},
        },
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["background"],
        font={"color": COLORS["text"]},
        showlegend=False,
        height=350,
        margin={"l": 40, "r": 40, "t": 60, "b": 60},  # 增加边距
    )
    
    # 更新 Y 轴范围，留出更多空间
    fig.update_yaxes(automargin=True)
    
    return fig


def create_risk_radar_chart(metrics: Dict[str, float]) -> go.Figure:
    """
    创建风险指标雷达图
    
    Args:
        metrics: 风险指标字典
        
    Returns:
        Plotly Figure 对象
    """
    categories = ["夏普比率", "胜率", "盈亏比", "稳定性", "活跃度"]
    
    # 归一化指标到 0-100 范围
    sharpe = min(max(metrics.get("sharpe_ratio", 0) / 3 * 100, 0), 100)
    win_rate = metrics.get("win_rate", 0) * 100
    profit_factor = min(max((metrics.get("profit_factor", 0) - 1) / 2 * 100, 0), 100)
    stability = max(0, 100 - abs(metrics.get("max_drawdown", 0)) * 200)
    activity = 50  # 需要额外数据
    
    values = [sharpe, win_rate, profit_factor, stability, activity]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # 闭合雷达图
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=f"rgba(16, 185, 129, 0.3)",
        line={"color": COLORS["alpha"], "width": 2},
        name="风险画像"
    ))
    
    fig.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, 100],
                "gridcolor": "rgba(255,255,255,0.2)",
            },
            "bgcolor": COLORS["background"],
        },
        title={
            "text": "风险画像雷达图",
            "font": {"size": 16, "color": COLORS["text"]},
        },
        paper_bgcolor=COLORS["background"],
        font={"color": COLORS["text"]},
        showlegend=False,
        height=350,
    )
    
    return fig


def create_pnl_curve(
    returns_series: pd.Series,
    benchmark_returns: Optional[pd.Series] = None
) -> go.Figure:
    """
    创建 PnL 曲线图
    
    Args:
        returns_series: 收益率序列
        benchmark_returns: 基准收益率序列（可选）
        
    Returns:
        Plotly Figure 对象
    """
    if returns_series.empty:
        return go.Figure()
    
    # 计算累计收益
    cumulative = (1 + returns_series).cumprod() - 1
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=cumulative.index,
        y=cumulative.values * 100,
        mode="lines",
        name="钱包收益",
        line={"color": COLORS["alpha"], "width": 2},
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.2)",
    ))
    
    if benchmark_returns is not None and not benchmark_returns.empty:
        benchmark_cumulative = (1 + benchmark_returns).cumprod() - 1
        fig.add_trace(go.Scatter(
            x=benchmark_cumulative.index,
            y=benchmark_cumulative.values * 100,
            mode="lines",
            name="ETH 基准",
            line={"color": COLORS["neutral"], "width": 2, "dash": "dash"},
        ))
    
    # 标记最大回撤
    cummax = (1 + returns_series).cumprod().cummax()
    drawdown = ((1 + returns_series).cumprod() / cummax - 1) * 100
    max_dd_idx = drawdown.idxmin()
    max_dd_val = drawdown.min()
    
    fig.add_annotation(
        x=max_dd_idx,
        y=cumulative.loc[max_dd_idx] * 100,
        text=f"最大回撤: {max_dd_val:.1f}%",
        showarrow=True,
        arrowhead=2,
        arrowcolor=COLORS["negative"],
        font={"color": COLORS["negative"]},
    )
    
    fig.update_layout(
        title={
            "text": "累计收益曲线",
            "font": {"size": 16, "color": COLORS["text"]},
        },
        xaxis_title="日期",
        yaxis_title="累计收益 (%)",
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["background"],
        font={"color": COLORS["text"]},
        hovermode="x unified",
        height=400,
    )
    
    return fig


def create_trade_distribution_chart(
    pnl_values: pd.Series,
    top_n: int = 10
) -> go.Figure:
    """
    创建交易分布图
    
    Args:
        pnl_values: PnL 值序列
        top_n: 显示前N大交易
        
    Returns:
        Plotly Figure 对象
    """
    if pnl_values.empty:
        return go.Figure()
    
    # 排序获取前N大交易
    sorted_pnl = pnl_values.sort_values(ascending=False)
    top_trades = sorted_pnl.head(top_n)
    bottom_trades = sorted_pnl.tail(top_n)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"Top {top_n} 盈利交易", f"Top {top_n} 亏损交易")
    )
    
    # 盈利交易
    fig.add_trace(
        go.Bar(
            y=[f"Trade {i+1}" for i in range(len(top_trades))],
            x=top_trades.values,
            orientation="h",
            marker_color=COLORS["positive"],
            text=[f"${v:,.0f}" for v in top_trades.values],
            textposition="auto",
        ),
        row=1, col=1
    )
    
    # 亏损交易
    fig.add_trace(
        go.Bar(
            y=[f"Trade {i+1}" for i in range(len(bottom_trades))],
            x=bottom_trades.values,
            orientation="h",
            marker_color=COLORS["negative"],
            text=[f"${v:,.0f}" for v in bottom_trades.values],
            textposition="auto",
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title={
            "text": "交易分布",
            "font": {"size": 16, "color": COLORS["text"]},
        },
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["background"],
        font={"color": COLORS["text"]},
        showlegend=False,
        height=400,
    )
    
    return fig
