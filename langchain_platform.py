#!/usr/bin/env python3
"""
LangChain 遊戲自動化平台
使用 LangChain Agent 控制遊戲測試
"""
import os
import sys
import json
import time
from datetime import datetime

# 設定 API Key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

# 導入現有模組
from monitoring.operation_logger import logger
from strategies.strategy_optimizer import optimizer
from ml.self_optimizer import predictor

class GameTestingPlatform:
    """遊戲測試平台"""
    
    def __init__(self, model="gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0.7)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
    def _create_tools(self):
        """建立工具"""
        
        def browser_navigate(url: str) -> str:
            """導航到指定網址"""
            # 這裡調用 Selenium/Playwright
            return f"已導航到: {url}"
        
        def click_element(element: str) -> str:
            """點擊元素"""
            return f"已點擊: {element}"
        
        def take_screenshot() -> str:
            """截圖"""
            return "截圖已完成"
        
        def analyze_result() -> str:
            """分析遊戲結果"""
            return "分析完成"
        
        def log_operation(operation: str, result: str) -> str:
            """記錄操作"""
            logger.log_operation(operation, {"result": result})
            return f"已記錄: {operation}"
        
        tools = [
            Tool(
                name="browser_navigate",
                func=browser_navigate,
                description="導航到指定網址，例如: browser_navigate('https://example.com')"
            ),
            Tool(
                name="click_element",
                func=click_element,
                description="點擊頁面元素，例如: click_element('SPIN按鈕')"
            ),
            Tool(
                name="take_screenshot",
                func=take_screenshot,
                description="截取當前頁面"
            ),
            Tool(
                name="analyze_result",
                func=analyze_result,
                description="分析遊戲結果（贏/輸/餘額變化）"
            ),
            Tool(
                name="log_operation",
                func=log_operation,
                description="記錄操作日誌，例如: log_operation('SPIN', '贏30元')"
            ),
        ]
        
        return tools
    
    def _create_agent(self):
        """建立 Agent"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一個專業的遊戲測試工程師。
            
            你的職責是：
            1. 自動化執行遊戲測試
            2. 記錄每次操作的結果
            3. 分析遊戲數據（贏/輸/餘額變化）
            4. 優化測試策略
            
            遊戲測試流程：
            1. 登入遊戲系統
            2. 選擇遊戲
            3. 點擊 SPIN
            4. 記錄結果
            5. 重複直到完成測試
            
            請使用工具來完成任務。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
    
    def run_test(self, task: str):
        """執行測試任務"""
        print("=" * 60)
        print("LangChain 遊戲測試平台")
        print("=" * 60)
        print(f"\n任務: {task}\n")
        
        result = self.agent.invoke({"input": task})
        
        print("\n" + "=" * 60)
        print("執行結果")
        print("=" * 60)
        print(result["output"])
        
        return result
    
    def run_spin_cycle(self, count: int = 10):
        """執行 SPIN 循環"""
        
        task = f"""請執行以下遊戲測試：
        
        1. 前往遊戲測試工具
        2. 登入（帳號：PHP123456789，遊戲：230001）
        3. 進入遊戲 Golden Mahjong
        4. 執行 {count} 次 SPIN
        5. 每次 SPIN 後記錄結果（餘額、贏/輸）
        6. 統計總結果
        
        請使用 log_operation 工具記錄每次結果。"""
        
        return self.run_test(task)


# 測試
if __name__ == "__main__":
    platform = GameTestingPlatform()
    
    # 簡單測試
    result = platform.run_test("請說 '你好，我是遊戲測試工程師'")
