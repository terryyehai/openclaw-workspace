"""
AI Browser Agent - 使用 browser-use 自動操作瀏覽器
"""
import os
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

class AIBrowserAgent:
    def __init__(self, model="gpt-4", headless=False):
        self.llm = ChatOpenAI(model=model)
        
        self.browser = Browser(
            config=BrowserConfig(
                headless=headless,
                disable_security=True,
            )
        )
        
    def run(self, task):
        """執行任務"""
        agent = Agent(
            task=task,
            llm=self.llm,
            browser=self.browser
        )
        result = agent.run()
        return result
    
    def close(self):
        """關閉瀏覽器"""
        self.browser.close()

def create_agent(task, model="gpt-4", headless=False):
    """建立 AI 瀏覽器代理"""
    return AIBrowserAgent(model=model, headless=headless)
