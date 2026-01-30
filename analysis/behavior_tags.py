"""
TraderDNA 行为标签生成模块

将复杂数据转化为易懂的行为标签
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import sys
sys.path.append('..')
from config import config


@dataclass
class BehaviorTag:
    """行为标签数据类"""
    emoji: str
    name: str
    description: str
    category: str  # positive, negative, neutral, warning


# 预定义标签
TAGS = {
    "diamond_hands": BehaviorTag("💎", "Diamond Hands", "平均持仓超过7天 (Avg Hold > 7d)", "positive"),
    "paper_hands": BehaviorTag("🧻", "Paper Hands", "平均持仓不足1天 (Avg Hold < 1d)", "negative"),
    "gambler": BehaviorTag("🎰", "Gambler", "高频交易且赔率不佳 (High freq, bad odds)", "warning"),
    "conservative": BehaviorTag("🐢", "Conservative", "低风险稳定收益 (Low risk, stable)", "positive"),
    "one_hit_wonder": BehaviorTag("🚀", "One-Hit Wonder", "收益主要来自单笔交易 (Single win reliance)", "warning"),
    "one_token_pony": BehaviorTag("🦄", "One-Token Pony", "收益主要来自单一币种 (Concentrated on one token)", "warning"),
    "suspicious": BehaviorTag("🐀", "Suspicious", "多次在暴涨前精准买入 (Insider-like precision)", "warning"),
    "whale": BehaviorTag("🐋", "Whale", "大额交易者 (High volume trader)", "neutral"),
    "sniper": BehaviorTag("🎯", "Sniper", "高胜率精准出手 (High win rate sniper)", "positive"),
    "fomo_buyer": BehaviorTag("😱", "FOMO Buyer", "常在高点追涨 (Chasing pumps)", "negative"),
    "smart_money": BehaviorTag("🧠", "Smart Money", "综合表现优秀 (High Alpha & skill)", "positive"),
    "declining": BehaviorTag("📉", "Declining", "近期表现不如历史 (Performance decay)", "warning"),
    "active_trader": BehaviorTag("⚡", "Active Trader", "交易频繁 (Frequently trading)", "neutral"),
    "dormant": BehaviorTag("😴", "Dormant", "近期不活跃 (Inactive recently)", "neutral"),
}

# 对应的中文翻译（辅助显示）
TAGS_ZH = {
    "Diamond Hands": "钻石手",
    "Paper Hands": "纸手",
    "Gambler": "高频赌徒",
    "Conservative": "稳健派",
    "One-Hit Wonder": "一战成名",
    "One-Token Pony": "单币战士",
    "Suspicious": "疑似内幕",
    "Whale": "巨鲸",
    "Sniper": "狙击手",
    "FOMO Buyer": "FOMO买家",
    "Smart Money": "聪明钱",
    "Declining": "近期下滑",
    "Active Trader": "活跃交易者",
    "Dormant": "休眠账户",
}


def generate_behavior_tags(analysis_results: Dict) -> List[Tuple[str, str, str]]:
    """
    根据分析结果生成行为标签
    
    Args:
        analysis_results: 包含以下键的字典:
            - avg_hold_time: 平均持仓时间（小时）
            - top_trade_contribution: 单笔交易最大贡献比例
            - top_token_contribution: 单一币种最大贡献比例
            - avg_time_before_pump: 平均暴涨前买入时间（分钟）
            - trade_frequency: 日均交易次数
            - win_rate: 胜率
            - profit_factor: 盈亏比
            - sharpe_ratio: 夏普比率
            - max_drawdown: 最大回撤
            - total_trades: 总交易次数
            - recent_activity: 近期是否活跃
            - decay_alert: 是否有衰减警告
            
    Returns:
        标签列表，每个元素为 (emoji, name, description) 元组
    """
    tags = []
    
    # 持仓时间标签
    avg_hold_time = analysis_results.get("avg_hold_time", 0)
    if avg_hold_time > config.DIAMOND_HANDS_MIN_HOLD_HOURS:
        tag = TAGS["diamond_hands"]
        tags.append((tag.emoji, tag.name, f"平均持仓 {avg_hold_time / 24:.1f} 天"))
    elif avg_hold_time < config.PAPER_HANDS_MAX_HOLD_HOURS and avg_hold_time > 0:
        tag = TAGS["paper_hands"]
        tags.append((tag.emoji, tag.name, f"平均持仓仅 {avg_hold_time:.1f} 小时"))
    
    # 一战成名检测 (单笔)
    top_contribution = analysis_results.get("top_trade_contribution", 0)
    if top_contribution > config.ONE_HIT_WONDER_THRESHOLD:
        tag = TAGS["one_hit_wonder"]
        tags.append((tag.emoji, tag.name, f"单笔交易贡献 {top_contribution * 100:.0f}% 收益"))
        
    # 单币战士检测 (Token Concentration)
    top_token_contribution = analysis_results.get("top_token_contribution", 0)
    if top_token_contribution > 0.8: # 80% 收益来自一个币
        tag = TAGS["one_token_pony"]
        tags.append((tag.emoji, tag.name, f"{top_token_contribution * 100:.0f}% 收益来自单一币种"))
    
    # 疑似老鼠仓检测
    avg_time_before_pump = analysis_results.get("avg_time_before_pump", float('inf'))
    if avg_time_before_pump < config.SUSPICIOUS_TIME_BEFORE_PUMP_MINUTES:
        tag = TAGS["suspicious"]
        tags.append((tag.emoji, tag.name, f"平均在暴涨前 {avg_time_before_pump:.0f} 分钟买入"))
    
    # 赌徒检测 (优化版：考虑盈亏比)
    trade_frequency = analysis_results.get("trade_frequency", 0)
    win_rate = analysis_results.get("win_rate", 0)
    profit_factor = analysis_results.get("profit_factor", 0)
    
    # 定义：高频 + 低胜率 + 还可以的盈亏比 = 不是赌徒
    # 赌徒：高频 + 低胜率 + 低盈亏比
    if trade_frequency > config.HIGH_FREQUENCY_THRESHOLD:
        if win_rate < config.LOW_WIN_RATE_THRESHOLD:
            if profit_factor < 1.0:
                tag = TAGS["gambler"]
                tags.append((tag.emoji, tag.name, f"高频交易但亏损 (PF: {profit_factor:.2f})"))
            elif profit_factor > 1.5:
                # 高盈亏比，虽然胜率低，但可能是策略
                tag = TAGS["sniper"] # 复用狙击手或者新加一个 "High Risk High Reward"
                # 这里暂时不打赌徒标签
                pass
    
    # 狙击手检测
    if win_rate > 0.7 and trade_frequency < 5 and profit_factor > 1.5:
        tag = TAGS["sniper"]
        tags.append((tag.emoji, tag.name, f"胜率 {win_rate * 100:.0f}%，盈亏比 {profit_factor:.2f}"))
    
    # 稳健派检测
    sharpe = analysis_results.get("sharpe_ratio", 0)
    max_dd = abs(analysis_results.get("max_drawdown", 0))
    if sharpe > 2 and max_dd < 0.2:
        tag = TAGS["conservative"]
        tags.append((tag.emoji, tag.name, f"夏普 {sharpe:.2f}，最大回撤仅 {max_dd * 100:.0f}%"))
    
    # 聪明钱检测
    alpha_pct = analysis_results.get("alpha_pct", 0)
    if alpha_pct > 60 and win_rate > 0.6 and sharpe > 1.5:
        tag = TAGS["smart_money"]
        tags.append((tag.emoji, tag.name, f"Alpha 占比 {alpha_pct:.0f}%，综合表现优秀"))
    
    # 近期下滑检测
    if analysis_results.get("decay_alert", False):
        tag = TAGS["declining"]
        tags.append((tag.emoji, tag.name, "近期表现显著不如历史"))
    
    # 活跃度检测
    recent_activity = analysis_results.get("recent_activity", True)
    total_trades = analysis_results.get("total_trades", 0)
    
    if not recent_activity and total_trades > 0:
        tag = TAGS["dormant"]
        tags.append((tag.emoji, tag.name, "近 30 天无交易"))
    elif trade_frequency > 5:
        tag = TAGS["active_trader"]
        tags.append((tag.emoji, tag.name, f"日均交易 {trade_frequency:.1f} 笔"))
    
    # 巨鲸检测
    avg_trade_value = analysis_results.get("avg_trade_value", 0)
    if avg_trade_value > 50000:  # 平均交易超过 5 万美金
        tag = TAGS["whale"]
        tags.append((tag.emoji, tag.name, f"平均交易额 ${avg_trade_value:,.0f}"))
    
    return tags


def get_tag_summary(tags: List[Tuple[str, str, str]]) -> str:
    """
    生成标签摘要文本
    
    Args:
        tags: 标签列表
        
    Returns:
        摘要字符串
    """
    if not tags:
        return "暂无明显特征"
    
    return " ".join([f"[{emoji} {name}]" for emoji, name, _ in tags])


def categorize_tags(tags: List[Tuple[str, str, str]]) -> Dict[str, List]:
    """
    按类别分组标签
    
    Args:
        tags: 标签列表
        
    Returns:
        按类别分组的字典
    """
    categorized = {
        "positive": [],
        "negative": [],
        "warning": [],
        "neutral": [],
    }
    
    for emoji, name, desc in tags:
        # 查找标签类别
        for tag_key, tag_obj in TAGS.items():
            if tag_obj.name == name:
                categorized[tag_obj.category].append((emoji, name, desc))
                break
    
    return categorized
