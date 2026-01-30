"""
TraderDNA 报告卡片组件模块

使用 Streamlit 创建可视化报告卡片
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional


def render_metric_card(
    label_en: str,
    label_zh: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal"
) -> None:
    """
    渲染双语指标卡片
    """
    label_html = f"""
    <div style="display: flex; flex-direction: column; margin-bottom: 4px;">
        <span style="font-size: 14px; color: #94A3B8; font-weight: 500;">{label_en}</span>
        <span style="font-size: 11px; color: #64748B;">{label_zh}</span>
    </div>
    """
    st.markdown(label_html, unsafe_allow_html=True)
    st.metric(
        label="", # 隐藏原生标签
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
                label_en=metric.get("label_en", ""),
                label_zh=metric.get("label_zh", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta"),
                delta_color=metric.get("delta_color", "normal"),
            )


def render_tag_badges(tags: List[Tuple[str, str, str]]) -> None:
    """
    渲染双语行为标签徽章
    """
    from analysis.behavior_tags import TAGS_ZH
    
    if not tags:
        st.info("No significant behavioral traits detected. (暂无明显行为特征)")
        return
    
    badges_html = ""
    for emoji, name_en, desc in tags:
        name_zh = TAGS_ZH.get(name_en, "")
        badge = f"""
        <div style="
            display: flex; 
            flex-direction: column; 
            align-items: center;
            justify-content: center;
            padding: 6px 14px; 
            margin: 4px; 
            border-radius: 12px; 
            background: linear-gradient(135deg, #374151, #1F2937); 
            border: 1px solid #4B5563;
            min-width: 100px;
        " title="{desc}">
            <div style="font-size: 14px; color: #F9FAFB; font-weight: 500;">{emoji} {name_en}</div>
            <div style="font-size: 10px; color: #9CA3AF; margin-top: 2px;">{name_zh}</div>
        </div>"""
        badges_html += badge
    
    st.markdown(f"""<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 12px; background: #111827; border-radius: 12px; border: 1px solid #1F2937;">{badges_html}</div>""", unsafe_allow_html=True)


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
        st.markdown(summary, unsafe_allow_html=True)
        
        # 跟单建议
        st.divider()
        
        if recommendation == "推荐":
            st.success(f"{emoji} Recommendation: Recommended (建议跟单)")
        elif recommendation == "不推荐":
            st.error(f"{emoji} Recommendation: Not Recommended (不建议跟单)")
        else:
            st.warning(f"{emoji} Recommendation: Caution (谨慎跟单)")


def render_section_header(title_en: str, title_zh: str, icon: str = "📊") -> None:
    """
    渲染双语区块标题
    """
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #374151;
    ">
        <span style="font-size: 24px; margin-right: 12px;">{icon}</span>
        <div style="display: flex; flex-direction: column;">
            <span style="font-size: 18px; font-weight: 600; color: #F9FAFB; line-height: 1.2;">{title_en}</span>
            <span style="font-size: 13px; color: #9CA3AF; margin-top: 2px;">{title_zh}</span>
        </div>
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
        padding: 24px;
        background: linear-gradient(135deg, #1F2937, #111827);
        border-radius: 12px;
        margin-bottom: 32px;
    ">
        <h1 style="color: #F9FAFB; margin: 0; font-size: 28px;">🧬 TraderDNA Report</h1>
        <p style="color: #9CA3AF; margin: 4px 0 12px 0; font-size: 14px;">交易员基因分析报告</p>
        <p style="color: #6B7280; margin: 0; font-family: monospace; font-size: 12px;">
            {wallet_address}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心指标
    render_section_header("Core Metrics", "核心指标", "💰")
    render_metric_row([
        {
            "label_en": "Total PnL",
            "label_zh": "总收益",
            "value": f"${metrics.get('total_pnl', 0):,.0f}",
        },
        {
            "label_en": "Win Rate",
            "label_zh": "交易胜率",
            "value": f"{metrics.get('win_rate', 0) * 100:.1f}%",
        },
        {
            "label_en": "Sharpe Ratio",
            "label_zh": "夏普比率",
            "value": f"{risk_metrics.get('sharpe_ratio', 0):.2f}",
        },
    ])
    
    # 行为标签
    render_section_header("Behavioral Tags", "行为标签", "🏷️")
    render_tag_badges(behavior_tags)
    
    # 收益归因
    render_section_header("Profit Attribution", "收益归因分析", "📊")
    col1, col2 = st.columns([2, 1])
    with col1:
        if "alpha_beta" in charts:
            st.plotly_chart(charts["alpha_beta"], use_container_width=True)
    with col2:
        alpha_pct = alpha_beta_result.get("alpha_pct", 0)
        beta_pct = alpha_beta_result.get("beta_pct", 0)
        
        if alpha_pct > 50:
            st.success(f"✅ Skill: {alpha_pct:.0f}% Alpha\n\n(来自真实操盘能力)")
        else:
            st.warning(f"⚠️ Market: {beta_pct:.0f}% Beta\n\n(主要随大盘波动)")
    
    # 时间衰减分析
    render_section_header("Performance Decay", "时间衰减分析", "📉")
    if "time_decay" in charts:
        st.plotly_chart(charts["time_decay"], use_container_width=True)
    
    decay_metrics = time_decay_result.get("decay_metrics", {})
    if decay_metrics.get("severe_decay_alert"):
        st.error("⚠️ Warning: Significant performance decay detected recently.\n\n(警告：近期表现显著下滑)")
    elif decay_metrics.get("recent_losing"):
        st.warning("⚠️ Note: Currently in a losing streak (past 30 days).\n\n(注意：近 30 天处于亏损状态)")
    
    # 每日活跃分析
    render_section_header("Daily Activity", "每日活跃分析", "📅")
    if "daily_activity" in charts:
        st.plotly_chart(charts["daily_activity"], use_container_width=True)
        st.caption("💡 Tip: Hover over bars to see token details. (提示：悬停在柱状图上可查看代币详情)")
    
    # 风险分析
    render_section_header("Risk Profile", "风险画像", "🛡️")
    col1, col2 = st.columns(2)
    with col1:
        if "risk_radar" in charts:
            st.plotly_chart(charts["risk_radar"], use_container_width=True)
    with col2:
        render_metric_row([
            {"label_en": "Max Drawdown", "label_zh": "最大回撤", "value": f"{abs(risk_metrics.get('max_drawdown', 0)) * 100:.1f}%"},
            {"label_en": "Profit Factor", "label_zh": "盈亏比", "value": f"{risk_metrics.get('profit_factor', 0):.2f}"},
        ])
    
    # AI 评语
    render_section_header("AI Analyst Summary", "AI 分析师评语", "🤖")
    render_ai_summary_card(ai_summary)

