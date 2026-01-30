"""
TraderDNA AI 评语生成模块

使用 OpenAI GPT-4 生成专业的投资分析评语
"""

from typing import Dict, Optional
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

import sys
sys.path.append('..')
from config import config


def generate_ai_summary(
    analysis_data: Dict,
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    使用 AI 生成分析评语
    
    Args:
        analysis_data: 分析数据字典，包含:
            - total_pnl: 总收益
            - win_rate: 胜率
            - trade_count: 交易次数
            - alpha_pct: Alpha 占比
            - beta_pct: Beta 占比
            - all_time_wr: 全周期胜率
            - 30d_wr: 近30天胜率
            - sharpe: 夏普比率
            - max_dd: 最大回撤
            - tags: 行为标签文本
        api_key: OpenAI API Key（可选）
        
    Returns:
        包含 AI 评语的字典
    """
    if OpenAI is None:
        return _generate_fallback_summary(analysis_data)
    
    key = api_key or config.OPENAI_API_KEY
    if not key:
        return _generate_fallback_summary(analysis_data)
    
    try:
        client = OpenAI(api_key=key)
        
        prompt = _build_prompt(analysis_data)
        
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional on-chain analyst. Analyze crypto traders. Provide feedback in BILINGUAL format: English first, then Chinese in brackets or a new line. Primary language is English."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=config.AI_MAX_TOKENS,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        return _parse_ai_response(ai_response, analysis_data)
        
    except Exception as e:
        print(f"AI 生成失败: {e}")
        return _generate_fallback_summary(analysis_data)


def _build_prompt(data: Dict) -> str:
    """构建 AI Prompt"""
    return f"""
Analyze this wallet performance and provide a professional investment summary (under 150 words).
Format: English first, with Chinese translation provided as a sub-text/smaller font below each point if possible, or simply follow each English sentence with a Chinese translation in parentheses.

## DATA
- Total PnL: ${data.get('total_pnl', 0):,.0f}
- Win Rate: {data.get('win_rate', 0) * 100:.1f}%
- Trades: {data.get('trade_count', 0)}
- Alpha: {data.get('alpha_pct', 0):.1f}% (Skill)
- Beta: {data.get('beta_pct', 0):.1f}% (Market)
- Sharpe: {data.get('sharpe', 0):.2f}
- Max DD: {abs(data.get('max_dd', 0)) * 100:.1f}%
- Behavioral Tags: {data.get('tags', 'N/A')}

Please provide:
1. One-sentence summary of the trader's style.
2. Clear recommendation (Recommended / Caution / Not Recommended).
3. If copying, what risks to watch out for.
"""


def _parse_ai_response(response: str, data: Dict) -> Dict[str, str]:
    """解析 AI 响应"""
    # 尝试判断建议类型
    recommendation = "谨慎"
    if "推荐" in response and "不推荐" not in response:
        recommendation = "推荐"
    elif "不推荐" in response:
        recommendation = "不推荐"
    elif "谨慎" in response:
        recommendation = "谨慎"
    
    return {
        "summary": response,
        "recommendation": recommendation,
        "recommendation_emoji": _get_recommendation_emoji(recommendation),
        "confidence": _calculate_confidence(data),
    }


def _get_recommendation_emoji(recommendation: str) -> str:
    """获取建议对应的表情"""
    emoji_map = {
        "推荐": "✅",
        "谨慎": "⚠️",
        "不推荐": "❌",
    }
    return emoji_map.get(recommendation, "❓")


def _calculate_confidence(data: Dict) -> str:
    """计算分析置信度"""
    trade_count = data.get("trade_count", 0)
    
    if trade_count >= 100:
        return "High Confidence (高置信度)"
    elif trade_count >= 30:
        return "Medium Confidence (中等置信度)"
    else:
        return "Low Confidence (低置信度-数据不足)"


def _generate_fallback_summary(data: Dict) -> Dict[str, str]:
    """
    生成备用摘要（当 AI 不可用时）
    
    使用规则引擎生成评语
    """
    total_pnl = data.get("total_pnl", 0)
    win_rate = data.get("win_rate", 0)
    alpha_pct = data.get("alpha_pct", 0)
    beta_pct = data.get("beta_pct", 0)
    sharpe = data.get("sharpe", 0)
    max_dd = abs(data.get("max_dd", 0))
    all_time_wr = data.get("all_time_wr", 0)
    recent_wr = data.get("30d_wr", 0)
    
    # 生成风格描述
    style_parts_en = []
    style_parts_zh = []
    
    if alpha_pct > 60:
        style_parts_en.append("Skill-based")
        style_parts_zh.append("实战型")
    elif beta_pct > 60:
        style_parts_en.append("Market-following")
        style_parts_zh.append("行情跟随型")
    
    if all_time_wr > 0 and recent_wr / all_time_wr < 0.7:
        style_parts_en.append("Performance Decay")
        style_parts_zh.append("近期下滑")
    
    if sharpe > 2:
        style_parts_en.append("Stable")
        style_parts_zh.append("稳健")
    elif max_dd > 0.4:
        style_parts_en.append("High Risk")
        style_parts_zh.append("高风险")
    
    style_en = " / ".join(style_parts_en) if style_parts_en else "Average Trader"
    style_zh = " / ".join(style_parts_zh) if style_parts_zh else "普通交易员"
    
    # 生成建议
    recommendation = "谨慎"
    rec_en = "Caution"
    if alpha_pct > 50 and sharpe > 1.5 and recent_wr >= all_time_wr * 0.8:
        recommendation = "推荐"
        rec_en = "Recommended"
    elif alpha_pct < 30 or sharpe < 0.5 or total_pnl < 0:
        recommendation = "不推荐"
        rec_en = "Not Recommended"
    
    summary = f"""**Trader Style:** {style_en} <br> <span style="font-size: 11px; color: #9CA3AF;">交易员风格：{style_zh}</span>
    
**Performance:** Total PnL is ${total_pnl:,.0f} with {alpha_pct:.0f}% Alpha (skill). <br> <span style="font-size: 11px; color: #9CA3AF;">表现：总收益 ${total_pnl:,.0f}，Alpha 占比 {alpha_pct:.0f}%</span>

**Recommendation:** {rec_en} <br> <span style="font-size: 11px; color: #9CA3AF;">跟单建议：{recommendation}</span>
"""
    
    return {
        "summary": summary,
        "recommendation": recommendation,
        "recommendation_emoji": _get_recommendation_emoji(recommendation),
        "confidence": _calculate_confidence(data),
    }
