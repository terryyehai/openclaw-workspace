#!/usr/bin/env python3
"""
Airtest 基本功能測試
"""
import sys
import os

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

def test_airtest():
    """測試 Airtest 基本功能"""
    print("=" * 60)
    print("Airtest 基本功能測試")
    print("=" * 60)
    
    # 1. 檢查版本
    print("\n[1] 檢查 Airtest 版本...")
    from airtest import __version__
    print(f"   ✓ Airtest {__version__}")
    
    # 2. 檢查模組
    print("\n[2] 檢查可用模組...")
    from airtest.core.api import (
        touch, swipe, text, snapshot, 
        assert_exists, wait, find_all, 
        connect_device, device, init_device
    )
    print("   ✓ 所有核心模組可用")
    
    # 3. 列出可用功能
    print("\n[3] 可用功能:")
    funcs = [
        ("touch()", "觸控點擊"),
        ("swipe()", "滑動"),
        ("text()", "輸入文字"),
        ("snapshot()", "截圖"),
        ("assert_exists()", "斷言存在"),
        ("wait()", "等待"),
        ("find_all()", "查找所有"),
        ("connect_device()", "連接設備"),
    ]
    for name, desc in funcs:
        print(f"   - {name}: {desc}")
    
    # 4. 設備連接選項
    print("\n[4] 支援的設備類型:")
    print("   Android: android:///")
    print("   iOS: ios:///")  
    print("   Windows: Windows:///")
    print("   Chrome: chrome:///")
    
    print("\n" + "=" * 60)
    print("✓ Airtest 安裝成功!")
    print("=" * 60)
    
    print("""
使用範例:

# 連接 Android
connect_device("android:///")

# 影像辨識點擊
touch(Template("spin_button.png"))

# 等待並驗證
wait(Template("loading.png"))
assert_exists(Template("win.png"))
""")

if __name__ == "__main__":
    test_airtest()
