# Specs 最新變更日誌

> 本檔案記錄 `specs/` 目錄中所有規格文件的變更歷史。
> **版本對標**：本日誌版本與 `manifest.json` 中的 `projectVersion` 保持一致。

---

## 📅 2026-03-05 — v1.0 初版發佈

### ✨ 新增

#### Demo Mode-spec.docx (v1.0)
- **功能**：完整的 DEMO MODE 遊戲規格說明 + 測試 SOP
- **排版**：參考 slot-game-spec-v2.docx 的專業規格文件格式
- **內容結構**：
  - `1. 遊戲功能選擇頁面` — 功能說明表格、注意事項
  - `2. DEMO MODE 遊戲頁面` — 主要按鈕說明、圖片標題標註
  - `3. DEMO MODE 測試流程（SOP）` — 4 步驟表格 + 詳細驗證點
- **核心測試流程**：
  1. DEMO MODE 中執行多場 SPIN，驗證 Credit 與 BET 扣款計算
  2. FEATURE 1～N 全部執行一輪，驗證特色演示完整呈現
  3. 驗證設定功能（SOUND / INFO / AUTO / CLOSE）
  4. 點擊 PLAY REAL，確認跳轉至正式遊戲頁面
- **使用場景**：Claude 執行 DEMO MODE 測試時的主要參考文件
- **圖片清單**：7 張圖片（已加標題標註）
  - image1.jpeg — 遊戲功能選擇頁面示意圖
  - image2.jpeg — DEMO MODE 遊戲頁面示意圖
  - image3.jpg ~ image7.jpg — 功能按鈕圖示

#### manifest.json (v1.0)
- **功能**：Specs 動態版本控制的核心驅動檔案
- **版本追蹤**：記錄每個 spec 的版本、更新時間、變更類型
- **變更分類**：
  - `new` — 新增 spec 檔案
  - `modified` — 現有 spec 有更新
  - `stable` — 無變更（參考標準）
  - `deprecated` — 已棄用
- **自動化支援**：支援 Claude Init 流程自動檢測並載入
- **後續擴展**：預留了 upcomingSpecs 欄位供新增規劃

#### LATEST_CHANGES.md (v1.0)
- **功能**：人工提示層面的變更日誌
- **用途**：使用者與 Claude 快速了解規格最新異動
- **更新規則**：新增/修改 spec 時同步更新此檔案

---

### 📝 CLAUDE.md 相關更新

#### 新增「動態記憶更新機制（Specs Init）」段落
- **位置**：CLAUDE.md 的「核心執行準則」章節後
- **內容**：
  - 強制初始化流程（4 步驟）
  - 版本控制規則表
  - 實現細節（讀取時機、讀取對象、載入方式、快取策略）
- **效果**：每次執行任務前，Claude 自動檢測 specs 變更並注入最新內容

---

### 🔗 相關檔案連結

| 檔案名稱 | 位置 | 說明 |
|---------|------|------|
| Demo Mode-spec.docx | specs/ | DEMO MODE 規格（本次新增） |
| manifest.json | specs/ | 版本控制索引（本次新增） |
| LATEST_CHANGES.md | specs/ | 變更日誌（本次新增） |
| CLAUDE.md | 專案根目錄 | 執行指令（已更新） |
| slot-game-spec-v2.docx | specs/ | 排版參考標準 |

---

### 💡 使用指南

#### 對 Claude（自動化執行）
1. 執行任務前，自動讀取 `manifest.json`
2. 檢測是否有 `changeType = "new"` 或 `"modified"` 的項目
3. 若有更新，自動載入對應 spec 檔案並注入執行 context
4. 報告：`🔄 已檢測 Demo Mode-spec v1.0 更新，已重新載入`

#### 對人類（手動維護）
1. **新增 spec 時**：
   - 建立新 spec 檔案（.docx / .xlsx / .json）
   - 在 `manifest.json` 新增項目，設定 `changeType: "new"`
   - 在本檔案（LATEST_CHANGES.md）的「新增」區塊記錄內容

2. **修改 spec 時**：
   - 更新 spec 檔案
   - 在 `manifest.json` 更新 `version`、`updatedAt`、`summary`
   - 設定 `changeType: "modified"`
   - 在本檔案的「更新」區塊記錄變更概要

3. **棄用 spec 時**：
   - 在 `manifest.json` 設定 `changeType: "deprecated"`
   - 在本檔案的「已棄用」區塊說明停用原因

---

## 未來計畫（RoadMap）

| 項目 | 計畫完成日期 | 說明 |
|------|-------------|------|
| **Game-Features.xlsx** | 2026-03-15 | 按 Game ID 集中列出各遊戲的 FEATURE |
| **Cross-Game Coordinates JSON** | 2026-03-20 | 將遊戲專屬座標集中管理（目前分散在 Excel Config sheet） |
| **Changelog 整合視圖** | 2026-03-25 | 建立一個整合檢視，顯示所有 spec 的時間軸 |

---

## 更新規則速記

```markdown
新增 spec 時：
1. 建立檔案 → manifest.json 新增項目（changeType: "new"）→ 本檔案記錄

修改 spec 時：
1. 修改檔案 → manifest.json 更新 version / updatedAt → 本檔案記錄

棄用 spec 時：
1. manifest.json 設定 changeType: "deprecated" → 本檔案記錄停用原因
```

---

**最後更新**：2026-03-05 06:30 UTC
**維護責任**：Terry（QA Engineer & Full Stack Developer）
