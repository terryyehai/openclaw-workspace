"""
AI Operator System - 主模組
整合所有自我進化功能
"""
from monitoring.operation_logger import logger, monitor, OperationLogger, PerformanceMonitor
from strategies.strategy_optimizer import optimizer, selector_optimizer, StrategyOptimizer, SelectorOptimizer
from ml.self_optimizer import predictor, recommender, OperationPredictor, OperationRecommender
from self_update.self_corrector import corrector, update_manager, health_checker, SelfCorrector, AutoUpdateManager, HealthChecker
from evaluation.evolution_engine import evolution_engine, PerformanceEvaluator, IterationController, EvolutionEngine

__version__ = "1.0.0"

__all__ = [
    # 監測
    'logger',
    'monitor', 
    'OperationLogger',
    'PerformanceMonitor',
    
    # 策略優化
    'optimizer',
    'selector_optimizer',
    'StrategyOptimizer',
    'SelectorOptimizer',
    
    # 機器學習
    'predictor',
    'recommender',
    'OperationPredictor',
    'OperationRecommender',
    
    # 自我修正
    'corrector',
    'update_manager', 
    'health_checker',
    'SelfCorrector',
    'AutoUpdateManager',
    'HealthChecker',
    
    # 進化引擎
    'evolution_engine',
    'PerformanceEvaluator',
    'IterationController',
    'EvolutionEngine',
]

def init_system():
    """初始化系統"""
    print("=" * 50)
    print("AI Operator System v1.0 - 自我進化系統")
    print("=" * 50)
    
    # 健康檢查
    health = health_checker.run_checks()
    print(f"\n健康狀態: {health['overall_health']}%")
    for check in health["checks"]:
        print(f"  - {check['name']}: {check['status']} ({check['message']})")
    
    # 當前策略
    strategy = optimizer.get_strategy()
    print(f"\n當前策略版本: {strategy['version']}")
    print(f"  - 點擊等待: {strategy['click_wait_ms']}ms")
    print(f"  - 重試次數: {strategy['retry_count']}")
    
    # 最近的迭代
    from evaluation.evolution_engine import IterationController
    it_ctrl = IterationController()
    latest = it_ctrl.get_latest_iteration()
    if latest:
        print(f"\n最近迭代: #{latest['id']} ({latest['status']})")
    
    print("\n" + "=" * 50)
    
    return {
        "health": health,
        "strategy": strategy,
        "latest_iteration": latest
    }

def run_evolution_cycle():
    """運行進化週期"""
    print("\n開始執行自我進化...")
    
    results = evolution_engine.run_self_optimization()
    
    print(f"\n進化完成!")
    print(f"  - 分析日誌: {results['logs_analyzed']}")
    print(f"  - 策略已更新: {results['strategy_updated']}")
    print(f"  - ML模型已更新: {results['ml_model_updated']}")
    print(f"  - 錯誤修正: {results['corrections_applied']}")
    
    return results

if __name__ == "__main__":
    init_system()
