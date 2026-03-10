# SLOT Game QA 自動化測試框架

> 基於 Claude AI + Chrome Extension 的 H5 SLOT 遊戲快速迴歸測試框架

## 專案目標

透過 AI Agent 驅動瀏覽器自動化，對 H5 Canvas SLOT 遊戲執行標準化的 QA 迴歸測試。支援全自動（AutoTest）與人工引導（Manual）兩種模式，可針對不同遊戲版本、語言設定進行測試。

## 目錄結構

```
claude-test-agent/
├── CLAUDE.md              # AI 指令集與執行規則
├── skill.md               # 通用規格（座標表、異常處理、多語言對照）
├── README.md              # 本文件
├── scripts/               # 測試腳本（Excel 格式）
│   ├── manifest.json      #   腳本註冊表
│   ├── regression/        #   迴歸測試
│   ├── functional/        #   功能測試
│   ├── smoke/             #   冒煙測試
│   └── templates/         #   空白範本
├── specs/                 # 遊戲規格文件
│   ├── slot-game-spec.docx
│   └── slot-game-spec-v2.docx
├── reports/               # 測試報告輸出
├── context/               # 團隊角色與協作規範
│   ├── about-me.md
│   ├── brand-voice.md
│   └── working-style.md
└── slot-game-project-guide.docx  # 專案操作指南
```

## 快速開始

### 1. 環境需求

- Claude Desktop（Cowork 模式）或 Claude Code
- Chrome 瀏覽器 + Claude in Chrome 擴充功能
- QA1 測試環境存取權限

### 2. 常用指令

| 指令 | 說明 |
|------|------|
| `ListScripts` | 列出所有可用測試腳本 |
| `RunTest quick-smoke --game 230001 --lang en` | 執行快速冒煙測試 |
| `RunTest full-regression --game 230014 --lang ja` | 執行完整迴歸測試 |
| `RunTest spin-balance settings-panel` | 組合執行多個腳本 |
| `NewScript <name>` | 建立新測試腳本 |
| `Manual` | 切換人工引導模式 |
| `SaveReport` | 儲存測試報告 |

### 3. 新增測試腳本

1. 複製 `scripts/templates/_template.xlsx` 至目標分類目錄
2. 填入 Meta（名稱、模塊、時間）、Steps（測試步驟）、Config（座標覆寫）
3. 在 `scripts/manifest.json` 新增註冊項目
4. 使用 `RunTest <new-id>` 執行

## 已收錄腳本

| ID | 名稱 | 分類 | 模塊 | 預估時間 |
|----|------|------|------|---------|
| full-regression | 完整迴歸測試 | regression | M1-M6 | 25min |
| spin-balance | SPIN 與 BALANCE 驗算 | regression | M4 | 8min |
| loading-verify | Loading Page 驗證 | regression | M2 | 5min |
| activity-menu | 活動功能選單測試 | functional | M5 | 12min |
| settings-panel | 設定選單測試 | functional | M6 | 8min |
| quick-smoke | 快速冒煙測試 | smoke | M1+M2+M4 | 5min |

## 相關文件

- `CLAUDE.md` — 完整指令集與執行流程
- `skill.md` — 座標基準、異常處理規則、多語言 UI 對照表
- `slot-game-project-guide.docx` — 專案操作手冊（Word 格式）

## 維護者

QA Team
