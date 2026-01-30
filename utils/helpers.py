"""
TraderDNA 工具函数模块

提供通用工具函数
"""

import re
from typing import Optional


def validate_wallet_address(address: str, chain: str = "Ethereum") -> bool:
    """
    验证钱包地址格式
    
    Args:
        address: 钱包地址字符串
        chain: 公链名称 ("Ethereum" 或 "Solana")
        
    Returns:
        是否为有效地址
    """
    if not address:
        return False
    
    if chain == "Ethereum":
        # 以太坊地址格式: 0x + 40 个十六进制字符
        pattern = r"^0x[a-fA-F0-9]{40}$"
        return bool(re.match(pattern, address))
    elif chain == "Solana":
        # Solana 地址格式: Base58, 32-44 字符
        # 简单正则: 排除 0, O, I, l
        pattern = r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"
        return bool(re.match(pattern, address))
    
    return False


def resolve_ens(ens_name: str) -> Optional[str]:
    """
    解析 ENS 域名为地址
    
    Args:
        ens_name: ENS 域名（如 vitalik.eth）
        
    Returns:
        解析后的地址或 None
    """
    # TODO: 实现 ENS 解析
    # 可以使用 web3.py 或 ens 库
    
    # 简单判断是否为 ENS 格式
    if ens_name.endswith(".eth"):
        # 这里需要实际的 ENS 解析逻辑
        return None
    
    return None


def format_currency(
    value: float,
    currency: str = "USD",
    decimals: int = 2
) -> str:
    """
    格式化货币显示
    
    Args:
        value: 数值
        currency: 货币类型
        decimals: 小数位数
        
    Returns:
        格式化后的字符串
        
    Example:
        >>> format_currency(1234567.89)
        '$1,234,567.89'
        >>> format_currency(-1234.5)
        '-$1,234.50'
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "ETH": "Ξ",
        "BTC": "₿",
    }
    
    symbol = currency_symbols.get(currency, "$")
    
    if value < 0:
        return f"-{symbol}{abs(value):,.{decimals}f}"
    else:
        return f"{symbol}{value:,.{decimals}f}"


def format_percentage(
    value: float,
    decimals: int = 1,
    include_sign: bool = False
) -> str:
    """
    格式化百分比显示
    
    Args:
        value: 小数值（0.15 = 15%）
        decimals: 小数位数
        include_sign: 是否包含正负号
        
    Returns:
        格式化后的字符串
        
    Example:
        >>> format_percentage(0.1567)
        '15.7%'
        >>> format_percentage(0.1567, include_sign=True)
        '+15.7%'
    """
    pct = value * 100
    
    if include_sign and pct > 0:
        return f"+{pct:.{decimals}f}%"
    else:
        return f"{pct:.{decimals}f}%"


def truncate_address(address: str, prefix_len: int = 6, suffix_len: int = 4) -> str:
    """
    截断钱包地址显示
    
    Args:
        address: 完整地址
        prefix_len: 前缀长度
        suffix_len: 后缀长度
        
    Returns:
        截断后的地址
        
    Example:
        >>> truncate_address("0x1234567890123456789012345678901234567890")
        '0x1234...7890'
    """
    if not address:
        return ""
    
    if len(address) <= prefix_len + suffix_len + 3:
        return address
    
    return f"{address[:prefix_len]}...{address[-suffix_len:]}"


def calculate_time_ago(timestamp) -> str:
    """
    计算距今时间
    
    Args:
        timestamp: 时间戳
        
    Returns:
        人类可读的时间差
    """
    from datetime import datetime
    import pandas as pd
    
    if timestamp is None:
        return "未知"
    
    if isinstance(timestamp, str):
        timestamp = pd.to_datetime(timestamp)
    
    now = datetime.now()
    if hasattr(timestamp, 'to_pydatetime'):
        timestamp = timestamp.to_pydatetime()
    
    delta = now - timestamp
    
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return "刚刚"
    elif seconds < 3600:
        return f"{int(seconds / 60)} 分钟前"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} 小时前"
    elif seconds < 2592000:
        return f"{int(seconds / 86400)} 天前"
    elif seconds < 31536000:
        return f"{int(seconds / 2592000)} 个月前"
    else:
        return f"{int(seconds / 31536000)} 年前"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 除数为零时的默认值
        
    Returns:
        除法结果或默认值
    """
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    限制数值范围
    
    Args:
        value: 输入值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        限制后的值
    """
    return max(min_value, min(max_value, value))
