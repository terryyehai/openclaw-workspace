"""
System Control - 滑鼠與鍵盤控制
"""
import pyautogui
import time

# 設定安全模式
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def click(x, y, button='left'):
    """點擊"""
    pyautogui.moveTo(x, y)
    pyautogui.click(button=button)
    
def double_click(x, y):
    """雙擊"""
    pyautogui.moveTo(x, y)
    pyautogui.doubleClick()

def right_click(x, y):
    """右鍵點擊"""
    pyautogui.moveTo(x, y)
    pyautogui.rightClick()

def type_text(text):
    """輸入文字"""
    pyautogui.write(text)

def press_key(key):
    """按鍵"""
    pyautogui.press(key)

def hotkey(*keys):
    """組合鍵"""
    pyautogui.hotkey(*keys)

def scroll(clicks):
    """滾動"""
    pyautogui.scroll(clicks)

def get_position():
    """取得目前滑鼠位置"""
    return pyautogui.position()

def move_to(x, y, duration=0.2):
    """移動滑鼠"""
    pyautogui.moveTo(x, y, duration=duration)

def drag_to(x, y, duration=0.5):
    """拖曳"""
    pyautogui.dragTo(x, y, duration=duration)
