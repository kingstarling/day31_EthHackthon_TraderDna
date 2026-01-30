# 🧬 TraderDNA - Smart Money 体检中心

> **"在你跟单之前，先看看这个钱包的「基因报告」"**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 项目简介

TraderDNA 是一个专为 ETH 黑客松打造的 Smart Money 分析工具。与 GMGN 等"发现层"工具不同，TraderDNA 专注于**"验证层"**——帮助用户判断一个钱包是真正的大神，还是只是运气好。

### 核心功能

| 功能 | 描述 |
|------|------|
| 🧮 **Alpha/Beta 分离** | 区分真实投资能力与市场跟随 |
| 📉 **时间衰减分析** | 发现"当年勇"型选手 |
| 🛡️ **风险指标计算** | 夏普比率、最大回撤、盈亏比等 |
| 🏷️ **行为标签系统** | 💎钻石手、🧻纸手、🎰赌徒等 |
| 🤖 **AI 分析师评语** | GPT-4 生成投资建议 |

## 🚀 快速开始

### 1. 克隆项目

```bash
cd day31/traderdna
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Keys
```

### 5. 启动应用

```bash
streamlit run app.py
```

访问 http://localhost:8501 即可使用。

## 📁 项目结构

```
traderdna/
├── app.py                 # Streamlit 主入口
├── requirements.txt       # Python 依赖
├── config.py              # API 配置
├── .env.example           # 环境变量示例
├── README.md              # 项目文档
│
├── data/                  # 数据层
│   ├── fetcher.py         # API 数据获取
│   └── processor.py       # 数据清洗处理
│
├── analysis/              # 分析引擎
│   ├── alpha_beta.py      # Alpha/Beta 分离
│   ├── time_decay.py      # 时间衰减分析
│   ├── risk_metrics.py    # 风险指标计算
│   ├── behavior_tags.py   # 行为标签生成
│   └── ai_summary.py      # AI 评语生成
│
├── visualization/         # 可视化层
│   ├── charts.py          # Plotly 图表
│   └── report_card.py     # 报告卡片组件
│
└── utils/                 # 工具函数
    └── helpers.py         # 通用工具
```

## 🔧 API 配置

需要配置以下 API Keys：

| API | 用途 | 获取地址 |
|-----|------|---------|
| Dune API | 链上交易历史 | https://dune.com/settings/api |
| CoinGecko API | 价格数据 | https://www.coingecko.com/en/api |
| OpenAI API | AI 评语生成 | https://platform.openai.com/api-keys |

## 📊 核心分析模块

### Alpha/Beta 分离

```python
from analysis.alpha_beta import calculate_alpha_beta

result = calculate_alpha_beta(wallet_returns, eth_returns)
print(f"Alpha 占比: {result['alpha_pct']:.1f}%")
print(f"Beta 占比: {result['beta_pct']:.1f}%")
```

### 时间衰减分析

```python
from analysis.time_decay import time_decay_analysis

result = time_decay_analysis(trades_df)
print(f"全周期胜率: {result['all_time']['win_rate']:.1%}")
print(f"近30天胜率: {result['30d']['win_rate']:.1%}")
```

### 风险指标

```python
from analysis.risk_metrics import calculate_risk_metrics

metrics = calculate_risk_metrics(returns_series)
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {metrics['max_drawdown']:.1%}")
```

## 🎯 Demo Day Pitch

```
"大家好，我做的项目叫 TraderDNA。

【问题】
每个人都想跟单 Smart Money，但问题是——
这个钱包真的牛吗？还是只是运气好？

【演示】
用 TraderDNA 分析后你会发现：
- 65% 的收益来自 Beta，跟着大盘涨
- 80% 的收益来自一笔交易
- 最近 90 天其实亏了 8000 美金

结论：这不是大神，是运气好。

【价值】
GMGN 告诉你「跟谁」，TraderDNA 告诉你「该不该跟」。"
```

## 📝 开发计划

- [x] 项目框架搭建
- [ ] Dune API 集成
- [ ] 完整数据管道
- [ ] 测试用例
- [ ] 部署上线

## 📄 License

MIT License

---

Made with ❤️ for ETH Chiang Mai Hackathon
