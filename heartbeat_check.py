#!/usr/bin/env python3
"""
Heartbeat 額外檢查腳本
檢查瀏覽器、遊戲自動化、系統資源狀態
"""
import os
import subprocess
import json
from pathlib import Path

def check_chrome():
    """檢查 Chrome 瀏覽器狀態"""
    result = {
        "name": "chrome_status",
        "status": "ok",
        "message": ""
    }
    
    # 檢查 Chrome 進程
    try:
        proc = subprocess.run(
            ["pgrep", "-f", "chrome"],
            capture_output=True,
            timeout=5
        )
        if proc.returncode == 0:
            result["message"] = "Chrome 運行中"
        else:
            result["status"] = "warning"
            result["message"] = "Chrome 未運行"
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"檢查失敗: {e}"
    
    # 檢查 Remote Debugging Port
    try:
        proc = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:18800/json"],
            capture_output=True,
            timeout=3
        )
        if proc.returncode == 0:
            result["debug_port"] = "可用"
        else:
            result["debug_port"] = "不可用"
    except:
        result["debug_port"] = "不可用"
    
    return result

def check_game_automation():
    """檢查遊戲自動化腳本"""
    result = {
        "name": "game_automation",
        "status": "ok",
        "message": ""
    }
    
    ai_op_dir = Path.home() / ".openclaw" / "ai-operator"
    
    # 檢查目錄是否存在
    if not ai_op_dir.exists():
        result["status"] = "error"
        result["message"] = "AI Operator 目錄不存在"
        return result
    
    # 檢查關鍵腳本
    scripts = ["game_full_flow.py", "game_test.py", "connect_debug.py"]
    missing = []
    for script in scripts:
        if not (ai_op_dir / script).exists():
            missing.append(script)
    
    if missing:
        result["status"] = "warning"
        result["message"] = f"缺少腳本: {', '.join(missing)}"
    else:
        result["message"] = "所有腳本就緒"
    
    # 檢查虛擬環境
    venv_python = ai_op_dir / "bin" / "python"
    if venv_python.exists():
        result["venv"] = "就緒"
    else:
        result["status"] = "error"
        result["venv"] = "未找到"
    
    # 檢查日誌目錄大小
    logs_dir = ai_op_dir / "logs"
    if logs_dir.exists():
        total_size = sum(
            f.stat().st_size for f in logs_dir.rglob("*") if f.is_file()
        )
        size_mb = total_size / (1024 * 1024)
        result["logs_size_mb"] = round(size_mb, 2)
        if size_mb > 100:
            result["status"] = "warning"
    
    return result

def check_system_resources():
    """檢查系統資源"""
    result = {
        "name": "system_resources",
        "status": "ok",
        "message": ""
    }
    
    # 磁碟空間
    stat = os.statvfs("/")
    free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    result["disk_free_gb"] = round(free_gb, 2)
    
    if free_gb < 1:
        result["status"] = "error"
        result["message"] = f"磁碟空間不足: {free_gb:.1f}GB"
    elif free_gb < 5:
        result["status"] = "warning"
        result["message"] = f"磁碟空間不足: {free_gb:.1f}GB"
    else:
        result["message"] = f"磁碟空間充足: {free_gb:.1f}GB"
    
    # 記憶體
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
            mem_total = int([l for l in lines if l.startswith("MemTotal:")][0].split()[1])
            mem_available = int([l for l in lines if l.startswith("MemAvailable:")][0].split()[1])
            mem_percent = (1 - mem_available / mem_total) * 100
            result["memory_percent"] = round(mem_percent, 1)
            
            if mem_percent > 90:
                result["status"] = "error"
            elif mem_percent > 80:
                result["status"] = "warning"
    except:
        pass
    
    return result

def run_heartbeat_checks():
    """執行所有檢查"""
    print("=" * 50)
    print("Heartbeat 額外檢查")
    print("=" * 50)
    
    checks = []
    
    # 1. Chrome 檢查
    print("\n[1] 檢查 Chrome...")
    chrome = check_chrome()
    print(f"    狀態: {chrome['status']}")
    print(f"    {chrome['message']}")
    checks.append(chrome)
    
    # 2. 遊戲自動化檢查
    print("\n[2] 檢查遊戲自動化...")
    game = check_game_automation()
    print(f"    狀態: {game['status']}")
    print(f"    {game['message']}")
    checks.append(game)
    
    # 3. 系統資源檢查
    print("\n[3] 檢查系統資源...")
    system = check_system_resources()
    print(f"    狀態: {system['status']}")
    print(f"    {system['message']}")
    checks.append(system)
    
    # 總結
    print("\n" + "=" * 50)
    print("檢查結果總結")
    print("=" * 50)
    
    errors = [c for c in checks if c["status"] == "error"]
    warnings = [c for c in checks if c["status"] == "warning"]
    
    if errors:
        print(f"❌ 錯誤: {len(errors)} 項")
        for e in errors:
            print(f"   - {e['name']}: {e['message']}")
    
    if warnings:
        print(f"⚠️  警告: {len(warnings)} 項")
        for w in warnings:
            print(f"   - {w['name']}: {w['message']}")
    
    if not errors and not warnings:
        print("✅ 所有檢查通過")
    
    return {
        "errors": errors,
        "warnings": warnings,
        "all_ok": len(errors) == 0 and len(warnings) == 0
    }

if __name__ == "__main__":
    run_heartbeat_checks()
