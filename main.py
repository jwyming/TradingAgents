from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# 从 .env 读取 yfinance 代理配置
use_proxy = os.getenv("USE_YF_PROXY", "false").lower() in ("true", "1", "yes")
if use_proxy:
    proxy_url = os.getenv("YF_PROXY_URL", "http://127.0.0.1:10810")
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url

# Create a custom config
config = DEFAULT_CONFIG.copy()
# config["llm_provider"] = "openrouter"        # 默认 provider（兼容旧配置）
# 可选：分别给 deep/quick 指定不同 provider；未设置则回退到 llm_provider
config["deep_llm_provider"] = "openrouter"
config["quick_llm_provider"] = "openrouter"
# config["deep_think_llm"] = "z-ai/glm-4.5-air:free"  # Use a different model
config["deep_think_llm"] = "nvidia/nemotron-3-super-120b-a12b:free"  # Use a different model
config["quick_think_llm"] = "nvidia/nemotron-3-nano-30b-a3b:free"  # Use a different model
config["max_debate_rounds"] = 3  # Increase debate rounds

# Configure data vendors (default uses yfinance, no extra API keys needed)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: alpha_vantage, yfinance
    "technical_indicators": "yfinance",      # Options: alpha_vantage, yfinance
    "fundamental_data": "yfinance",          # Options: alpha_vantage, yfinance
    "news_data": "yfinance",                 # Options: alpha_vantage, yfinance
}

# Output language
config["output_language"] = "zh"

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("GOOGL", "2026-03-16")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
