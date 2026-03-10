# SLOT Game 快速迴歸測試腳本基準 (v2.2)

> **最後更新**: 2026-03-05
> **更新說明**: v2.2 — 導入「腳本式測試架構」，測試步驟從 skill.md 抽離至 `scripts/` 目錄下的 Excel 腳本（由 manifest.json 統一管理）。skill.md 保留通用規格：座標表、異常處理規則、多語言對照表。詳見 CLAUDE.md 指令集。
>
> **架構變更摘要**：
> - 測試步驟 → `scripts/*.xlsx`（Steps sheet）
> - 遊戲座標覆寫 → `scripts/*.xlsx`（Config sheet）
> - 通用座標基準 → 仍在本檔（下方座標表）
> - 異常處理規則 → 仍在本檔（下方異常處理節）
> - LOGIN 頁面預設參數 → `Login info/Login.xlsx`（Account、Game ID、Language、Agent 等）
> - 指令集 → `CLAUDE.md`（RunTest / ListScripts / NewScript）

---

## 📌 LOGIN 頁面預設參數（Login.xlsx）

所有 LOGIN 相關操作均應優先使用 `Login info/Login.xlsx` 中的預設參數。該檔案位置：`/Login info/Login.xlsx`

### Login.xlsx 參數結構

| 欄位 | 說明 | 目前值 | 用途 |
|------|------|--------|------|
| **Agent** | 遊戲代理商識別 | Jmeter總控台 (Jmeter) | API 或登入路由參數 |
| **Sub Agent** | 子代理商（幣種） | PHP (披索 PHP) | 確定玩家帳戶幣種 |
| **Account** | 測試帳號 | Autotest00001 | LOGIN 頁面輸入帳號 |
| **Game ID** | 遊戲編號 | 230003 - King Royale | QA 模擬器選擇遊戲 |
| **Language** | 介面語言 | English (en) | 遊戲 & 頁面語言設定 |

### 使用規則

1. **初始化時讀取**：RunTest 啟動時，於初始化階段優先讀取 Login.xlsx
2. **作為預設值**：所有 LOGIN 相關步驟（navigate、click、input）均應使用此參數
3. **允許覆寫**：如 Excel 腳本的 Steps sheet 或 Config sheet 中明確指定不同參數，則以腳本為優先
4. **多帳號測試**：若需測試多組帳號，請先更新 Login.xlsx，再啟動 RunTest
5. **報告記錄**：每份測試報告應包含使用的 Account、Game ID、Language（來自 Login.xlsx）

### 何時更新 Login.xlsx

- ✅ 需要切換測試帳號
- ✅ 需要更換遊戲 ID（不同的遊戲版本）
- ✅ 需要測試不同語言
- ✅ 代理商或幣種發生變更

---

## ⚠️ 遊戲流程異常處理（AutoTest 必讀）

> 以下情境在自動化測試過程中**必須主動偵測與處理**，否則會導致測試中斷或結果誤判。

### 1. Timeout / Kick 機制

- **觸發條件**：遊戲長時間（通常 3～5 分鐘）無 SPIN 操作，伺服器會主動 KICK 玩家
- **症狀**：畫面出現警示彈跳視窗（如「您已被踢出」「連線逾時」等），點擊確認後遊戲結束，分頁導向 Back URL
- **處理方式**：
  1. 偵測到警示視窗 → 先截圖記錄
  2. 點擊視窗確認按鈕關閉
  3. 若遊戲仍可繼續 → 執行一次 SPIN，確認連線恢復
  4. 若已跳回 Back URL → 回報 BLOCKED，通知主對話重新登入
- **預防措施**：測試模塊五（VP Logo 多功能依序開關）等耗時模塊時，每 2～3 個功能測完後主動執行一次 SPIN 保持連線

### 2. Free SPIN 觸發

- **觸發條件**：SPIN 過程中出現特定符號組合（Scatter 或活動符號），自動進入 Free SPIN 模式
- **症狀**：畫面出現「FREE SPIN 觸發」動畫、確認/開始按鈕，或直接進入 Free SPIN 連續旋轉
- **處理方式**：
  1. 截圖記錄 Free SPIN 觸發畫面
  2. 若出現確認按鈕 → 點擊繼續（不跳過）
  3. 等待 Free SPIN 全部完成（可能需要額外 10～30 秒）
  4. Free SPIN 結束後截圖記錄最終 BALANCE 與 WIN
  5. BALANCE 驗算需涵蓋 Free SPIN 全程：`BALANCE後 = BALANCE前 - BET（原始單押）+ Free SPIN 總贏分`
  6. 在測試記錄中標注「含 Free SPIN」並說明旋轉次數與總贏分

### 3. 活動彈跳視窗（Event Popup）

- **觸發條件**：SPIN 後達成活動條件（累積任務、排行榜達標、特殊獎勵等），彈出活動通知視窗
- **症狀**：畫面中央出現非遊戲盤面的彈跳層（含獎勵資訊、領取按鈕或關閉 X）
- **處理方式**：
  1. 截圖記錄彈跳視窗內容
  2. 點擊「關閉 X」或「確認/領取」按鈕（視內容判斷）
  3. 確認彈跳視窗消失後再截圖，確認回到正常遊戲狀態
  4. 在測試記錄中備注「SPIN N 觸發活動彈跳視窗，已關閉」

### 4. 遊戲 Session 被踢（Back URL 跳轉）

- **觸發條件**：Timeout Kick 後，或伺服器強制登出，遊戲分頁自動導向 Back URL（如 `https://example.com/back`）
- **症狀**：tabs_context_mcp 顯示遊戲 tabId 的 title 變成「example.com」或非「Vertex Play」
- **處理方式（Subagent 內）**：
  1. 偵測到 tabId 導向非 Vertex Play 網址 → 回報 BLOCKED 並停止，通知主對話
- **處理方式（主對話）**：
  1. 切換至 QA 模擬器頁（tabId: 1123303072）
  2. 確認 Game ID / Language 仍為目標設定
  3. 重新點擊 Login → 等待新分頁開啟
  4. 從 tabs_context_mcp 取得新的 tabId
  5. 以新 tabId 重新啟動 Subagent，從 Loading Page 繼續

### 5. BALANCE 驗算差異（計費異常排查）

- **觸發條件**：SPIN 後計算出的 `BALANCE_AFTER ≠ BALANCE_BEFORE - BET + WIN`

**【重要】數值精度規範**：
- **BET**：通常固定為 **0.50**，截圖讀取時務必確認（不應出現 0.04、0.34 等異常值）
- **WIN**：可能顯示到**小數點後三位**（如 6.070、0.150、0.033）
- **BALANCE（Credit）**：精確存儲到**小數點後三位**，但顯示時**只顯示小數點後兩位**（不四捨五入，直接不顯示第三位）
- **驗算時務必注意精度**：WIN 的三位小數與 BALANCE 的三位小數精度進行計算，但 BALANCE 顯示時會隱藏第三位

- **常見原因與處理**：

| 差異類型 | 可能原因 | 處理方式 |
|---------|---------|---------|
| 差異 ≤ 0.01 | BALANCE 顯示隱藏第三位小數導致的讀取誤差（如實際 9,999,995.833 顯示為 9,999,995.83） | 標注 `✅ PASS（顯示精度差異）` |
| 差異 = 0.02～0.05 | WIN 值讀取不准（如 WIN 實際為 0.150 但讀成 0.15）或 BALANCE 第三位小數影響 | 放大截圖確認 WIN 小數位數，讀取 DOM 值確認實際精度 |
| 差異 = ±0.50（BET 金額） | BET 讀取錯誤，或觸發 Bonus 邏輯 | 確認 BET 是否真的為 0.50，記錄 Bonus 觸發條件 |
| 大於 0.10 的不規律差異 | 遊戲內部計費邏輯異常（未知） | 記錄詳細數據，提報 Dev 確認 |

- **正確驗算公式**：
  ```
  BALANCE_AFTER = BALANCE_BEFORE - BET + WIN

  特別注意：
  - BET = 0.50（固定值）
  - 若 WIN = 0.150（三位小數），BALANCE_AFTER 應四捨五入至小數點後二位
  ```

- **回報規範**：
  - 差異 ≤ 0.01（顯示精度差異：BALANCE 隱藏第三位小數）→ 標注 `✅ PASS（顯示精度差異）`
  - 差異 0.01～0.05（WIN 或 BALANCE 讀取精度誤差）→ 標注 `⚠️ PASS（待確認）`，記錄讀到的完整 WIN 與 BALANCE 值
  - 差異 > 0.05 → 標注 `❌ FAIL（BALANCE 計算異常）`，提交 Bug Report，記錄完整截圖與 DOM 值
  - 備註：遊戲 230003 無 Fee 機制。差異應優先檢查：(1) BALANCE 第三位隱藏小數，(2) WIN 值精度讀取

---

## 技術備注：自動化座標系統

> 適用於 Claude AI 自動化執行時參考，人工測試可略過此節。

- **截圖尺寸**：1568×702 px
- **點擊座標空間**：與截圖像素座標一致，直接使用，**無需換算 viewport CSS 座標**
- **iframe 位置**：left=690, top=0, width=540, height=859（viewport CSS）
- **核心規則**：`mcp__Claude_in_Chrome__computer` 的 click coordinate 直接使用截圖像素坐標

> ⚠️ **跨遊戲注意**：座標因遊戲版本略有差異。每次測試新遊戲前，建議先以 SPIN 按鈕做 1 次校驗確認座標有效。

### Game 230001 已驗證座標（截圖像素座標系）

| 元素 | 座標 (x, y) | 備註 |
|------|------------|------|
| VP Logo（活動選單） | (583, 80) | 左上角 VP 圓形 Logo |
| BAG | (598, 95) | 活動選單展開後 |
| INBOX | (657, 95) | 活動選單展開後 |
| NEWS | (598, 163) | 活動選單展開後 |
| USER | (657, 163) | 活動選單展開後 |
| TASK | (598, 285) | 活動選單展開後 |
| RANK | (657, 285) | 活動選單展開後 |
| WHEEL | (598, 350) | 活動選單展開後 |
| LOTTO | (657, 350) | 活動選單展開後 |
| DAILY | (598, 415) | 活動選單展開後 |
| 齒輪（設定） | (975, 686) | 右下角 |
| SOUND | (603, 628) | 設定選單展開後 |
| NOTIFY | (675, 628) | 設定選單展開後 |
| INFO | (748, 628) | 設定選單展開後 |
| AUTO | (820, 628) | 設定選單展開後 |
| RECORD | (891, 628) | 設定選單展開後 |
| CLOSE | (962, 628) | 設定選單展開後 |
| 右箭頭（Loading Page） | (955, 330) | Loading Page 右翻頁 |
| 左箭頭（Loading Page） | (605, 330) | Loading Page 左翻頁 |
| PLAY REAL / 開始遊戲 | (783, 578) | Loading Page 進入真錢模式 |
| SPIN | (783, 638) | 主遊戲畫面 |

### Game 230005 已驗證座標（截圖像素座標系）

| 元素 | 座標 (x, y) | 與 230001 差異 | 備註 |
|------|------------|--------------|------|
| VP Logo | (583, 80) | 無 | 左上角 |
| BAG～DAILY | 同 230001 | 無 | 活動選單展開後 |
| 齒輪（設定） | (975, 686) | 無 | 右下角 |
| SOUND | **(583, 628)** | x -20 | 設定選單展開後 |
| NOTIFY | **(665, 628)** | x -10 | 設定選單展開後 |
| INFO | (748, 628) | 無 | 設定選單展開後 |
| AUTO | (820, 628) | 無 | 設定選單展開後 |
| RECORD | (891, 628) | 無 | 設定選單展開後 |
| CLOSE | **(954, 628)** | x -8 | 設定選單展開後 |
| PLAY REAL / 開始遊戲 | (783, 587) | y +9 | Loading Page |
| SPIN | (783, 638) | 無 | 主遊戲畫面 |

### 多語言 UI 文字對照表

> 遊戲語言切換後，按鈕文字會跟著改變。Subagent 使用 `find` 工具搜尋按鈕時，需使用對應語言的文字。

| 功能 | English (en) | 簡體中文 (zh-Hans) | 備註 |
|------|-------------|------------------|------|
| 開始真錢遊戲 | PLAY REAL | 開始遊戲 | Loading Page 綠色按鈕 |
| 試玩模式 | DEMO MODE | 試玩模式 | Loading Page 橘色按鈕 |
| 下次不再顯示 | Don't show again | 下次不再顯示 | Loading Page 切換開關 |
| 背包 | BAG | 背包 | VP Logo 選單 |
| 信件 | INBOX | 收件箱 | VP Logo 選單 |
| 公告 | NEWS | 公告 | VP Logo 選單 |
| 個人資訊 | USER | 會員 | VP Logo 選單 |
| 任務 | TASK | 任務 | VP Logo 選單 |
| 排行榜 | RANK | 排行榜 | VP Logo 選單 |
| 轉盤 | WHEEL | 歡樂轉輪 | VP Logo 選單 |
| 樂透 | LOTTO | 樂透彩 | VP Logo 選單 |
| 每日獎勵 | DAILY | 每日獎勵 | VP Logo 選單 |
| 遊戲記錄 | RECORD | 遊戲紀錄 | 設定選單 |
| 自動玩 | AUTO | 自動設定 | 設定選單 |
| 遊戲說明 | INFO | 遊戲說明 | 設定選單 |

---

## 模塊一：登入與環境測試

> 1-5 / 1-6 的預期值依本次測試目標遊戲填寫（由主對話傳入 Subagent）。

| # | 測試步驟 | 預期結果 |
|---|---------|---------|
| 1-1 | 進入 QA1 測試環境 `https://gp001-qa1-simulation.xwautc.online/index` | 頁面標題顯示「遊戲測試工具」 |
| 1-2 | 驗證 Agent 欄位 | 顯示「Jmeter總控台 (Jmeter)」 |
| 1-3 | 驗證 Sub Agent 欄位 | 顯示「PHP (披索 PHP)」 |
| 1-4 | 驗證 Account 欄位 | 顯示「PHP123456789」 |
| 1-5 | 驗證 Game ID 欄位 | 顯示目標 Game ID 與遊戲名稱（例：`230001 - Golden Mahjong` / `230005 - Tai Chi`） |
| 1-6 | 驗證 Language 欄位 | 顯示目標語言（例：`English (en)` / `Chinese(Simplified) (zh-Hans)`） |
| 1-7 | 點擊 Login 按鈕 | 出現 Loading Bar，並透過 `window.open` 開啟新分頁，標題為「Vertex Play」 |

---

## 模塊二：遊戲功能選擇頁面（Loading Page）

> ⚠️ **Loading Page 頁數因遊戲而異**：230001 為 3 頁，230005 為 2 頁。測試時不寫死頁數，改為「持續右翻直到無法再翻」，再確認進入遊戲按鈕。
> **按鈕文字依語言而異**：英文為「PLAY REAL」，中文為「開始遊戲」（詳見座標區的多語言對照表）。

| # | 測試步驟 | 預期結果 |
|---|---------|---------|
| 2-1 | 確認 Loading Page 第 1 頁顯示 | 顯示遊戲特色說明第 1 頁，左側 `<` 箭頭不可點擊或不存在 |
| 2-2 | 持續點擊右箭頭 `>` 翻頁，直到無法繼續 | 每頁畫面內容明顯更換，記錄總頁數（依遊戲不同，2～4 頁不等） |
| 2-3 | 點擊左箭頭 `<` 一次 | 成功回到前一頁，確認可往回翻頁 |
| 2-4 | 點擊「PLAY REAL / 開始遊戲」（綠色大按鈕） | 進入真錢遊戲主畫面，底部顯示 BALANCE / WIN / BET 資訊列 |
| 2-5 | （選測）點擊「DEMO MODE / 試玩模式」 | 進入 Demo 模式，BALANCE 為虛擬金額 |

---

## 模塊三：主遊戲介面與資訊顯示

| # | 測試步驟 | 預期結果 |
|---|---------|---------|
| 3-1 | 觀察 BALANCE（Credit）顯示格式 | 數值包含千分位逗號與兩位小數點，例如：`10,471,445.19` |
| 3-2 | 觸發一次 SPIN 並有中獎 | WIN 區域顯示大於 0 的贏分金額 |
| 3-3 | 觸發一次 SPIN 無中獎 | WIN 區域顯示 `0.00` |
| 3-4 | 點擊 BET 區域（+ / -） | 出現不同金額選項，可調整押注額 |

---

## 模塊四：玩家操作區（SPIN 驗證）

**BALANCE 驗算公式**：`BALANCE後 = BALANCE前 - BET + WIN`（容許誤差 ±0.10）

| # | 測試步驟 | 預期結果 |
|---|---------|---------|
| 4-1 | 在 Credit 足夠的狀態下點擊 SPIN | 盤面開始滾動，SPIN 按鈕在滾動期間變為即停狀態 |
| 4-2 | 驗算有中獎的 BALANCE（至少 1 次 WIN > 0） | `BALANCE後 = BALANCE前 - BET + WIN`，誤差 < 0.10 |
| 4-3 | 驗算無中獎的 BALANCE（至少 1 次 WIN = 0） | `BALANCE後 = BALANCE前 - BET`，誤差 < 0.10 |
| 4-4 | 點擊 BET + 按鈕 | 押注往上一階，無 Loop（有封頂），BALANCE 扣除正確 |
| 4-5 | 點擊 BET - 按鈕 | 押注往下一階，無 Loop（有最小值） |
| 4-6 | 啟動 Auto Play | 自動連續 SPIN，按鈕圖示變為停止圖示 |
| 4-7 | 點擊即停按鈕（SPIN 進行中） | 滾停速度加快，圖示切換為取消即停 |
| 4-8 | 點擊取消即停 | 恢復正常滾停速度，圖示復原 |

---

## 模塊五：活動功能收納區（VP Logo 選單）

### 選單結構
```
VP Logo（展開/收合按鈕）
├── USER 區塊
│   ├── BAG（4頁籤：THIS GAME / OTHER GAME / ITEMS / MESSAGES）
│   ├── INBOX（玩家信件）
│   ├── NEWS（最新消息/公告 = ANNOUNCEMENT）
│   └── USER（3頁籤：USER / VIP / HONOR WALL）
└── FUNCTION 區塊
    ├── TASK（2頁籤：Daily Task / Weekly Task）
    ├── RANK（2頁籤：DRAGON RANK / TIGER RANK）
    ├── WHEEL（HAPPY WHEEL 轉盤）
    ├── LOTTO（樂透彩 3頁籤：TICKETS / PAYTABLE / HISTORY）
    └── DAILY（DAILY BONUS 每日簽到）
```

| # | 測試步驟 | 預期結果 |
|---|---------|---------|
| 5-1 | 點擊 VP Logo | 選單展開，顯示 USER 區塊（BAG/INBOX/NEWS/USER）與 FUNCTION 區塊（TASK/RANK/WHEEL/LOTTO/DAILY） |
| 5-2 | 點擊 BAG | 開啟背包，顯示四個頁籤：THIS GAME / OTHER GAME / ITEMS / MESSAGES |
| 5-3 | 點擊 BAG 的 X 關閉 | 背包視窗關閉，回到主畫面（選單仍展開） |
| 5-4 | 點擊 INBOX | 開啟信件頁面，顯示玩家收件匣與 Claim All 按鈕 |
| 5-5 | 點擊 INBOX 的 X 關閉 | 信件視窗關閉 |
| 5-6 | 點擊 NEWS | 開啟 ANNOUNCEMENT（公告）頁面 |
| 5-7 | 點擊 NEWS 的 X 關閉 | 公告視窗關閉 |
| 5-8 | 點擊 USER | 開啟個人資訊，頁籤列顯示：USER / VIP / HONOR WALL |
| 5-9 | 點擊 VIP 頁籤 | 切換至 VIP SYSTEM，顯示等級進度條與升/降級條件 |
| 5-10 | 點擊 HONOR WALL 頁籤 | 切換至榮耀牆，顯示玩家歷史最高倍率記錄列表 |
| 5-11 | 點擊 USER 的 X 關閉 | 視窗關閉 |
| 5-12 | 點擊 TASK | 開啟任務頁面，顯示：Daily Task / Weekly Task 兩個頁籤 |
| 5-13 | 點擊 Weekly Task 頁籤 | 切換至本週任務列表，顯示任務進度條 |
| 5-14 | 點擊 TASK 的 X 關閉 | 視窗關閉 |
| 5-15 | 點擊 RANK | 開啟 LEADERBOARD，顯示：DRAGON RANK / TIGER RANK 兩個頁籤 |
| 5-16 | 點擊 TIGER RANK 頁籤 | 切換至 TIGER RANK（最高單次倍率排行），顯示排名列表 |
| 5-17 | 點擊 RANK 的 X 關閉 | 視窗關閉 |
| 5-18 | 點擊 WHEEL | 開啟 HAPPY WHEEL 頁面，顯示轉盤、CARD BET 設定、SPIN 按鈕 |
| 5-19 | 點擊 WHEEL 的 X 關閉 | 視窗關閉 |
| 5-20 | 點擊 LOTTO | 開啟樂透彩頁面，顯示三個頁籤（TICKETS / PAYTABLE / HISTORY）與下次開獎時間 |
| 5-21 | 點擊 LOTTO 的 X 關閉 | 視窗關閉 |
| 5-22 | 點擊 DAILY | 開啟 DAILY BONUS 頁面，顯示 DAY1～DAY7 簽到日曆與 LOTTO 彩券獎勵 |
| 5-23 | 點擊 DAILY 的 X 關閉 | 視窗關閉 |
| 5-24 | 再次點擊 VP Logo | 選單收合，主畫面恢復正常，僅顯示遊戲控制按鈕 |

---

## 模塊六：設定選單（齒輪）

### 選單結構
```
齒輪圖示（右下角）
└── 設定列（底部）
    ├── SOUND（音效開關）
    ├── NOTIFY（通知開關）
    ├── INFO（遊戲說明）
    ├── AUTO（自動玩設定）
    ├── RECORD（遊戲記錄）
    └── CLOSE（關閉設定列）
```

| # | 測試步驟 | 預期結果 |
|---|---------|---------|
| 6-1 | 點擊右下角齒輪圖示 | 底部展開設定列，六個按鈕全部可見：SOUND / NOTIFY / INFO / AUTO / RECORD / CLOSE |
| 6-2 | 點擊 RECORD | 開啟 GAME RECORD 頁面，可按遊戲分類查詢近 30 天玩局記錄 |
| 6-3 | 點擊 RECORD 的 X 關閉 | 記錄視窗關閉，設定列仍顯示 |
| 6-4 | 點擊 AUTO | 開啟 AUTOPLAY SETTING 頁面，顯示 Total Spin 選項（50/100/200/500/999）、停止條件設定、START 按鈕 |
| 6-5 | 點擊 AUTO 的 X 關閉 | 自動玩設定視窗關閉 |
| 6-6 | 點擊 INFO | 開啟遊戲說明頁面，顯示 WILD / SPECIAL WILD 說明、賠付表 |
| 6-7 | 點擊 INFO 的 X 關閉 | 說明視窗關閉 |
| 6-8 | 點擊 NOTIFY（初始任意狀態） | 圖示狀態切換（亮色↔靜音鈴鐺），代表通知開/關切換 |
| 6-9 | 再次點擊 NOTIFY | 圖示狀態復原至原始狀態 |
| 6-10 | 點擊 SOUND（初始為亮色喇叭=開） | 圖示切換為靜音符號（關閉音效） |
| 6-11 | 再次點擊 SOUND | 圖示恢復為亮色喇叭（開啟音效） |
| 6-12 | 點擊 CLOSE | 設定列完全消失，底部恢復主遊戲控制欄（SPIN 等按鈕） |
