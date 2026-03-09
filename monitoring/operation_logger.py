"""
自我監測與數據收集系統
記錄每次操作的結果、效能指標、錯誤日誌
"""
import json
import time
import os
from datetime import datetime
from pathlib import Path

class OperationLogger:
    def __init__(self, log_dir="~/.openclaw/ai-operator/logs"):
        self.log_dir = Path(os.path.expanduser(log_dir))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = datetime.now().strftime("%Y%m%d")
        
    def log_operation(self, operation_type, details, status="success", 
                      duration_ms=0, metadata=None):
        """記錄操作"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "status": status,  # success, failure, timeout
            "duration_ms": duration_ms,
            "details": details,
            "metadata": metadata or {}
        }
        
        # 寫入日誌檔
        log_file = self.log_dir / f"operations_{self.current_session}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        return log_entry
    
    def log_click(self, selector, x, y, status="success", duration_ms=0):
        """記錄點擊操作"""
        return self.log_operation(
            "click",
            {"selector": selector, "x": x, "y": y},
            status,
            duration_ms
        )
    
    def log_fill(self, selector, value_length, status="success", duration_ms=0):
        """記錄輸入操作"""
        return self.log_operation(
            "fill",
            {"selector": selector, "value_length": value_length},
            status,
            duration_ms
        )
    
    def log_navigation(self, url, load_time_ms, status="success"):
        """記錄導航"""
        return self.log_operation(
            "navigate",
            {"url": url},
            status,
            load_time_ms
        )
    
    def log_error(self, operation, error_message, details=None):
        """記錄錯誤"""
        return self.log_operation(
            "error",
            {"operation": operation, "error": error_message, "details": details},
            "failure"
        )
    
    def get_session_stats(self):
        """取得當前會話統計"""
        log_file = self.log_dir / f"operations_{self.current_session}.jsonl"
        if not log_file.exists():
            return {"total": 0, "success": 0, "failure": 0, "success_rate": 0}
        
        stats = {"total": 0, "success": 0, "failure": 0, "timeout": 0}
        
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    stats["total"] += 1
                    if entry["status"] == "success":
                        stats["success"] += 1
                    elif entry["status"] == "timeout":
                        stats["timeout"] += 1
                    else:
                        stats["failure"] += 1
                except:
                    pass
        
        if stats["total"] > 0:
            stats["success_rate"] = round(stats["success"] / stats["total"] * 100, 2)
        else:
            stats["success_rate"] = 0
            
        return stats
    
    def get_recent_operations(self, limit=10):
        """取得最近操作"""
        log_file = self.log_dir / f"operations_{self.current_session}.jsonl"
        if not log_file.exists():
            return []
        
        operations = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    operations.append(json.loads(line))
                except:
                    pass
        return operations[-limit:][::-1]


class PerformanceMonitor:
    """效能監控"""
    
    def __init__(self):
        self.metrics = {
            "page_load_times": [],
            "click_response_times": [],
            "error_count": 0,
            "retry_count": 0
        }
        
    def record_page_load(self, url, load_time_ms):
        """記錄頁面載入時間"""
        self.metrics["page_load_times"].append({
            "url": url,
            "time_ms": load_time_ms,
            "timestamp": datetime.now().isoformat()
        })
        
    def record_click_response(self, response_time_ms):
        """記錄點擊響應時間"""
        self.metrics["click_response_times"].append(response_time_ms)
        
    def record_error(self):
        """記錄錯誤"""
        self.metrics["error_count"] += 1
        
    def record_retry(self):
        """記錄重試"""
        self.metrics["retry_count"] += 1
        
    def get_average_load_time(self):
        """取得平均載入時間"""
        if not self.metrics["page_load_times"]:
            return 0
        times = [p["time_ms"] for p in self.metrics["page_load_times"]]
        return sum(times) / len(times)
    
    def get_metrics_summary(self):
        """取得指標摘要"""
        return {
            "avg_page_load_time": self.get_average_load_time(),
            "avg_click_response": sum(self.metrics["click_response_times"]) / 
                                  len(self.metrics["click_response_times"]) if self.metrics["click_response_times"] else 0,
            "total_errors": self.metrics["error_count"],
            "total_retries": self.metrics["retry_count"],
            "operations_count": len(self.metrics["page_load_times"])
        }


# 全域實例
logger = OperationLogger()
monitor = PerformanceMonitor()
