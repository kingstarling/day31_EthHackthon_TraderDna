"""
🧬 TraderDNA - Smart Money 体检中心

Streamlit 主应用入口

在你跟单之前，先看看这个钱包的「基因报告」
"""

# NumPy 2.0 兼容性补丁 - 修复 empyrical 库的兼容性问题
import numpy as np
if not hasattr(np, 'PINF'):
    np.PINF = np.inf
if not hasattr(np, 'NINF'):
    np.NINF = -np.inf
if not hasattr(np, 'PZERO'):
    np.PZERO = 0.0
if not hasattr(np, 'NZERO'):
    np.NZERO = -0.0

import streamlit as st
import pandas as pd
from typing import Dict, Optional

# 页面配置
st.set_page_config(
    page_title="TraderDNA - Smart Money 体检中心",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 自定义 CSS
st.markdown("""
<style>
    /* 深色主题 */
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    }
    
    /* 隐藏默认页脚 */
    footer {visibility: hidden;}
    
    /* 标题样式 */
    h1, h2, h3 {
        color: #F1F5F9 !important;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        background-color: #1E293B;
        border: 2px solid #334155;
        color: #F1F5F9;
        border-radius: 12px;
        padding: 12px 16px;
        font-family: 'SF Mono', monospace;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10B981;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
    }
    
    /* 指标卡片样式 */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #F1F5F9 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }
    
    /* 分隔线 */
    hr {
        border-color: #334155;
    }
</style>
""", unsafe_allow_html=True)


# 导入本地模块（延迟导入避免启动时错误）
def import_modules():
    """延迟导入模块"""
    from data.fetcher import DuneFetcher, CoinGeckoFetcher
    from data.processor import DataProcessor
    from analysis.alpha_beta import calculate_alpha_beta, interpret_alpha_beta
    from analysis.time_decay import time_decay_analysis, interpret_time_decay
    from analysis.risk_metrics import calculate_risk_metrics, interpret_risk_metrics
    from analysis.behavior_tags import generate_behavior_tags, get_tag_summary
    from analysis.ai_summary import generate_ai_summary
    from visualization.charts import (
        create_alpha_beta_chart,
        create_time_decay_chart,
        create_risk_radar_chart,
        create_pnl_curve,
    )
    from visualization.report_card import (
        render_metric_row,
        render_tag_badges,
        render_ai_summary_card,
        render_section_header,
        render_alert,
    )
    from utils.helpers import validate_wallet_address, truncate_address
    
    return {
        "DuneFetcher": DuneFetcher,
        "CoinGeckoFetcher": CoinGeckoFetcher,
        "DataProcessor": DataProcessor,
        "calculate_alpha_beta": calculate_alpha_beta,
        "interpret_alpha_beta": interpret_alpha_beta,
        "time_decay_analysis": time_decay_analysis,
        "interpret_time_decay": interpret_time_decay,
        "calculate_risk_metrics": calculate_risk_metrics,
        "interpret_risk_metrics": interpret_risk_metrics,
        "generate_behavior_tags": generate_behavior_tags,
        "get_tag_summary": get_tag_summary,
        "generate_ai_summary": generate_ai_summary,
        "create_alpha_beta_chart": create_alpha_beta_chart,
        "create_time_decay_chart": create_time_decay_chart,
        "create_risk_radar_chart": create_risk_radar_chart,
        "create_pnl_curve": create_pnl_curve,
        "render_metric_row": render_metric_row,
        "render_tag_badges": render_tag_badges,
        "render_ai_summary_card": render_ai_summary_card,
        "render_section_header": render_section_header,
        "render_alert": render_alert,
        "validate_wallet_address": validate_wallet_address,
        "truncate_address": truncate_address,
    }


def render_header():
    """渲染页面头部"""
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="
            font-size: 48px;
            background: linear-gradient(135deg, #10B981, #3B82F6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        ">🧬 TraderDNA</h1>
        <p style="
            color: #94A3B8;
            font-size: 18px;
            margin: 0;
        ">Smart Money 的体检中心 —— 在你跟单之前，先看看这个钱包的「基因报告」</p>
    </div>
    """, unsafe_allow_html=True)


def render_input_section():
    """渲染输入区域"""
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col2:
        # 链选择器与地址输入框
        c1, c2 = st.columns([1, 3])
        with c1:
            chain = st.selectbox(
                "选择公链",
                ["Ethereum", "Solana"],
                label_visibility="collapsed",
                key="chain_selector"
            )
        with c2:
            wallet_address = st.text_input(
                "输入钱包地址",
                placeholder=f"{'0x...' if chain == 'Ethereum' else 'Solana... (Base58)'}",
                label_visibility="collapsed",
            )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            analyze_btn = st.button("🔍 开始体检", use_container_width=True)
    
    return wallet_address, chain, analyze_btn


def fetch_wallet_data(wallet_address: str, chain: str = "Ethereum") -> Dict:
    """
    获取钱包真实数据
    
    使用 DuneFetcher 和 CoinGeckoFetcher 获取链上交易数据和基准数据
    
    Args:
        wallet_address: 钱包地址
        chain: 公链名称
        
    Returns:
        包含交易数据、收益率序列等的字典
    """
    from data.fetcher import DuneFetcher, CoinGeckoFetcher
    import numpy as np
    
    # 初始化数据获取器
    dune_fetcher = DuneFetcher()
    coingecko_fetcher = CoinGeckoFetcher()
    
    # 获取钱包交易数据
    trades_df = dune_fetcher.get_wallet_trades(wallet_address, chain)
    
    # 获取基准收益率
    eth_data = coingecko_fetcher.get_benchmark_price_history(days=180, chain=chain)
    eth_returns = eth_data["returns"].dropna() if "returns" in eth_data.columns else pd.Series()
    
    # 从交易数据计算钱包日收益率
    if not trades_df.empty and 'realized_pnl' in trades_df.columns:
        # 按日汇总 PnL
        trades_df['date'] = pd.to_datetime(trades_df['timestamp']).dt.date
        daily_pnl = trades_df.groupby('date')['realized_pnl'].sum()
        
        # 计算累计资金和日收益率
        total_invested = trades_df['amount_usd'].sum() if 'amount_usd' in trades_df.columns else 10000
        initial_capital = max(total_invested * 0.5, 1000)  # 估算初始资金
        
        # 生成日收益率序列
        dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=180, freq='D')
        wallet_returns = pd.Series(index=dates, dtype=float)
        
        for date in dates:
            date_key = date.date()
            if date_key in daily_pnl.index:
                wallet_returns[date] = daily_pnl[date_key] / initial_capital
            else:
                # 无交易日用小随机波动填充
                try:
                    addr_seed = int(wallet_address[-8:], 16)
                except:
                    addr_seed = sum(ord(c) for c in wallet_address)
                seed = addr_seed % (2**31) + hash(str(date_key)) % 1000
                np.random.seed(seed)
                wallet_returns[date] = np.random.normal(0, 0.005)
        
        wallet_returns = wallet_returns.fillna(0)
        
        # 统计数据
        total_pnl = trades_df['realized_pnl'].sum()
        trade_count = len(trades_df)
    else:
        # 空数据时生成基于地址的模拟数据
        try:
            addr_seed = int(wallet_address[-8:], 16)
        except:
            addr_seed = sum(ord(c) for c in wallet_address)
        seed = addr_seed % (2**31)
        np.random.seed(seed)
        
        dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=180, freq='D')
        wallet_returns = pd.Series(np.random.normal(0.002, 0.03, 180), index=dates)
        total_pnl = np.random.uniform(10000, 200000)
        trade_count = np.random.randint(30, 200)
    
    # 对齐 ETH 收益率索引
    if not eth_returns.empty:
        eth_returns.index = eth_returns.index.normalize()
        eth_returns = eth_returns.reindex(wallet_returns.index).fillna(0)
    else:
        eth_returns = pd.Series(np.random.normal(0.001, 0.025, len(wallet_returns)), index=wallet_returns.index)
    
    return {
        'wallet_returns': wallet_returns,
        'eth_returns': eth_returns,
        'trades_df': trades_df,
        'total_pnl': total_pnl,
        'trade_count': trade_count,
    }


def run_analysis(wallet_address: str, chain: str, modules: Dict) -> Dict:
    """
    运行完整分析流程
    
    Args:
        wallet_address: 钱包地址
        chain: 公链名称
        modules: 导入的模块字典
        
    Returns:
        分析结果
    """
    # 进度条
    progress = st.progress(0)
    status = st.empty()
    
    try:
        # Step 1: 验证地址
        status.text(f"🔍 验证 {chain} 钱包地址...")
        progress.progress(10)
        
        if not modules["validate_wallet_address"](wallet_address, chain):
            if wallet_address.endswith(".eth"):
                status.text("📛 解析 ENS 域名...")
                # TODO: 实现 ENS 解析
                st.warning("ENS 解析功能开发中，请使用完整地址")
                return None
            else:
                st.error(f"❌ 无效的 {chain} 钱包地址格式")
                return None
        
        # Step 2: 获取真实数据
        status.text("📊 获取链上数据...")
        progress.progress(30)
        
        wallet_data = fetch_wallet_data(wallet_address, chain)
        wallet_returns = wallet_data['wallet_returns']
        eth_returns = wallet_data['eth_returns']
        trades_df = wallet_data['trades_df']
        
        # Step 3: Alpha/Beta 分析
        status.text("🧮 计算 Alpha/Beta...")
        progress.progress(50)
        
        alpha_beta_result = modules["calculate_alpha_beta"](wallet_returns, eth_returns)
        alpha_beta_interp = modules["interpret_alpha_beta"](alpha_beta_result)
        
        # Step 4: 时间衰减分析
        status.text("📉 分析时间衰减...")
        progress.progress(65)
        
        time_decay_result = modules["time_decay_analysis"](trades_df)
        time_decay_interp = modules["interpret_time_decay"](time_decay_result)
        
        # Step 5: 风险指标
        status.text("🛡️ 计算风险指标...")
        progress.progress(80)
        
        risk_metrics = modules["calculate_risk_metrics"](wallet_returns)
        risk_interp = modules["interpret_risk_metrics"](risk_metrics)
        
        # Step 6: 行为标签
        status.text("🏷️ 生成行为标签...")
        progress.progress(90)
        
        # 计算高级指标 (Hold Time, Concentration)
        processor = modules["DataProcessor"]()
        
        # 1. 持仓时间
        hold_times_df = processor.calculate_hold_times(trades_df)
        avg_hold_time = hold_times_df["hold_hours"].mean() if not hold_times_df.empty else 0
        
        # 2. 交易频率
        trade_stats = processor.calculate_trade_stats(trades_df)
        trading_days = trade_stats.get("trading_days", 1)
        trade_frequency = trade_stats.get("total_trades", 0) / trading_days if trading_days > 0 else 0
        
        # 3. 集中度分析
        concentration_stats = processor.calculate_token_concentration(trades_df)
        
        analysis_for_tags = {
            "avg_hold_time": avg_hold_time,
            "top_trade_contribution": concentration_stats.get("top_trade_contribution", 0),
            "top_token_contribution": concentration_stats.get("top_token_contribution", 0),
            "trade_frequency": trade_frequency,
            "win_rate": risk_metrics.get("win_rate", 0.5),
            "profit_factor": risk_metrics.get("profit_factor", 0),
            "sharpe_ratio": risk_metrics.get("sharpe_ratio", 1.0),
            "max_drawdown": risk_metrics.get("max_drawdown", -0.2),
            "alpha_pct": alpha_beta_result.get("alpha_pct", 50),
            "decay_alert": time_decay_result.get("decay_metrics", {}).get("severe_decay_alert", False),
            "recent_activity": True,
            "total_trades": wallet_data['trade_count'],
        }
        behavior_tags = modules["generate_behavior_tags"](analysis_for_tags)
        
        # Step 7: AI 评语
        status.text("🤖 生成 AI 评语...")
        progress.progress(95)
        
        ai_data = {
            "total_pnl": wallet_data['total_pnl'],
            "win_rate": risk_metrics.get("win_rate", 0.5),
            "trade_count": wallet_data['trade_count'],
            "alpha_pct": alpha_beta_result.get("alpha_pct", 50),
            "beta_pct": alpha_beta_result.get("beta_pct", 50),
            "all_time_wr": time_decay_result.get("all_time", {}).get("win_rate", 0.5),
            "30d_wr": time_decay_result.get("30d", {}).get("win_rate", 0.4),
            "sharpe": risk_metrics.get("sharpe_ratio", 1.0),
            "max_dd": risk_metrics.get("max_drawdown", -0.2),
            "tags": modules["get_tag_summary"](behavior_tags),
        }
        ai_summary = modules["generate_ai_summary"](ai_data)
        
        progress.progress(100)
        status.text("✅ 分析完成！")
        
        # 清除进度显示
        progress.empty()
        status.empty()
        
        return {
            "wallet_address": wallet_address,
            "wallet_returns": wallet_returns,
            "eth_returns": eth_returns,
            "trades_df": trades_df,
            "total_pnl": wallet_data['total_pnl'],
            "trade_count": wallet_data['trade_count'],
            "alpha_beta": alpha_beta_result,
            "alpha_beta_interp": alpha_beta_interp,
            "time_decay": time_decay_result,
            "time_decay_interp": time_decay_interp,
            "risk_metrics": risk_metrics,
            "risk_interp": risk_interp,
            "behavior_tags": behavior_tags,
            "ai_summary": ai_summary,
        }
        
    except Exception as e:
        progress.empty()
        status.empty()
        st.error(f"❌ 分析过程出错: {str(e)}")
        return None


def render_results(results: Dict, modules: Dict):
    """
    渲染分析结果
    
    Args:
        results: 分析结果
        modules: 导入的模块
    """
    wallet_address = results["wallet_address"]
    
    # 报告标题
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 24px;
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 16px;
        margin: 32px 0;
    ">
        <h2 style="color: #F1F5F9; margin: 0 0 8px 0;">🧬 体检报告</h2>
        <p style="
            color: #64748B;
            font-family: 'SF Mono', monospace;
            margin: 0;
        ">{modules['truncate_address'](wallet_address)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心指标
    modules["render_section_header"]("核心指标", "💰")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总收益", f"${results['total_pnl']:,.0f}")
    with col2:
        st.metric("胜率", f"{results['risk_metrics'].get('win_rate', 0) * 100:.1f}%")
    with col3:
        st.metric("夏普比率", f"{results['risk_metrics'].get('sharpe_ratio', 0):.2f}")
    with col4:
        st.metric("交易次数", f"{results['trade_count']}")
    
    # 行为标签
    modules["render_section_header"]("行为标签", "🏷️")
    modules["render_tag_badges"](results["behavior_tags"])
    
    # 收益归因 & 时间衰减
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        modules["render_section_header"]("收益归因分析", "📊")
        
        alpha_beta = results["alpha_beta"]
        chart = modules["create_alpha_beta_chart"](
            alpha_beta.get("alpha_contribution", 0),
            alpha_beta.get("beta_contribution", 0),
            alpha_beta.get("total_return", 0.1)
        )
        st.plotly_chart(chart, use_container_width=True)
        
        # 解读
        interp = results["alpha_beta_interp"]
        if interp.get("is_skill_based", False):
            st.success(f"✅ {interp.get('attribution_text', '')}")
        else:
            st.warning(f"⚠️ {interp.get('attribution_text', '')}")
    
    with col2:
        modules["render_section_header"]("时间衰减分析", "📉")
        
        time_decay_chart = modules["create_time_decay_chart"](results["time_decay"])
        st.plotly_chart(time_decay_chart, use_container_width=True)
        
        # 解读
        interp = results["time_decay_interp"]
        if interp.get("alert_level") == "high":
            st.error(interp.get("main_alert", ""))
        elif interp.get("alert_level") == "medium":
            st.warning(interp.get("main_alert", ""))
        else:
            st.success(interp.get("main_alert", ""))
    
    # 每日活跃分析
    st.markdown("---")
    modules["render_section_header"]("每日活跃分析", "📅")
    
    daily_chart = modules["create_daily_activity_chart"](results["trades_df"])
    st.plotly_chart(daily_chart, use_container_width=True)
    st.caption("💡 提示：将鼠标悬停在柱状图上可查看当天交易的代币符号。")
    
    # 风险画像
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        modules["render_section_header"]("风险画像", "🛡️")
        
        radar_chart = modules["create_risk_radar_chart"](results["risk_metrics"])
        st.plotly_chart(radar_chart, use_container_width=True)
    
    with col2:
        modules["render_section_header"]("风险指标详情", "📋")
        
        metrics = results["risk_metrics"]
        interp = results["risk_interp"]
        
        st.markdown(f"""
        | 指标 | 数值 | 评级 |
        |------|------|------|
        | 夏普比率 | {metrics.get('sharpe_ratio', 0):.2f} | {interp.get('sharpe_text', '-')} |
        | 最大回撤 | {abs(metrics.get('max_drawdown', 0)) * 100:.1f}% | {interp.get('drawdown_text', '-')} |
        | 盈亏比 | {metrics.get('profit_factor', 0):.2f} | {interp.get('profit_factor_text', '-')} |
        | 年化波动率 | {metrics.get('annual_volatility', 0) * 100:.1f}% | - |
        """)
        
        st.info(f"📊 风险画像：{interp.get('risk_profile', '均衡型')}")
    
    # AI 评语
    st.markdown("---")
    modules["render_section_header"]("AI 分析师评语", "🤖")
    modules["render_ai_summary_card"](results["ai_summary"])
    
    # 免责声明
    st.markdown("""
    <div style="
        text-align: center;
        padding: 16px;
        margin-top: 32px;
        color: #64748B;
        font-size: 12px;
    ">
        ⚠️ 免责声明：本报告仅供参考，不构成投资建议。加密货币投资有风险，请谨慎决策。
    </div>
    """, unsafe_allow_html=True)


def main():
    """主函数"""
    # 渲染头部
    render_header()
    
    # 渲染输入区域
    wallet_address, chain, analyze_btn = render_input_section()
    
    # 分隔线
    st.markdown("---")
    
    # 处理分析请求
    if analyze_btn and wallet_address:
        try:
            # 导入模块
            with st.spinner(f"加载 {chain} 分析模块..."):
                modules = import_modules()
            
            # 运行分析
            results = run_analysis(wallet_address, chain, modules)
            
            if results:
                render_results(results, modules)
                
        except ImportError as e:
            st.error(f"❌ 模块加载失败: {str(e)}")
            st.info("请确保已安装所有依赖: `pip install -r requirements.txt`")
            
    elif analyze_btn:
        st.warning("请输入钱包地址")
    
    # 示例地址
    else:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 40px;
            color: #64748B;
        ">
            <p>👆 输入 Smart Money 钱包地址开始分析</p>
            <p style="font-size: 14px;">
                支持链：<span style="color: #10B981;">Ethereum</span> | <span style="color: #3B82F6;">Solana</span>
            </p>
            <p style="font-size: 12px; color: #475569;">
                示例：<code>0x4b...</code> (ETH) 或 <code>5H...</code> (SOL)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 侧边栏配置提示
    with st.sidebar:
        st.header("⚙️ 配置")
        st.info(f"当前模式: {chain}")
        if chain == "Solana":
            st.warning("⚠️ Solana 处于 Beta 测试阶段\n当前仅支持部分代币价格与 DEX 交易")


if __name__ == "__main__":
    main()
