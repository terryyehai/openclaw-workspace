#!/usr/bin/env python3
"""
Telegram 訊息重試機制
監控日誌中的失敗訊息並重試發送
"""
import json
import os
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path

LOG_FILE = "/tmp/openclaw/openclaw-2026-03-18.log"
FAILED_MESSAGES_LOG = "/home/terry/.openclaw/workspace-dev/report/logs/telegram_retry.jsonl"

def get_recent_telegram_errors():
    """取得最近失敗的 Telegram 訊息"""
    errors = []
    if not Path(LOG_FILE).exists():
        return errors
    
    # 讀取最近 1 小時的日誌
    cutoff = datetime.now() - timedelta(hours=1)
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if "telegram" in str(data).lower() and "failed" in str(data).lower():
                    # 解析時間
                    time_str = data.get("_meta", {}).get("time", "")
                    if time_str:
                        try:
                            log_time = datetime.fromisoformat(time_str.replace("+08:00", ""))
                            if log_time > cutoff:
                                errors.append(data)
                        except:
                            pass
            except:
                pass
    
    return errors

def retry_message(chat_id, text):
    """重試發送訊息"""
    # 使用 curl 直接呼叫 Telegram API
    token = "8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-d", f"chat_id={chat_id}",
        "-d", f"text={text}",
        "-d", "parse_mode=Markdown"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0

def main():
    print(f"[{datetime.now().isoformat()}] Telegram 重試檢查開始")
    
    # 確保日誌目錄存在
    Path(FAILED_MESSAGES_LOG).parent.mkdir(parents=True, exist_ok=True)
    
    errors = get_recent_telegram_errors()
    
    if errors:
        print(f"發現 {len(errors)} 個失敗訊息")
        for err in errors:
            print(f"  - {err}")
    else:
        print("無失敗訊息")
    
    # 檢查是否有需要重試的訊息
    # 這裡可以擴展為從 FAILED_MESSAGES_LOG 讀取並重試
    
    print(f"[{datetime.now().isoformat()}] 檢查完成")

if __name__ == "__main__":
    main()
