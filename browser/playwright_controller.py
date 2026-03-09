"""
Browser Controller - 使用 Playwright 控制瀏覽器
"""
from playwright.sync_api import sync_playwright
import os

class BrowserController:
    def __init__(self, headless=False):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
    def open(self, url):
        """打開網頁"""
        self.page.goto(url)
        return self.page
        
    def click(self, selector):
        """點擊元素"""
        self.page.click(selector)
        
    def fill(self, selector, text):
        """填入文字"""
        self.page.fill(selector, text)
        
    def screenshot(self, path="screen.png"):
        """截圖"""
        self.page.screenshot(path=path)
        return path
    
    def wait(self, timeout=3000):
        """等待"""
        self.page.wait_for_timeout(timeout)
        
    def close(self):
        """關閉瀏覽器"""
        self.browser.close()
        self.playwright.stop()

# 預設瀏覽器實例
_default_browser = None

def get_browser(headless=False):
    """取得瀏覽器實例"""
    global _default_browser
    if _default_browser is None:
        _default_browser = BrowserController(headless=headless)
    return _default_browser

def close_browser():
    """關閉瀏覽器"""
    global _default_browser
    if _default_browser:
        _default_browser.close()
        _default_browser = None
