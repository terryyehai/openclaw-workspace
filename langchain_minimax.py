#!/usr/bin/env python3
"""
LangChain + MiniMax API 整合
"""
import os
import json
import requests
from typing import Any, List, Optional, Dict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field


class MiniMaxChat(BaseChatModel):
    model: str = Field(default="abab6.5s-chat")
    api_key: str = Field(default="")
    api_base: str = Field(default="https://api.minimax.chat/v1")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048)
    
    @property
    def _llm_type(self) -> str:
        return "minimax_chat"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": self.model, "temperature": self.temperature, "max_tokens": self.max_tokens}
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        minimax_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                minimax_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                minimax_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                minimax_messages.insert(0, {"role": "system", "content": msg.content})
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": minimax_messages, "temperature": self.temperature, "max_tokens": self.max_tokens}
        
        try:
            response = requests.post(f"{self.api_base}/text/chatcompletion_v2", headers=headers, json=payload, timeout=30)
            print(f"MiniMax API 狀態: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"MiniMax 回應: {json.dumps(result)[:300]}")
                
                # 處理不同格式
                choices = result.get("choices")
                if choices and len(choices) > 0:
                    content = choices[0].get("message", {}).get("content", "無內容")
                elif choices:
                    content = str(choices)
                else:
                    content = f"回應: {result}"
            else:
                content = f"API 錯誤: {response.status_code}"
        except Exception as e:
            content = f"錯誤: {str(e)}"
        
        ai_message = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=ai_message)])


def get_minimax_llm(api_key: str = None, model: str = "abab6.5s-chat"):
    if not api_key:
        api_key = os.getenv("MINIMAX_API_KEY", "")
    if not api_key:
        raise ValueError("請設定 MINIMAX_API_KEY")
    return MiniMaxChat(api_key=api_key, model=model, temperature=0.7)


if __name__ == "__main__":
    api_key = os.getenv("MINIMAX_API_KEY", "")
    if api_key:
        llm = get_minimax_llm(api_key)
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content="用繁體中文說你好")])
        print(f"\n回覆: {response.content}")
    else:
        print("請設定 MINIMAX_API_KEY")
