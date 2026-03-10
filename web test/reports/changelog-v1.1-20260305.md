# 變更紀錄：v1.1 腳本式測試架構導入

> **日期**：2026-03-05
> **版本**：v1.0 → v1.1
> **變更類型**：架構升級
> **影響範圍**：CLAUDE.md / skill.md / README.md / slot-game-project-guide.docx / scripts/（新增）

---

## 變更摘要

本次更新將測試步驟從 monolithic `skill.md` 抽離至獨立的 Excel 腳本，實現「測試邏輯」與「執行引擎」的分離。QA 人員可透過編輯 Excel 控制測試內容，無需修改 skill.md 或 CLAUDE.md。

---

## 新增檔案清單

### scripts/ 目錄結構

| 檔案路徑 | 說明 |
|---------|------|
| `scripts/manifest.json` | 腳本註冊表，索引所有可用測試腳本 |
| `scripts/regression/full-regression.xlsx` | 完整迴歸測試（M1-M6，55 步驟） |
| `scripts/regression/spin-balance.xlsx` | SPIN 與 BALANCE 驗算（M4，15 步驟） |
| `scripts/regression/loading-verify.xlsx` | Loading Page 驗證（M2，8 步驟） |
| `scripts/functional/activity-menu.xlsx` | 活動功能選單測試（M5，29 步驟） |
| `scripts/functional/settings-panel.xlsx` | 設定選單測試（M6，16 步驟） |
| `scripts/smoke/quick-smoke.xlsx` | 快速冒煙測試（M1+M2+M4，13 步驟） |
| `scripts/templates/_template.xlsx` | 空白範本（建立新腳本用） |

### Excel 腳本標準 Sheet 結構

每份腳本包含 4 個 Sheet：

- **Meta**：名稱、版本、適用遊戲、作者、最後更新
- **Steps**：StepID / Module / Action / Target / Input / Expected / VerifyMethod / OnFail / Note
- **Config**：GameID / Element / Coord_X / Coord_Y / Override / Note
- **Changelog**：日期 / 版本 / 變更類型 / 說明

### manifest.json Schema

新增標準化欄位：

- `actionTypes`：11 種操作類型（navigate / click / screenshot / wait / verify_text / verify_balance / spin / find_and_click / find_and_verify / scroll / key_press）
- `verifyMethods`：6 種驗證方式（screenshot / text_match / balance_calc / element_exists / element_not_exists / visual_check）
- `onFailOptions`：4 種失敗處理（log / retry / abort / skip）
- `batchStrategy`：分批策略（single / auto-2 / auto-5）

---

## 修改檔案清單

### CLAUDE.md

| 區塊 | 變更 |
|------|------|
| 架構概覽 | **新增**：完整目錄結構圖 |
| 指令集 | **新增**：RunTest / ListScripts / NewScript / EditScript |
| 指令集 | **保留**：AutoTest / Manual / SaveReport / Reset（向下相容） |
| RunTest 執行流程 | **新增**：初始化 → 分批策略 → Subagent 建構 → 結果收集 |
| NewScript 建立流程 | **新增**：從範本複製 → 填入 Meta/Steps → 註冊 manifest |
| Action 對照表 | **新增**：11 種 Action 與 Target 格式對照 |
| 測試報告格式 | **更新**：新增「執行的腳本清單」欄位 |

### skill.md

| 區塊 | 變更 |
|------|------|
| 標題版本 | v2.1 → **v2.2** |
| 更新說明 | **新增**：架構變更摘要（測試步驟、座標覆寫、指令集的新歸屬位置） |

### README.md

| 區塊 | 變更 |
|------|------|
| 全文 | **重寫**：從 GitLab 預設範本改為專案實際說明 |
| 內容 | 包含：專案目標、目錄結構、快速開始、常用指令、已收錄腳本表、相關文件 |

### slot-game-project-guide.docx

| 區塊 | 變更 |
|------|------|
| 封面 | **更新**：Version 1.0 → 1.1，新增「腳本式測試架構」副標 |
| 目錄 | **新增**：第 7 節「腳本式測試架構」 |
| 第 7 節 | **新增**：目錄結構、新指令集表格、Excel Sheet 結構說明、設計原則 |
| 第 8 節 | **原第 7 節**：更新日誌移至第 8 節 |
| 更新日誌表 | **新增**：v1.1 架構升級記錄 |

---

## 未變更檔案

| 檔案 | 原因 |
|------|------|
| `context/about-me.md` | 團隊角色定義，不受架構影響 |
| `context/brand-voice.md` | 語氣規範，不受架構影響 |
| `context/working-style.md` | 協作規則，不受架構影響 |
| `specs/slot-game-spec.docx` | 原始遊戲規格，保留為歷史版本 |
| `specs/slot-game-spec-v2.docx` | 排版後遊戲規格，內容不變 |
| `reports/qa-*.md` | 歷史測試報告，不修改 |

---

## 向下相容性

- `AutoTest` 指令等同 `RunTest full-regression`，行為不變
- `AutoTest 模塊X` 從 full-regression 腳本篩選對應 Module 步驟
- `Manual` / `SaveReport` / `Reset` 行為不變
- skill.md 的座標表、異常處理規則、多語言對照表不變

---

## 後續規劃

1. **新增遊戲專屬腳本**：針對不同遊戲版本的特有功能建立專屬腳本（如 Free SPIN 驗證、特殊 Wild 功能）
2. **座標自動校驗**：在腳本中加入座標校驗步驟，首次執行自動比對並更新 Config sheet
3. **腳本版本管理**：結合 Git 追蹤 manifest.json 與 Excel 變更
4. **測試覆蓋率統計**：依 manifest.json 的 modules 標記，產出跨腳本覆蓋率報告
