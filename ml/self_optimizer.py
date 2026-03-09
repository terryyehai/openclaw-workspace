"""
機器學習自我優化系統
基於強化學習的決策優化
"""
import json
import os
import random
from pathlib import Path
from datetime import datetime
import numpy as np

class QLearningAgent:
    """Q-Learning 強化學習代理"""
    
    def __init__(self, states, actions, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.states = states
        self.actions = actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon  # 探索率
        
        # Q表
        self.q_table = {}
        for state in states:
            self.q_table[state] = {action: 0.0 for action in actions}
            
    def choose_action(self, state):
        """選擇動作（ε-greedy）"""
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            return self.get_best_action(state)
            
    def get_best_action(self, state):
        """取得最佳動作"""
        if state not in self.q_table:
            return random.choice(self.actions)
            
        q_values = self.q_table[state]
        max_q = max(q_values.values())
        
        # 如果有多個相同Q值的動作，随機選擇
        best_actions = [a for a, q in q_values.items() if q == max_q]
        return random.choice(best_actions)
        
    def learn(self, state, action, reward, next_state):
        """學習（Q-learning更新）"""
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in self.actions}
            
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state].values())
        
        # Q學習公式
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q
        
    def save(self, path):
        """儲存模型"""
        with open(path, "w") as f:
            json.dump({
                "q_table": self.q_table,
                "lr": self.lr,
                "gamma": self.gamma,
                "epsilon": self.epsilon
            }, f)
            
    def load(self, path):
        """載入模型"""
        with open(path, "r") as f:
            data = json.load(f)
            self.q_table = data["q_table"]
            self.lr = data["lr"]
            self.gamma = data["gamma"]
            self.epsilon = data["epsilon"]


class OperationPredictor:
    """操作預測器 - 預測下一步操作"""
    
    def __init__(self, model_dir="~/.openclaw/ai-operator/models"):
        self.model_dir = Path(os.path.expanduser(model_dir))
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # 定義狀態和動作
        self.states = [
            "page_loading", "page_loaded", "form_visible", "login_button_visible",
            "game_loaded", "spin_button_visible", "popup_visible", "error_state"
        ]
        
        self.actions = [
            "click_login", "fill_account", "fill_password", "select_agent",
            "select_game", "click_spin", "wait", "screenshot", "retry", "dismiss_popup"
        ]
        
        # 初始化Q學習代理
        self.agent = QLearningAgent(self.states, self.actions)
        
        # 嘗試載入既有模型
        model_path = self.model_dir / "operation_qlearning.json"
        if model_path.exists():
            try:
                self.agent.load(str(model_path))
            except:
                pass
                
    def predict_next_action(self, current_state, context=None):
        """預測下一步動作"""
        action = self.agent.choose_action(current_state)
        return {
            "recommended_action": action,
            "q_values": self.agent.q_table.get(current_state, {}),
            "confidence": self.get_confidence(current_state)
        }
        
    def get_confidence(self, state):
        """取得預測信心度"""
        if state not in self.agent.q_table:
            return 0.0
            
        q_values = list(self.agent.q_table[state].values())
        if not q_values:
            return 0.0
            
        max_q = max(q_values)
        if max_q == 0:
            return 0.0
            
        # 計算信心度（基於Q值差異）
        return min(1.0, max_q / 10.0)
        
    def record_outcome(self, state, action, reward):
        """記錄結果並學習"""
        # 假設下一個狀態就是回報對應的狀態
        next_state = state  # 簡化處理
        self.agent.learn(state, action, reward, next_state)
        
    def save_model(self):
        """儲存模型"""
        model_path = self.model_dir / "operation_qlearning.json"
        self.agent.save(str(model_path))


class OperationRecommender:
    """操作推薦器 - 根據歷史推薦最佳操作"""
    
    def __init__(self, data_dir="~/.openclaw/ai-operator/data"):
        self.data_dir = Path(os.path.expanduser(data_dir))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_patterns(self, logs):
        """分析操作模式"""
        patterns = {
            "click_before_fill": 0,
            "fill_before_click": 0,
            "wait_after_navigate": 0,
            "retry_on_failure": 0
        }
        
        for i in range(len(logs) - 1):
            curr = logs[i]
            next_op = logs[i + 1]
            
            if curr["operation_type"] == "click" and next_op["operation_type"] == "fill":
                patterns["click_before_fill"] += 1
            elif curr["operation_type"] == "fill" and next_op["operation_type"] == "click":
                patterns["fill_before_click"] += 1
                
            if curr["operation_type"] == "navigate" and next_op.get("duration_ms", 0) > 1000:
                patterns["wait_after_navigate"] += 1
                
            if curr["status"] == "failure":
                patterns["retry_on_failure"] += 1
                
        return patterns
        
    def recommend_strategy(self, task_type, logs):
        """推薦策略"""
        if not logs:
            return {
                "wait_before_click": 1000,
                "fill_first_then_click": True,
                "max_retries": 3
            }
            
        patterns = self.analyze_patterns(logs)
        
        # 基於模式調整策略
        if patterns["fill_before_click"] > patterns["click_before_fill"]:
            return {
                "wait_before_click": 500,
                "fill_first_then_click": True,
                "max_retries": 3
            }
        else:
            return {
                "wait_before_click": 1500,
                "fill_first_then_click": False,
                "max_retries": 4
            }


# 全域實例
predictor = OperationPredictor()
recommender = OperationRecommender()
