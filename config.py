"""
TraderDNA 配置模块

管理所有 API Keys 和默认参数设置
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class Config:
    """配置类 - 管理所有配置项"""
    
    # API Keys
    DUNE_API_KEY: str = os.getenv("DUNE_API_KEY", "")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Dune 配置
    DUNE_BASE_URL: str = "https://api.dune.com/api/v1"
    
    # CoinGecko 配置
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    
    # DefiLlama 配置
    DEFILLAMA_BASE_URL: str = "https://api.llama.fi"
    
    # 分析参数
    DEFAULT_TIME_WINDOWS: tuple = (7, 30, 90, 365)  # 天数
    MIN_TRADES_FOR_ANALYSIS: int = 10
    
    # 风险指标阈值
    SHARPE_GOOD_THRESHOLD: float = 1.5
    SHARPE_EXCELLENT_THRESHOLD: float = 2.0
    MAX_DRAWDOWN_WARNING_THRESHOLD: float = 0.3  # 30%
    MAX_DRAWDOWN_DANGER_THRESHOLD: float = 0.5   # 50%
    
    # 行为标签阈值
    DIAMOND_HANDS_MIN_HOLD_HOURS: int = 7 * 24   # 7天
    PAPER_HANDS_MAX_HOLD_HOURS: int = 24         # 1天
    ONE_HIT_WONDER_THRESHOLD: float = 0.5        # 单笔贡献50%以上
    SUSPICIOUS_TIME_BEFORE_PUMP_MINUTES: int = 60
    HIGH_FREQUENCY_THRESHOLD: int = 10           # 日均交易次数
    LOW_WIN_RATE_THRESHOLD: float = 0.4          # 40%
    
    # AI 配置
    OPENAI_MODEL: str = "gpt-4"
    AI_MAX_TOKENS: int = 500
    
    # 无风险利率（用于夏普比率计算）
    RISK_FREE_RATE: float = 0.04  # 4% 年化
    
    # 多链配置
    CHAIN_CONFIG = {
        "Ethereum": {
            "coingecko_id": "ethereum",
            "dune_query_id": 6619227,
            "currency_symbol": "ETH",
            "explorer_url": "https://etherscan.io/address/",
        },
        "Solana": {
            "coingecko_id": "solana",
            "dune_query_id": 6619482,  # 需用户填入 SOL Query ID
            "currency_symbol": "SOL",
            "explorer_url": "https://solscan.io/account/",
        }
    }

# 全局配置实例
config = Config()
