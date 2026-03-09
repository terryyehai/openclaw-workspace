"""
自我評估與迭代系統
持續收集數據、分析問題、優化策略
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class PerformanceEvaluator:
    """效能評估器"""
    
    def __init__(self, data_dir="~/.openclaw/ai-operator/data"):
        self.data_dir = Path(os.path.expanduser(data_dir))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate_session(self, session_id):
        """評估單次會話"""
        # 讀取會話日誌
        log_file = Path(f"~/.openclaw/ai-operator/logs/operations_{session_id}.jsonl")
        if not log_file.exists():
            return None
            
        operations = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    operations.append(json.loads(line))
                except:
                    pass
                    
        if not operations:
            return None
            
        # 計算指標
        total = len(operations)
        successes = sum(1 for op in operations if op.get("status") == "success")
        failures = sum(1 for op in operations if op.get("status") == "failure")
        timeouts = sum(1 for op in operations if op.get("status") == "timeout")
        
        # 平均響應時間
        durations = [op.get("duration_ms", 0) for op in operations if op.get("duration_ms", 0) > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # 操作類型統計
        op_types = {}
        for op in operations:
            op_type = op.get("operation_type", "unknown")
            op_types[op_type] = op_types.get(op_type, 0) + 1
            
        return {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "total_operations": total,
            "successes": successes,
            "failures": failures,
            "timeouts": timeouts,
            "success_rate": round(successes / total * 100, 2) if total > 0 else 0,
            "avg_response_time_ms": round(avg_duration, 2),
            "operation_types": op_types
        }
        
    def generate_report(self, days=7):
        """生成效能報告"""
        log_dir = Path("~/.openclaw/ai-operator/logs")
        
        # 取得最近7天的日誌
        sessions = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            result = self.evaluate_session(date)
            if result:
                sessions.append(result)
                
        if not sessions:
            return {"message": "沒有足夠數據生成報告"}
            
        # 匯總統計
        total_ops = sum(s["total_operations"] for s in sessions)
        total_successes = sum(s["successes"] for s in sessions)
        total_failures = sum(s["failures"] for s in sessions)
        avg_response = sum(s["avg_response_time_ms"] for s in sessions) / len(sessions)
        
        return {
            "period_days": days,
            "total_sessions": len(sessions),
            "total_operations": total_ops,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "overall_success_rate": round(total_successes / total_ops * 100, 2) if total_ops > 0 else 0,
            "avg_response_time_ms": round(avg_response, 2),
            "sessions": sessions,
            "generated_at": datetime.now().isoformat()
        }


class IterationController:
    """迭代控制器"""
    
    def __init__(self):
        self.iteration_file = Path("~/.openclaw/ai-operator/data/iterations.json")
        self.iterations = []
        
        if self.iteration_file.exists():
            with open(self.iteration_file, "r") as f:
                self.iterations = json.load(f)
                
    def start_iteration(self, trigger_reason):
        """開始新迭代"""
        iteration = {
            "id": len(self.iterations) + 1,
            "start_time": datetime.now().isoformat(),
            "trigger_reason": trigger_reason,
            "status": "in_progress",
            "changes": [],
            "results": {}
        }
        
        self.iterations.append(iteration)
        self.save()
        
        return iteration
        
    def record_change(self, iteration_id, change_type, description, details):
        """記錄變更"""
        for it in self.iterations:
            if it["id"] == iteration_id:
                it["changes"].append({
                    "type": change_type,
                    "description": description,
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                })
                break
                
        self.save()
        
    def complete_iteration(self, iteration_id, results):
        """完成迭代"""
        for it in self.iterations:
            if it["id"] == iteration_id:
                it["status"] = "completed"
                it["end_time"] = datetime.now().isoformat()
                it["results"] = results
                break
                
        self.save()
        
    def save(self):
        """儲存"""
        with open(self.iteration_file, "w") as f:
            json.dump(self.iterations, f, indent=2)
            
    def get_latest_iteration(self):
        """取得最新迭代"""
        if self.iterations:
            return self.iterations[-1]
        return None


class EvolutionEngine:
    """進化引擎 - 整合所有自我進化功能"""
    
    def __init__(self):
        from monitoring.operation_logger import logger, monitor
        from strategies.strategy_optimizer import optimizer
        from ml.self_optimizer import predictor, recommender
        from self_update.self_corrector import corrector, health_checker
        
        self.logger = logger
        self.monitor = monitor
        self.optimizer = optimizer
        self.predictor = predictor
        self.recommender = recommender
        self.corrector = corrector
        self.health_checker = health_checker
        
        self.evaluator = PerformanceEvaluator()
        self.iteration = IterationController()
        
    def run_health_check(self):
        """執行健康檢查"""
        return self.health_checker.run_checks()
        
    def run_self_optimization(self):
        """執行自我優化"""
        # 開始新迭代
        iteration = self.iteration.start_iteration("scheduled_optimization")
        
        # 1. 分析歷史數據
        logs = self.logger.get_recent_operations(limit=100)
        
        # 2. 優化策略
        self.optimizer.optimize_from_history(
            str(Path("~/.openclaw/ai-operator/logs"))
        )
        
        self.iteration.record_change(
            iteration["id"],
            "strategy_optimization",
            "根據歷史數據優化策略",
            self.optimizer.get_strategy()
        )
        
        # 3. 機器學習訓練
        for log in logs:
            if log.get("status") in ["success", "failure"]:
                # 簡化的學習過程
                state = "page_loaded"  # 假設狀態
                action = log.get("operation_type", "unknown")
                reward = 1.0 if log.get("status") == "success" else -1.0
                
                self.predictor.record_outcome(state, action, reward)
                
        # 儲存模型
        self.predictor.save_model()
        
        self.iteration.record_change(
            iteration["id"],
            "ml_model_update",
            "更新機器學習模型",
            {"model_version": "updated"}
        )
        
        # 4. 錯誤分析與修正
        error_patterns = self.corrector.analyze_errors(logs)
        corrections = self.corrector.generate_corrections(error_patterns)
        
        for correction in corrections:
            self.corrector.apply_correction(correction)
            
        self.iteration.record_change(
            iteration["id"],
            "error_corrections",
            "修正錯誤模式",
            {"corrections_applied": len(corrections)}
        )
        
        # 完成迭代
        results = {
            "logs_analyzed": len(logs),
            "strategy_updated": True,
            "ml_model_updated": True,
            "corrections_applied": len(corrections)
        }
        
        self.iteration.complete_iteration(iteration["id"], results)
        
        return results
        
    def generate_evolution_report(self):
        """生成進化報告"""
        health = self.run_health_check()
        performance = self.evaluator.generate_report(days=7)
        latest_iter = self.iteration.get_latest_iteration()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health": health,
            "performance": performance,
            "latest_iteration": latest_iter,
            "current_strategy": self.optimizer.get_strategy()
        }


# 全域實例
evolution_engine = EvolutionEngine()
