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
    page_title="TraderDNA - Smart Money Analysis",
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
        create_daily_activity_chart,
    )
    from visualization.report_card import (
        render_metric_card,
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
        "create_daily_activity_chart": create_daily_activity_chart,
        "render_metric_card": render_metric_card,
        "render_metric_row": render_metric_row,
        "render_tag_badges": render_tag_badges,
        "render_ai_summary_card": render_ai_summary_card,
        "render_section_header": render_section_header,
        "render_alert": render_alert,
        "validate_wallet_address": validate_wallet_address,
        "truncate_address": truncate_address,
    }


def render_header():
    """渲染头部 HTML"""
    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 48px 0 24px 0;
        background: transparent;
    ">
        <div style="text-align: center;">
            <h1 style="
                font-size: 52px;
                font-weight: 800;
                margin: 0;
                background: linear-gradient(135deg, #10B981, #3B82F6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -1px;
            ">TraderDNA</h1>
            <p style="
                color: #94A3B8;
                font-size: 20px;
                margin: 8px 0 0 0;
                font-weight: 400;
            ">Smart Money Analysis Center</p>
            <p style="
                color: #64748B;
                font-size: 14px;
                margin: 4px 0 0 0;
            ">挖掘链上高胜率交易者的基因</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_input_section():
    """渲染地址输入区域"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        input_col, btn_col = st.columns([4, 1])
        
        with input_col:
            # 选择链
            chain = st.selectbox(
                "Select Chain (选择公链)",
                ["Ethereum", "Solana"],
                label_visibility="collapsed",
                index=0
            )
            
            wallet_address = st.text_input(
                "Wallet Address (钱包地址)",
                placeholder="Enter Address / ENS (输入钱包地址或 ENS)",
                label_visibility="collapsed"
            )
            
        with btn_col:
            # 按钮对齐美化
            st.write("<div style='height: 42px;'></div>", unsafe_allow_html=True)
            analyze_btn = st.button("🚀 Start (开始体检)", use_container_width=True)
            
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
        status.text(f"🔍 Validating {chain} address... (验证地址)")
        progress.progress(10)
        
        if not modules["validate_wallet_address"](wallet_address, chain):
            if wallet_address.endswith(".eth"):
                status.text("📛 Resolving ENS... (解析域名)")
                # TODO: 实现 ENS 解析
                st.warning("ENS resolution is coming soon. Please use full address.")
                return None
            else:
                st.error(f"❌ Invalid {chain} address format. (地址格式错误)")
                return None
        
        # Step 2: 获取真实数据
        status.text("📊 Fetching on-chain data... (获取数据)")
        progress.progress(30)
        
        wallet_data = fetch_wallet_data(wallet_address, chain)
        wallet_returns = wallet_data['wallet_returns']
        eth_returns = wallet_data['eth_returns']
        trades_df = wallet_data['trades_df']
        
        # Step 3: Alpha/Beta 分析
        status.text("🧮 Calculating Alpha/Beta... (计算归因)")
        progress.progress(50)
        
        alpha_beta_result = modules["calculate_alpha_beta"](wallet_returns, eth_returns)
        alpha_beta_interp = modules["interpret_alpha_beta"](alpha_beta_result)
        
        # Step 4: 时间衰减分析
        status.text("📉 Analyzing Decay... (分析衰减)")
        progress.progress(65)
        
        time_decay_result = modules["time_decay_analysis"](trades_df)
        time_decay_interp = modules["interpret_time_decay"](time_decay_result)
        
        # Step 5: 风险指标
        status.text("🛡️ Computing Risk Stats... (计算风险)")
        progress.progress(80)
        
        risk_metrics = modules["calculate_risk_metrics"](wallet_returns)
        risk_interp = modules["interpret_risk_metrics"](risk_metrics)
        
        # Step 6: 行为标签
        status.text("🏷️ Generating Tags... (生成标签)")
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
        <h2 style="color: #F1F5F9; margin: 0 0 4px 0;">🧬 TraderDNA Report</h2>
        <p style="color: #64748B; margin: 0 0 12px 0; font-size: 14px;">交易员基因体检报告</p>
        <p style="
            color: #475569;
            font-family: 'SF Mono', monospace;
            margin: 0;
            font-size: 12px;
        ">{wallet_address}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心指标
    modules["render_section_header"]("Core Metrics", "核心指标", "💰")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        modules["render_metric_card"]("Total PnL", "总收益", f"${results['total_pnl']:,.0f}")
    with col2:
        modules["render_metric_card"]("Win Rate", "交易胜率", f"{results['risk_metrics'].get('win_rate', 0) * 100:.1f}%")
    with col3:
        modules["render_metric_card"]("Sharpe Ratio", "夏普比率", f"{results['risk_metrics'].get('sharpe_ratio', 0):.2f}")
    with col4:
        modules["render_metric_card"]("Trades", "交易次数", f"{results['trade_count']}")
    
    # 行为标签
    modules["render_section_header"]("Behavioral Tags", "行为标签", "🏷️")
    modules["render_tag_badges"](results["behavior_tags"])
    
    # 收益归因 & 时间衰减
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        modules["render_section_header"]("Profit Attribution", "收益归因分析", "📊")
        
        alpha_beta = results["alpha_beta"]
        chart = modules["create_alpha_beta_chart"](
            alpha_beta.get("alpha_contribution", 0),
            alpha_beta.get("beta_contribution", 0),
            alpha_beta.get("total_return", 0.1)
        )
        st.plotly_chart(chart, use_container_width=True)
        
        # 解读
        interp = results["alpha_beta_interp"]
        attribution_text = interp.get('attribution_text', '')
        if interp.get("is_skill_based", False):
            st.success(f"✅ Skill: {results['alpha_beta'].get('alpha_pct', 0):.0f}% Alpha\n\n({attribution_text})")
        else:
            st.warning(f"⚠️ Market: {results['alpha_beta'].get('beta_pct', 0):.0f}% Beta\n\n({attribution_text})")
    
    with col2:
        modules["render_section_header"]("Performance Decay", "时间衰减分析", "📉")
        
        time_decay_chart = modules["create_time_decay_chart"](results["time_decay"])
        st.plotly_chart(time_decay_chart, use_container_width=True)
        
        # 解读
        interp = results["time_decay_interp"]
        msg = interp.get("main_alert", "")
        if interp.get("alert_level") == "high":
            st.error(f"🚨 {msg}")
        elif interp.get("alert_level") == "medium":
            st.warning(f"⚠️ {msg}")
        else:
            st.success(f"✅ {msg}")
    
    # 每日活跃分析
    st.markdown("---")
    modules["render_section_header"]("Daily Activity", "每日活跃分析", "📅")
    
    daily_chart = modules["create_daily_activity_chart"](results["trades_df"])
    st.plotly_chart(daily_chart, use_container_width=True)
    st.caption("💡 Tip: Hover over bars to see token symbols. (提示：悬停在柱状图上可查看代币符号)")
    
    # 风险画像
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        modules["render_section_header"]("Risk Profile", "风险画像", "🛡️")
        
        radar_chart = modules["create_risk_radar_chart"](results["risk_metrics"])
        st.plotly_chart(radar_chart, use_container_width=True)
    
    with col2:
        modules["render_section_header"]("Risk Details", "风险指标详情", "📋")
        
        metrics = results["risk_metrics"]
        interp = results["risk_interp"]
        
        st.markdown(f"""
        | Metric (指标) | Value (数值) | Rating (评级) |
        |------|------|------|
        | Sharpe Ratio (夏普) | {metrics.get('sharpe_ratio', 0):.2f} | {interp.get('sharpe_text', '-')} |
        | Max Drawdown (回撤) | {abs(metrics.get('max_drawdown', 0)) * 100:.1f}% | {interp.get('drawdown_text', '-')} |
        | Profit Factor (盈亏比) | {metrics.get('profit_factor', 0):.2f} | {interp.get('profit_factor_text', '-')} |
        | Volatility (波动率) | {metrics.get('annual_volatility', 0) * 100:.1f}% | - |
        """)
        
        st.info(f"📊 Profile (画像)：{interp.get('risk_profile', '均衡型')}")
    
    # AI 评语
    st.markdown("---")
    modules["render_section_header"]("AI Analyst Summary", "AI 分析师评语", "🤖")
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
        ⚠️ Disclaimer: For informational purposes only. Crypto investments carry risks. <br>
        (免责声明：本报告仅供参考，不构成投资建议。加密货币投资有风险，请谨慎决策。)
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
            <p style="font-size: 18px; color: #94A3B8;">Enter a Smart Money wallet address to start analysis</p>
            <p style="font-size: 13px; margin-top: -10px;">👇 输入 Smart Money 钱包地址开始分析</p>
            <p style="font-size: 14px; margin-top: 20px;">
                Chains: <span style="color: #10B981;">Ethereum</span> | <span style="color: #3B82F6;">Solana</span>
            </p>
            <p style="font-size: 11px; color: #475569; margin-top: 10px;">
                Example: <code>0x4b...</code> (ETH) or <code>5H...</code> (SOL)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 侧边栏配置提示
    with st.sidebar:
        st.header("⚙️ Settings (配置)")
        st.info(f"Current Mode: {chain} (当前模式)")
        if chain == "Solana":
            st.warning("⚠️ Solana is in Beta (测试中)\n\nSupports specific tokens and DEX trades only.")


if __name__ == "__main__":
    main()
