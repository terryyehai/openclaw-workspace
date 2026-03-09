"""
策略調整與規則優化系統
根據歷史操作自動調整策略
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class StrategyOptimizer:
    def __init__(self, strategy_dir="~/.openclaw/ai-operator/strategies"):
        self.strategy_dir = Path(os.path.expanduser(strategy_dir))
        self.strategy_dir.mkdir(parents=True, exist_ok=True)
        self.strategy_file = self.strategy_dir / "current_strategy.json"
        self.history_file = self.strategy_dir / "strategy_history.json"
        
        # 預設策略
        self.default_strategy = {
            "version": "1.0",
            "click_wait_ms": 1000,
            "fill_wait_ms": 500,
            "page_load_timeout_ms": 30000,
            "retry_count": 3,
            "retry_delay_ms": 2000,
            "selectors_priority": ["aria-label", "data-testid", "id", "class", "xpath"],
            "error_handling": {
                "popup_action": "dismiss",
                "timeout_action": "retry",
                "error_action": "screenshot_and_continue"
            },
            "adaptive": {
                "enabled": True,
                "learn_from_errors": True,
                "adjust_wait_times": True
            }
        }
        
        self.load_strategy()
        
    def load_strategy(self):
        """載入當前策略"""
        if self.strategy_file.exists():
            with open(self.strategy_file, "r") as f:
                self.current_strategy = json.load(f)
        else:
            self.current_strategy = self.default_strategy.copy()
            self.save_strategy()
            
    def save_strategy(self):
        """儲存策略"""
        with open(self.strategy_file, "w", encoding="utf-8") as f:
            json.dump(self.current_strategy, f, indent=2, ensure_ascii=False)
            
    def optimize_from_history(self, logs_dir):
        """根據歷史記錄優化策略"""
        # 讀取最近的操作日誌
        log_files = sorted(Path(logs_dir).glob("operations_*.jsonl"))
        if not log_files:
            return
            
        recent_logs = []
        for log_file in log_files[-7:]:  # 最近7天
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        recent_logs.append(json.loads(line))
                    except:
                        pass
        
        if not recent_logs:
            return
            
        # 分析失敗模式
        failures = [l for l in recent_logs if l["status"] == "failure"]
        timeouts = [l for l in recent_logs if l["status"] == "timeout"]
        
        # 調整等待時間
        if self.current_strategy["adaptive"]["adjust_wait_times"]:
            avg_success_duration = sum(
                l["duration_ms"] for l in recent_logs 
                if l["status"] == "success" and l.get("duration_ms", 0) > 0
            ) / max(len([l for l in recent_logs if l["status"] == "success"]), 1)
            
            if avg_success_duration > self.current_strategy["click_wait_ms"]:
                # 自動增加等待時間
                self.current_strategy["click_wait_ms"] = int(avg_success_duration * 1.2)
                
        # 調整重試次數
        if len(failures) > 5:
            self.current_strategy["retry_count"] = min(5, self.current_strategy["retry_count"] + 1)
            
        # 記錄優化歷史
        self.save_strategy_history(len(recent_logs), len(failures), len(timeouts))
        
    def save_strategy_history(self, total_ops, failures, timeouts):
        """儲存策略歷史"""
        history = []
        if self.history_file.exists():
            with open(self.history_file, "r") as f:
                history = json.load(f)
                
        history.append({
            "timestamp": datetime.now().isoformat(),
            "total_operations": total_ops,
            "failures": failures,
            "timeouts": timeouts,
            "success_rate": round((total_ops - failures - timeouts) / max(total_ops, 1) * 100, 2),
            "strategy_version": self.current_strategy["version"],
            "click_wait_ms": self.current_strategy["click_wait_ms"],
            "retry_count": self.current_strategy["retry_count"]
        })
        
        # 只保留最近30筆
        history = history[-30:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            
    def get_strategy(self):
        """取得當前策略"""
        return self.current_strategy
    
    def update_strategy(self, updates):
        """更新策略"""
        self.current_strategy.update(updates)
        self.current_strategy["version"] = self.bump_version()
        self.save_strategy()
        
    def bump_version(self):
        """版本號遞增"""
        parts = self.current_strategy["version"].split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)


class SelectorOptimizer:
    """選擇器優化器"""
    
    def __init__(self):
        self.selector_stats = {}  # selector -> success_rate
        
    def record_selector_result(self, selector, success):
        """記錄選擇器結果"""
        if selector not in self.selector_stats:
            self.selector_stats[selector] = {"success": 0, "failure": 0}
            
        if success:
            self.selector_stats[selector]["success"] += 1
        else:
            self.selector_stats[selector]["failure"] += 1
            
    def get_best_selector(self, selectors):
        """取得最佳選擇器"""
        best = None
        best_rate = -1
        
        for sel in selectors:
            if sel in self.selector_stats:
                stats = self.selector_stats[sel]
                total = stats["success"] + stats["failure"]
                rate = stats["success"] / max(total, 1)
                
                if rate > best_rate:
                    best_rate = rate
                    best = sel
                    
        return best or selectors[0] if selectors else None
    
    def suggest_selectors(self, element_info):
        """根據元素資訊建議選擇器"""
        suggestions = []
        
        if "aria-label" in element_info:
            suggestions.append(f'[aria-label="{element_info["aria-label"]}"]')
        if "data-testid" in element_info:
            suggestions.append(f'[data-testid="{element_info["data-testid"]}"]')
        if "id" in element_info:
            suggestions.append(f'#{element_info["id"]}')
        if "class" in element_info:
            cls = element_info["class"].split()[0]
            suggestions.append(f'.{cls}')
            
        return suggestions


# 全域實例
optimizer = StrategyOptimizer()
selector_optimizer = SelectorOptimizer()
