"""
TraderDNA 报告卡片组件模块

使用 Streamlit 创建可视化报告卡片
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional


def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal"
) -> None:
    """
    渲染指标卡片
    
    Args:
        label: 指标标签
        value: 指标值
        delta: 变化值（可选）
        delta_color: 变化值颜色 (normal, inverse, off)
    """
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color,
    )


def render_metric_row(metrics: List[Dict]) -> None:
    """
    渲染一行指标卡片
    
    Args:
        metrics: 指标列表，每个元素包含 label, value, delta (可选)
    """
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
            render_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta"),
                delta_color=metric.get("delta_color", "normal"),
            )


def render_tag_badges(tags: List[Tuple[str, str, str]]) -> None:
    """
    渲染行为标签徽章
    
    Args:
        tags: 标签列表，每个元素为 (emoji, name, description)
    """
    if not tags:
        st.info("暂无明显行为特征")
        return
    
    # 使用 HTML 渲染标签
    badges_html = ""
    for emoji, name, desc in tags:
        badge = f"""
        <span style="display: inline-block; padding: 4px 12px; margin: 4px; border-radius: 16px; background: linear-gradient(135deg, #374151, #1F2937); border: 1px solid #4B5563; font-size: 14px;" title="{desc}">
            {emoji} {name}
        </span>"""
        badges_html += badge
    
    st.markdown(f"""<div style="display: flex; flex-wrap: wrap; gap: 4px; padding: 8px; background: #111827; border-radius: 8px;">{badges_html}</div>""", unsafe_allow_html=True)


def render_ai_summary_card(ai_result: Dict[str, str]) -> None:
    """
    渲染 AI 分析师评语卡片
    
    Args:
        ai_result: AI 分析结果，包含 summary, recommendation, recommendation_emoji
    """
    recommendation = ai_result.get("recommendation", "谨慎")
    emoji = ai_result.get("recommendation_emoji", "⚠️")
    summary = ai_result.get("summary", "")
    confidence = ai_result.get("confidence", "")
    
    # 使用 Streamlit 原生组件避免 HTML 渲染问题
    with st.container():
        # 置信度显示
        if confidence:
            st.caption(f"📊 {confidence}")
        
        # 摘要内容
        st.markdown(summary)
        
        # 跟单建议
        st.divider()
        
        if recommendation == "推荐":
            st.success(f"{emoji} 跟单建议：{recommendation}")
        elif recommendation == "不推荐":
            st.error(f"{emoji} 跟单建议：{recommendation}")
        else:
            st.warning(f"{emoji} 跟单建议：{recommendation}")


def render_section_header(title: str, icon: str = "📊") -> None:
    """
    渲染区块标题
    
    Args:
        title: 标题文本
        icon: 图标
    """
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #374151;
    ">
        <span style="font-size: 24px; margin-right: 8px;">{icon}</span>
        <span style="font-size: 18px; font-weight: 600; color: #F9FAFB;">
            {title}
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_alert(message: str, alert_type: str = "info") -> None:
    """
    渲染警告/提示信息
    
    Args:
        message: 消息内容
        alert_type: 类型 (info, warning, error, success)
    """
    alert_map = {
        "info": st.info,
        "warning": st.warning,
        "error": st.error,
        "success": st.success,
    }
    alert_func = alert_map.get(alert_type, st.info)
    alert_func(message)


def render_full_report(
    wallet_address: str,
    metrics: Dict,
    alpha_beta_result: Dict,
    time_decay_result: Dict,
    risk_metrics: Dict,
    behavior_tags: List[Tuple[str, str, str]],
    ai_summary: Dict,
    charts: Dict
) -> None:
    """
    渲染完整体检报告
    
    Args:
        wallet_address: 钱包地址
        metrics: 基础指标
        alpha_beta_result: Alpha/Beta 分析结果
        time_decay_result: 时间衰减分析结果
        risk_metrics: 风险指标
        behavior_tags: 行为标签
        ai_summary: AI 摘要
        charts: 图表字典
    """
    # 报告标题
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1F2937, #111827);
        border-radius: 12px;
        margin-bottom: 24px;
    ">
        <h1 style="color: #F9FAFB; margin: 0;">🧬 TraderDNA 体检报告</h1>
        <p style="color: #9CA3AF; margin: 8px 0 0 0; font-family: monospace;">
            {wallet_address[:8]}...{wallet_address[-6:] if len(wallet_address) > 14 else wallet_address}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心指标
    render_section_header("核心指标", "💰")
    render_metric_row([
        {
            "label": "总收益",
            "value": f"${metrics.get('total_pnl', 0):,.0f}",
        },
        {
            "label": "胜率",
            "value": f"{metrics.get('win_rate', 0) * 100:.1f}%",
        },
        {
            "label": "夏普比率",
            "value": f"{risk_metrics.get('sharpe_ratio', 0):.2f}",
        },
    ])
    
    # 行为标签
    render_section_header("行为标签", "🏷️")
    render_tag_badges(behavior_tags)
    
    # 收益归因
    render_section_header("收益归因分析", "📊")
    col1, col2 = st.columns([2, 1])
    with col1:
        if "alpha_beta" in charts:
            st.plotly_chart(charts["alpha_beta"], use_container_width=True)
    with col2:
        alpha_pct = alpha_beta_result.get("alpha_pct", 0)
        beta_pct = alpha_beta_result.get("beta_pct", 0)
        
        if alpha_pct > 50:
            st.success(f"✅ 真实力：{alpha_pct:.0f}% 的收益来自 Alpha")
        else:
            st.warning(f"⚠️ 注意：{beta_pct:.0f}% 的收益来自跟大盘")
    
    elif decay_metrics.get("recent_losing"):
        st.warning("⚠️ 注意：该钱包近 30 天处于亏损状态")
    
    # 每日活跃分析
    render_section_header("每日活跃分析", "📅")
    if "daily_activity" in charts:
        st.plotly_chart(charts["daily_activity"], use_container_width=True)
        st.caption("💡 提示：将鼠标悬停在柱状图上可查看当天交易的代币符号。")
    
    # 风险分析
    render_section_header("风险画像", "🛡️")
    col1, col2 = st.columns(2)
    with col1:
        if "risk_radar" in charts:
            st.plotly_chart(charts["risk_radar"], use_container_width=True)
    with col2:
        render_metric_row([
            {"label": "最大回撤", "value": f"{abs(risk_metrics.get('max_drawdown', 0)) * 100:.1f}%"},
            {"label": "盈亏比", "value": f"{risk_metrics.get('profit_factor', 0):.2f}"},
        ])
    
    # AI 评语
    render_section_header("AI 分析师评语", "🤖")
    render_ai_summary_card(ai_summary)
