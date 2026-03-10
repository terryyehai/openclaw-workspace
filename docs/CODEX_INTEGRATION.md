# OpenAI Codex Computer Use 整合研究

## 概述

OpenAI Codex 的 Computer Use 功能允許 AI 模型透過截圖理解頁面狀態，並返回 UI 動作（點擊、輸入、滾動）來操作瀏覽器。

## 與 OpenClaw 現有瀏覽器控制的比較

| 功能 | Codex Computer Use | OpenClaw Browser |
|------|------------------|------------------|
| 截圖理解 | ✅ GPT-5.4 Vision | ❌ 無 |
| AI 推理 | ✅ 根據截圖推理 | ❌ 規則驅動 |
| 自主性 | 高 | 中 |
| 精確度 | 中（依賴視覺） | 高（CDP 精確） |

## 整合架構

### 方式 1: 使用 Responses API（推薦）

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.4",
    tools=[{"type": "computer"}],
    input="操作瀏覽器完成任務...",
    computer={"display_width": 1920, "display_height": 1080}
)
```

### 方式 2: 自訂 Tool 整合現有 CDP

保持 OpenClaw 的 CDP 控制，加上 Codex 的視覺理解能力。

## 實作需求

1. **API Key**: 需要 OpenAI API Key
2. **截圖功能**: 定期截圖並編碼為 base64
3. **動作執行**: 解析 Codex 返回的動作並執行
4. **循環機制**: 截圖 → 發送 → 執行 → 反饋

## 價格估算

- GPT-5.4: 輸入 $10/M tokens, 輸出 $40/M tokens
- 每次操作約 100K tokens (截圖 + 分析)
- 每次任務約 $0.01-0.05

## 下一步

1. 申請 OpenAI API Key
2. 建立 Codex Tool 原型
3. 與現有 CDP 控制整合
