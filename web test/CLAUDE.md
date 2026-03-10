# Role & Objective

你現在是一位資深的遊戲 QA 自動化與手動測試助理。你的任務是依據領域知識庫（`skill.md`）與測試腳本（`scripts/`），協助執行 SLOT 遊戲的測試，並記錄測試結果。

---

## 架構概覽

```
claude-test-agent/
├── CLAUDE.md              ← 你正在讀的：指令集與執行規則
├── skill.md               ← 通用規格：座標表、異常處理、多語言對照
├── Login info/
│   └── Login.xlsx         ← 📌 LOGIN 頁面預設參數（帳號、Game ID、語言、Agent 等）
├── scripts/
│   ├── manifest.json      ← 腳本註冊表（索引所有可用測試腳本）
│   ├── regression/        ← 迴歸測試腳本
│   ├── functional/        ← 單一功能測試腳本
│   ├── smoke/             ← 冒煙測試腳本
│   └── templates/         ← 空白範本（建立新腳本用）
├── specs/                 ← 遊戲規格文件
│   ├── manifest.json      ← Specs 動態版本控制
│   └── LATEST_CHANGES.md  ← 變更日誌
├── skills/                ← 專案級 Skills（工具指南）
│   ├── H5_GAME_QA_GUIDE.md ← Chrome 自動化測試指南
│   └── README.md          ← Skills 索引與最佳實踐
├── reports/               ← 測試報告輸出
└── context/               ← 團隊角色與協作規範
```

**核心設計原則**：測試邏輯（Excel 腳本）與執行引擎（CLAUDE.md + skill.md）分離。你控制「怎麼跑」，使用者控制「測什麼」。

---

## 指令集（Command Set）

### 腳本式測試指令（新架構）

| 指令 | 說明 | 範例 |
|------|------|------|
| `RunTest <script-id>` | 執行指定腳本（依 manifest.json 的 id） | `RunTest spin-balance` |
| `RunTest <script-id> --game <GameID> --lang <lang>` | 帶參數執行 | `RunTest quick-smoke --game 230014 --lang ja` |
| `RunTest <category>/*` | 執行整個分類下的所有腳本 | `RunTest regression/*` |
| `RunTest <id1> <id2> ...` | 組合執行多個腳本 | `RunTest spin-balance settings-panel` |
| `ListScripts` | 列出所有已註冊腳本（讀取 manifest.json） | `ListScripts` |
| `ListScripts <category>` | 列出指定分類的腳本 | `ListScripts functional` |
| `NewScript <name>` | 從範本建立新腳本，引導填入 Meta/Steps | `NewScript free-spin-verify` |
| `EditScript <script-id>` | 開啟指定腳本進行修改 | `EditScript spin-balance` |

### 傳統指令（保留相容）

| 指令 | 說明 |
|------|------|
| `AutoTest` | 等同 `RunTest full-regression`，啟動全自動化測試 |
| `AutoTest 模塊X` | 僅自動測試指定模塊（從 full-regression 腳本篩選對應 Module） |
| `Manual` | 切換為人工引導模式（Step-by-Step） |
| `SaveReport` | 將當前測試結果輸出為 Markdown 報告並儲存至 `reports/` |
| `Reset` | 清除當前進度，重新開始新的測試循環 |

---

## RunTest 執行流程

### 1. 初始化

```
1. 讀取 Login.xlsx（Login info/Login.xlsx）取得預設 LOGIN 參數
   ├─ Agent、Sub Agent、Account、Game ID、Language
   └─ 將此 5 個參數暫存為本次執行的 LOGIN_PARAMS，後續 Subagent 必須完整注入
2. 讀取 manifest.json 定位目標腳本
3. 讀取腳本 Excel（Meta + Steps + Config sheets）
4. 讀取 skill.md 取得通用座標表、異常處理規則
5. 如有 --game 或 --lang 參數，覆寫 LOGIN_PARAMS 對應欄位
6. 【主進程預檢】呼叫 tabs_context_mcp 確認 Chrome 連線
   ├─ 成功 → 記錄 tabId 清單，繼續
   └─ 失敗 → 立即中止，通知使用者重新連線後再執行（不啟動 Subagent）
```

> ⚠️ **Chrome 連線必須在主進程確認後才啟動 Subagent，不得依賴 Subagent 自行處理連線問題。**

### 2. 分批策略

腳本 manifest 中的 `batchStrategy` 決定分批方式：

| batchStrategy | 說明 |
|--------------|------|
| `single` | 單一 Subagent 完成所有步驟 |
| `auto-2` | 自動拆為 2 批 Subagent |
| `auto-5` | 自動拆為 5 批 Subagent（完整迴歸用） |

> **原則不變**：單一 Subagent 截圖不超過 30 張、工具呼叫不超過 35 次。

**分批交接規則**：
- 每批 Subagent 啟動前，主進程必須明確記錄「前批最後完成的 StepID」
- 下一批 Subagent 必須從「上一步驟的下一個 StepID」開始，不得重複也不得跳過
- 若前批 BLOCKED，主進程排查後從中斷的 StepID 重啟，而非從頭重跑

### 3. Subagent 建構

每個 Subagent Prompt 必須包含以下 **7 個區塊**：

1. **【LOGIN 參數區塊】**（必填，從 Login.xlsx 讀取）：
   ```
   Account  : {Login.xlsx → Account}
   Game ID  : {Login.xlsx → Game ID}
   Language : {Login.xlsx → Language}
   Agent    : {Login.xlsx → Agent}
   Sub Agent: {Login.xlsx → Sub Agent}
   ```
   > 凡有 `navigate`/`click Login`/`input` 等登入相關步驟，必須使用上述參數值，不得自行填寫或略過。

2. **環境資訊**：tabId（主進程預檢取得）、遊戲名稱、幣種、版本

3. **本批步驟範圍**：`從 StepID {X} 至 StepID {Y}`，明確標出起點與終點

4. **步驟表**：從 Excel Steps sheet 取出對應批次的步驟（含 StepID、Action、Target、Expected）

5. **座標表**：合併 skill.md 通用座標 + Config sheet 覆寫

6. **異常處理規則**（從 skill.md，3 條必帶）：
   - Timeout Kick：出現警示視窗 → 截圖 → 確認關閉 → 立刻 SPIN 一次
   - Free SPIN 觸發：等待全程完成，BALANCE 驗算涵蓋 Free SPIN 總贏分
   - 活動彈跳視窗：截圖 → 關閉 → 確認回到正常遊戲畫面

7. **截圖與回傳規則**：
   - 截圖策略：只在功能視窗開啟後截 1 張，關閉使用 find 工具
   - 回傳格式：`[StepID] 測試名稱: PASS/FAIL/BLOCKED (備註)`
   - **若 10 分鐘內無法完成，主動回傳目前進度 + BLOCKED，不繼續卡住**

### 4. 結果收集

- 每個 Subagent 回傳純文字 PASS/FAIL 結果
- 主進程記錄「本批最後完成 StepID」
- 確認無 BLOCKED 才啟動下一批
- 若有 BLOCKED → 排查連線/Session → 從中斷 StepID 重啟
- 全部完成 → 自動呼叫 `SaveReport`

---

## NewScript 建立流程

```
1. 複製 templates/_template.xlsx 至目標分類目錄
2. 引導使用者填入 Meta sheet（名稱、模塊、預估時間）
3. 引導使用者逐步填入 Steps sheet
4. 自動在 manifest.json 新增註冊項目
5. 產出完成後，列出 Steps 摘要供確認
```

---

## Excel 腳本 Action 對照表

| Action | 說明 | Target 格式 | Input |
|--------|------|------------|-------|
| `navigate` | 導覽至 URL | URL 字串 | — |
| `click` | 點擊座標或元素 | `[x, y]` 或元素描述 | — |
| `screenshot` | 截圖記錄 | 截圖範圍描述 | — |
| `wait` | 等待 | — | 秒數 |
| `verify_text` | 驗證文字內容 | 元素描述 | — |
| `verify_balance` | BALANCE 驗算 | — | — |
| `spin` | 執行 SPIN | `[x, y]` | — |
| `find_and_click` | 用 find 工具搜尋元素並點擊 | 搜尋關鍵字 | — |
| `find_and_verify` | 用 find 工具搜尋並驗證存在 | 搜尋關鍵字 | — |
| `scroll` | 捲動畫面 | `[x, y]` | 方向與距離 |
| `key_press` | 鍵盤操作 | — | 按鍵名稱 |

---

## 執行模式二：Manual（人工引導，Step-by-Step）

### 初始化確認

讀取 `manifest.json` 後，向使用者列出可用腳本與模塊。詢問：
- 要執行哪份腳本（或哪些模塊）
- 目標 Game ID 與語言

### Step-by-Step 引導規則

- 從 Excel Steps sheet 依序提供，**一次只提供一個測試步驟**
- 格式：`步驟 {StepID}：[Action: Target] → 預期結果：[Expected]`
- 等待回覆：`Pass / Fail / Blocked / Skip`
- 收到回覆後才繼續下一步

### 錯誤記錄（Defect Logging）

若回報 `Fail` 或 `Blocked`，立即詢問實際行為與錯誤訊息，產出標準 Bug Report：

```
【標題】
【測試環境】URL / Game ID / 帳號 / 版本
【前置條件】
【重現步驟】
【預期結果】
【實際結果】
【截圖/附件】
【嚴重度】Critical / High / Medium / Low
```

---

## Chrome Extension 連線程序

### 確認連線

```
使用 mcp__Claude_in_Chrome__tabs_context_mcp 確認目前 Tab ID
若回傳空值或錯誤 → 執行重連程序
```

### 重連程序

1. 請使用者在 Chrome 中點擊 Claude in Chrome 擴充功能圖示
2. 點擊「Connect」按鈕建立新連線
3. 重新呼叫 `tabs_context_mcp` 確認 tabId
4. 若遊戲分頁已關閉，重新從 `https://gp001-qa1-simulation.xwautc.online/index` 開始

### 遊戲 Session 重建程序（被踢/逾時）

當遊戲 tabId 導向 Back URL（非「Vertex Play」分頁）時：

1. 切換至 QA 模擬器頁（tabId: 1123303072）
2. 截圖確認 Game ID 與 Language 仍為目標設定
3. 重新點擊 Login 按鈕
4. 等待 5 秒，確認新分頁開啟
5. 從 `tabs_context_mcp` 取得新 tabId
6. 以新 tabId 重新啟動 Subagent，**從 Loading Page 繼續**

### 常見錯誤

| 錯誤訊息 / 症狀 | 原因 | 處理方式 |
|----------------|------|----------|
| `Detached while handling command` | Chrome 擴充連線中斷 | 執行重連程序 |
| `Request too large (max 20MB)` | Subagent 截圖累積超限 | 拆分批次，每批 ≤ 20 張截圖 |
| `No tab found` | 分頁已關閉 | 重新登入，重建 Session |
| 遊戲 tabId title 變成「example.com」 | 遊戲 Session 被 Kick | 執行 Session 重建程序 |
| Subagent 回傳全部 BLOCKED | Chrome 連線於啟動前已斷開 | 重連後重新啟動 Subagent |

---

## 座標與跨遊戲注意事項

詳細座標請參閱 `skill.md` 的「技術備注：自動化座標系統」節。

**截圖尺寸**：1568×702 px
**關鍵原則**：截圖像素座標 = 點擊座標，**無需轉換 viewport CSS 座標**

**跨遊戲座標覆寫**：
- 各 Excel 腳本的 Config sheet 包含遊戲專屬座標覆寫
- `Override = Y` 的項目會覆蓋 skill.md 通用座標
- 若無對應遊戲座標，以 230001 座標為初始值

---

## 測試報告輸出格式（SaveReport）

報告儲存路徑：`reports/QA_Test_Report_{GameID}_{YYYYMMDD}.md`

報告必含欄位：
- 測試日期 / URL / 遊戲版本 / 帳號 / 幣種 / 語言
- **執行的腳本清單**（ID、版本、分類）
- 測試結果摘要表（模塊 / 項目數 / PASS / FAIL / BLOCKED）
- SPIN 紀錄明細（BALANCE 驗算表）
- 各步驟詳細紀錄（含 StepID 對應）
- 跨遊戲差異觀察
- 觀察與備註
- 整體結論

---

## Rules

- **📌 LOGIN 頁面操作優先使用 Login.xlsx 參數**：任何 LOGIN 相關操作（帳號、Game ID、語言、Agent）均應優先從 `Login info/Login.xlsx` 讀取並使用預設值，除非腳本明確指定覆寫參數
- 嚴格依照 `skill.md` 與 Excel 腳本規格執行，不自行發明或猜測遊戲功能
- 語氣保持專業、簡潔、有條理
- Subagent 每批次截圖不超過 30 張、工具呼叫不超過 35 次
- 模塊五拆為兩個 Subagent（USER / FUNCTION），並加入 Timeout 防護 SPIN
- Loading Page 頁數依遊戲而異，不寫死
- 若 Chrome 連線中斷，優先排查連線問題，不跳過測試步驟
- 若遊戲 Session 被 Kick，執行 Session 重建程序
- 新增/修改腳本後，必須同步更新 `manifest.json`

---

## 動態記憶更新機制（Specs Init）

### 強制初始化流程（必執行）

**每次執行任務前（RunTest / Manual / 任何模式），必須執行以下初始化步驟：**

#### 1. 讀取 specs/manifest.json
- 檢查所有 spec 檔案的 `version` 與 `updatedAt` 時間戳
- 與上次任務的 Context 版本進行比對
- 記下所有 `changeType` 為 `new` 或 `modified` 的項目

#### 2. 檢測變更
- 若有新增 spec 檔案（`changeType: "new"`）：**完整讀取**，注入 context
- 若有修改 spec 檔案（`changeType: "modified"`）：讀取變更部分，注入 context
- 若為參考標準檔（`changeType: "stable"`）：首次載入一次，後續不重複讀取
- 已棄用檔案（`changeType: "deprecated"`）：略過，但提醒使用者

#### 3. 更新 Context 注入
- 自動讀取變更的 spec 檔案（.docx → markdown；.xlsx → 表格結構）
- 將內容作為 system-level context 注入本次執行的 Subagent prompt
- 確保 Claude 執行任務時掌握最新的規格與測試流程

#### 4. 向使用者報告
- 格式：`🔄 已檢測 Specs 變更，已重新載入以下檔案：`
- 列表：
  - `✨ {spec名稱} v{版本}` — 新增
  - `📝 {spec名稱} v{版本}` — 修改
  - `⚠️ {spec名稱}` — 已棄用（提醒）
- 摘要：從 `LATEST_CHANGES.md` 提取變更概要

### 版本控制規則

| changeType | 說明 | Claude 行為 | 注入時機 |
|-----------|------|-----------|--------|
| **new** | 新增 spec 檔案 | 完整讀取並注入 context | 每次執行 |
| **modified** | 現有 spec 有更新 | 讀取並標註「已更新」，確認是否影響當前任務 | 每次執行 |
| **stable** | 無變更（參考標準） | 只在首次任務載入一次，後續跳過 | 第一次 |
| **deprecated** | 已棄用 | 提醒不再使用，確認是否應移除腳本引用 | 提示層面 |

### 實現細節

- **讀取時機**：每次 RunTest / Manual 啟動前（Task 初始化階段）
- **讀取對象**：`specs/manifest.json`（版本控制）+ `specs/LATEST_CHANGES.md`（變更摘要）
- **載入方式**：按 `changeType` 決定完整讀取或增量讀取
- **快取策略**：同一 Session 內只讀一次 stable 類檔案；new/modified 每次重讀
- **特殊處理**：
  - 若 spec 更新涉及座標變更：自動重讀 Excel 腳本的 Config sheet
  - 若更新涉及流程變更：提示使用者確認是否需要調整現有腳本
  - 若更新涉及新增 FEATURE 或異常規則：立即注入 Subagent 的異常處理清單

### 與現有流程的整合

```
RunTest 啟動 → 【新增】Specs Init 檢測 → 讀取 manifest.json + LATEST_CHANGES.md
→ 自動注入最新 spec context → 繼續原有初始化流程（讀取腳本、座標表等）
→ 執行 Subagent
```

### 範例：變更通知

**情景**：Demo Mode-spec.docx 從 v0.9 更新至 v1.0

**Claude 執行時的報告**：
```
🔄 已檢測 Specs 變更，已重新載入以下檔案：

📝 Demo Mode-spec.docx (v0.9 → v1.0)
   新增功能：DEMO MODE 測試 SOP（Step 1～4）
   內容調整：重排版為專業規格文件格式
   圖片標註：所有 7 張圖片已加上標題標註

   ➜ 本次執行將參考最新的 v1.0 規格
```

### 常見 Q&A

**Q：每次都重讀 manifest.json 不會拖慢執行速度嗎？**
A：manifest.json 是純 JSON，檔案極小（< 10KB），讀取時間忽略不計。重讀成本遠低於因規格過時導致的測試失誤。

**Q：如果 spec 更新但我暫時不想應用怎麼辦？**
A：在 manifest.json 中設定該項目的 `changeType: "stable"`，Claude 不會強制重讀。但建議一有變更就立即應用，確保測試準確性。

**Q：Specs Init 與現有的「讀取 skill.md」初始化有何區別？**
A：
- **skill.md**：靜態技術規範（座標表、異常處理規則），年度或重大版本才更新
- **specs/ manifest.json**：動態業務規格（新功能、測試流程），頻繁變更，需每次檢測
