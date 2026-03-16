import time
import uuid
import uvicorn
from fastapi import FastAPI, BackgroundTasks

app = FastAPI(title="Trading Agent API")

# 用于在内存中临时存储任务状态和结果
task_store = {}

def run_agent_analysis(task_id: str, symbol: str, date_str: str):
    """
    后台真正执行耗时分析的函数
    """
    try:
        print(f"[Task {task_id}] 开始对 {symbol} 进行深度 AI 推演，基准日期: {date_str}...")

        # ==========================================================
        # 在这里调用你 TradingAgent 原本的分析逻辑
        # 例如:
        # from your_agent_module import analyze
        # final_signal = analyze(symbol, date_str)
        # ==========================================================
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

        # Output language
        config["output_language"] = "zh"

        # Initialize with custom config
        ta = TradingAgentsGraph(debug=True, config=config)

        # forward propagate
        _, decision = ta.propagate(symbol, date_str)
        print(decision)
        # ==========================================================


        # 下面这行只是模拟耗时，实装时请删除
        # time.sleep(600)

        # AI 给出的结果
        final_signal = decision

        # 分析结束，更新状态和结果
        task_store[task_id] = {
            "status": "completed",
            "signal": final_signal
        }
        print(f"[Task {task_id}] {symbol} 分析完毕，结论: {final_signal}")

    except Exception as e:
        print(f"[Task {task_id}] 分析失败: {e}")
        task_store[task_id] = {
            "status": "completed",
            "signal": "HOLD"  # 报错则默认保守持有
        }

# 🌟 修改点 1：补齐 /agent 前缀
@app.post("/agent/analyze")
def submit_analysis_task(symbol: str, date: str, background_tasks: BackgroundTasks):
    """
    接收分析请求，立即返回 task_id，并将耗时任务放入后台执行
    """
    task_id = str(uuid.uuid4())
    task_store[task_id] = {
        "status": "processing",
        "signal": None
    }

    # 丢入后台任务队列
    background_tasks.add_task(run_agent_analysis, task_id, symbol, date)

    return {"task_id": task_id, "message": f"{symbol} 分析任务已提交后台"}

# 🌟 修改点 2：补齐 /agent 前缀
@app.get("/agent/result/{task_id}")
def get_task_result(task_id: str):
    """
    策略端用来轮询查询结果的接口
    """
    task_info = task_store.get(task_id)
    if not task_info:
        # FastAPI 默认会把 return dict 转化为 JSON
        return {"error": "Task ID not found"}

    return task_info

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)