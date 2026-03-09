"""
AI Operator System - 自動操作瀏覽器與電腦
"""
from browser.playwright_controller import BrowserController, get_browser, close_browser
from vision.ocr_engine import read_text, detect_elements
from system.mouse_control import click, type_text, press_key, hotkey, scroll
import sys
import os

# 確保路徑正確
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

__version__ = "1.0.0"

__all__ = [
    'BrowserController',
    'get_browser', 
    'close_browser',
    'read_text',
    'detect_elements',
    'click',
    'type_text', 
    'press_key',
    'hotkey',
    'scroll',
]

if __name__ == "__main__":
    print("AI Operator System v1.0")
    print("可用模組:")
    print("  - BrowserController: 瀏覽器控制")
    print("  - read_text(): OCR 文字辨識")
    print("  - click(): 滑鼠點擊")
    print("  - type_text(): 鍵盤輸入")
