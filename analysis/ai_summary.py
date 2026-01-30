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
                    "content": "你是一位专业的链上分析师，擅长分析 crypto 交易员的表现。请用简洁、专业的语言给出投资建议。"
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
请根据以下数据为这个钱包生成一段简洁的投资建议（100字以内）：

## 基础数据
- 总收益: ${data.get('total_pnl', 0):,.0f}
- 胜率: {data.get('win_rate', 0) * 100:.1f}%
- 交易次数: {data.get('trade_count', 0)}

## 归因分析
- Alpha占比: {data.get('alpha_pct', 0):.1f}% (真实力)
- Beta占比: {data.get('beta_pct', 0):.1f}% (跟大盘)

## 时间衰减
- 全周期胜率: {data.get('all_time_wr', 0) * 100:.1f}%
- 近30天胜率: {data.get('30d_wr', 0) * 100:.1f}%

## 风险指标
- 夏普比率: {data.get('sharpe', 0):.2f}
- 最大回撤: {abs(data.get('max_dd', 0)) * 100:.1f}%

## 行为标签
{data.get('tags', '暂无标签')}

请给出：
1. 一句话总结这个交易员的风格
2. 是否值得跟单的建议（推荐/谨慎/不推荐）
3. 如果跟单，需要注意什么
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
        return "高置信度"
    elif trade_count >= 30:
        return "中等置信度"
    else:
        return "低置信度（数据不足）"


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
    style_parts = []
    
    if alpha_pct > 60:
        style_parts.append("真实力型")
    elif beta_pct > 60:
        style_parts.append("跟大盘型")
    
    if all_time_wr > 0 and recent_wr / all_time_wr < 0.7:
        style_parts.append("近期下滑")
    
    if sharpe > 2:
        style_parts.append("稳健")
    elif max_dd > 0.4:
        style_parts.append("高风险")
    
    style = "【" + "，".join(style_parts) + "】" if style_parts else "【普通交易员】"
    
    # 生成建议
    recommendation = "谨慎"
    if alpha_pct > 50 and sharpe > 1.5 and recent_wr >= all_time_wr * 0.8:
        recommendation = "推荐"
    elif alpha_pct < 30 or sharpe < 0.5 or total_pnl < 0:
        recommendation = "不推荐"
    
    # 生成注意事项
    notes = []
    if beta_pct > 50:
        notes.append(f"{beta_pct:.0f}% 的收益来自 Beta（跟随大盘）")
    if all_time_wr > 0 and recent_wr < all_time_wr * 0.7:
        notes.append("近期表现显著下滑")
    if max_dd > 0.3:
        notes.append(f"最大回撤达 {max_dd * 100:.0f}%，需控制仓位")
    
    notes_text = "；".join(notes) if notes else "无特别注意事项"
    
    summary = f"""该交易员属于{style}。

总收益 ${total_pnl:,.0f}，其中 Alpha 占比 {alpha_pct:.0f}%，Beta 占比 {beta_pct:.0f}%。

📊 跟单建议：{_get_recommendation_emoji(recommendation)} {recommendation}

⚠️ 注意事项：{notes_text}"""
    
    return {
        "summary": summary,
        "recommendation": recommendation,
        "recommendation_emoji": _get_recommendation_emoji(recommendation),
        "confidence": _calculate_confidence(data),
    }
