#!/usr/bin/env python3
"""
LangChain 遊戲測試 Chain - 使用 MiniMax API
"""
import os
import sys
import json

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence

# 引入現有模組
from monitoring.operation_logger import logger
from strategies.strategy_optimizer import optimizer


def get_llm():
    """取得 LLM - 支援 OpenAI 和 MiniMax"""
    
    # 優先使用 MiniMax
    minimax_key = os.getenv("MINIMAX_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if minimax_key:
        print("使用 MiniMax API")
        # 使用自定義適配器
        from langchain_minimax import get_minimax_llm
        return get_minimax_llm(minimax_key, "abab6.5s-chat")
    
    elif openai_key:
        print("使用 OpenAI API")
        return ChatOpenAI(model="gpt-4o", temperature=0.3)
    
    else:
        print("⚠️ 沒有 API Key，將使用規則引擎")
        return None


class GameTestChain:
    """遊戲測試 Chain"""
    
    def __init__(self):
        self.llm = get_llm()
        self.use_llm = self.llm is not None
        
        if self.use_llm:
            self.chain = self._build_chain()
    
    def _build_chain(self):
        """建立 Chain"""
        
        parser = JsonOutputParser()
        
        prompt = ChatPromptTemplate.from_template("""
你是一個專業的遊戲測試分析師。

請分析以下遊戲數據，並提供結構化的結果。

遊戲數據：{game_data}

請回覆以下格式的 JSON：
{{
    "result_type": "win|lose|free_spin|bonus",
    "win_amount": 贏的金額（如果沒有則為 0）,
    "analysis": "简短分析"
}}
""")
        
        return prompt | self.llm | parser
    
    def analyze_game_result(self, game_data: dict) -> dict:
        """分析遊戲結果"""
        
        if not self.use_llm:
            # 使用規則引擎
            balance_before = game_data.get("balance_before", 0)
            balance_after = game_data.get("balance_after", 0)
            diff = balance_after - balance_before
            
            if diff > 0:
                result = {
                    "result_type": "win",
                    "win_amount": diff,
                    "analysis": f"贏了 {diff} 元"
                }
            elif diff < 0:
                result = {
                    "result_type": "lose",
                    "win_amount": diff,
                    "analysis": f"輸了 {abs(diff)} 元"
                }
            else:
                result = {
                    "result_type": "break_even",
                    "win_amount": 0,
                    "analysis": "不贏不輸"
                }
            
            # 記錄
            logger.log_operation("analyze_game", result)
            return result
        
        try:
            result = self.chain.invoke({"game_data": json.dumps(game_data)})
            logger.log_operation("analyze_game", result)
            return result
        except Exception as e:
            print(f"分析錯誤: {e}")
            return {"error": str(e)}
    
    def decide_next_action(self, current_state: dict) -> str:
        """決定下一步"""
        
        if not self.use_llm:
            # 使用規則引擎
            spin_count = current_state.get("spin_count", 0)
            target = current_state.get("target_spins", 10)
            
            if spin_count < target:
                return "spin"
            else:
                return "stop"
        
        prompt = f"""
目前狀態：
- 餘額：{current_state.get('balance', '未知')}
- 已 SPIN：{current_state.get('spin_count', 0)} 次
- 目標：{current_state.get('target_spins', 10)} 次

請決定下一步：spin / wait / stop
只回覆選項。
        """
        
        result = self.llm.invoke(prompt)
        return result.content.strip().lower()
    
    def generate_report(self, test_results: list) -> str:
        """生成報告"""
        
        if not self.use_llm:
            # 使用規則引擎生成報告
            total_spins = len(test_results)
            wins = sum(1 for r in test_results if r.get("result_type") == "win")
            loses = sum(1 for r in test_results if r.get("result_type") == "lose")
            
            total_win = sum(r.get("win_amount", 0) for r in test_results if r.get("win_amount", 0) > 0)
            total_lose = sum(abs(r.get("win_amount", 0)) for r in test_results if r.get("win_amount", 0) < 0)
            
            net = total_win - total_lose
            
            rtp = (total_win / (total_win + total_lose) * 100) if (total_win + total_lose) > 0 else 0
            
            report = f"""
# 遊戲測試報告

## 統計
- 總 SPIN 次數：{total_spins}
- 贏的次數：{wins}
- 輸的次數：{loses}
- 總贏金額：{total_win}
- 總輸金額：{total_lose}
- 淨利潤：{net}
- RTP：{rtp:.2f}%

## 建議
{"表現不錯！" if net > 0 else "建議調整投注策略"}
"""
            return report
        
        prompt = f"""
請根據以下測試結果生成報告：

{json.dumps(test_results, indent=2, ensure_ascii=False)}

請用繁體中文，包含：
1. 總結
2. 統計數據
3. 建議
"""
        
        result = self.llm.invoke(prompt)
        return result.content


class SmartGameAgent:
    """智能遊戲代理"""
    
    def __init__(self):
        self.game_chain = GameTestChain()
        self.state = {
            "balance": 0,
            "spin_count": 0,
            "target_spins": 10,
            "results": []
        }
    
    def update_state(self, **kwargs):
        self.state.update(kwargs)
    
    def get_state(self):
        return self.state.copy()
    
    def run_test_cycle(self):
        """執行測試循環"""
        
        action = self.game_chain.decide_next_action(self.state)
        print(f"[決定] {action}")
        
        if action == "spin":
            self.state["spin_count"] += 1
            logger.log_operation("spin", {"count": self.state["spin_count"]})
            return "spin"
        elif action == "stop":
            report = self.game_chain.generate_report(self.state["results"])
            print(f"\n{'='*50}")
            print("測試報告")
            print(f"{'='*50}")
            print(report)
            return "stop"
        else:
            return action


# 測試
if __name__ == "__main__":
    print("=" * 60)
    print("LangChain 遊戲測試 Chain")
    print("=" * 60)
    
    # 建立 Chain
    chain = GameTestChain()
    
    # 測試分析功能
    result = chain.analyze_game_result({
        "balance_before": 10000,
        "balance_after": 10030,
        "spin": 1
    })
    
    print(f"\n分析結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 測試智能代理
    print("\n" + "=" * 60)
    agent = SmartGameAgent()
    agent.update_state(balance=10000, spin_count=0, target_spins=10)
    
    for i in range(3):
        action = agent.run_test_cycle()
        print(f"行動 {i+1}: {action}")
        
        # 模擬結果
        if action == "spin":
            agent.state["results"].append({
                "result_type": "win" if i % 2 == 0 else "lose",
                "win_amount": 30 if i % 2 == 0 else -15
            })
    
    print("\n測試完成!")
