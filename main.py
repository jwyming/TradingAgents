from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

os.environ['HTTP_PROXY'] = "http://127.0.0.1:10810"
os.environ['HTTPS_PROXY'] = "http://127.0.0.1:10810"

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openrouter"        # openai, google, anthropic, xai, openrouter, ollama
config["deep_think_llm"] = "z-ai/glm-4.5-air:free"  # Use a different model
config["quick_think_llm"] = "nvidia/nemotron-3-nano-30b-a3b:free"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance, no extra API keys needed)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: alpha_vantage, yfinance
    "technical_indicators": "yfinance",      # Options: alpha_vantage, yfinance
    "fundamental_data": "yfinance",          # Options: alpha_vantage, yfinance
    "news_data": "yfinance",                 # Options: alpha_vantage, yfinance
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("TSLA", "2026-03-14")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
