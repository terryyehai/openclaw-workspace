# H5 Game QA — 瀏覽器自動化測試指南

> **專案級 Skill**
>
> 位置：`skills/H5_GAME_QA_GUIDE.md`
>
> 用途：Claude 在 Chrome 瀏覽器上進行 H5 遊戲 QA 自動化測試時的執行指南
>
> 適用於：Login → Loading Page → Basic Game Play 三大步驟

**最後更新**：2026-03-05
**版本**：1.0（專案本地版本）

---

## ⚠️ 關鍵架構知識（必讀）

以下是實際測試中反覆遇到的問題，跳過這些會浪費大量時間在座標除錯上。

### 1. 遊戲在 iframe 中渲染（不是直接在主頁面上）

Login 後開啟的 "Vertex Play" 頁面，**PixiJS 遊戲 canvas 是嵌在一個 `<iframe>` 裡面**，而非直接在主頁面上。這帶來幾個重要影響：

- `document.querySelector('canvas')` 在主頁面會回傳 `null`（canvas 在 iframe 內部）
- `get_page_text` 只會取得主頁面的文字（如 Claude extension UI 文字），**無法取得遊戲內的 BALANCE / WIN / BET 數值**
- 由於跨域限制，`javascript_tool` 也**無法存取 iframe 內部的 DOM**

### 2. 所有座標必須基於 iframe 的實際位置來計算

遊戲 iframe 並不是佔滿整個 viewport，它有自己的位置和大小。**直接使用 `skill.md` 中的參考座標會點不到東西**，必須先偵測 iframe 位置再換算。

**強制執行的座標校準流程**（在遊戲頁面上做任何點擊前執行）：

```javascript
// Step A: 取得 iframe 的實際位置（在遊戲頁的 tabId 上執行）
const iframes = document.querySelectorAll('iframe');
const gameIframe = Array.from(iframes).find(f => f.getBoundingClientRect().width > 100);
const rect = gameIframe.getBoundingClientRect();
JSON.stringify({
  left: rect.left, top: rect.top,
  width: rect.width, height: rect.height,
  viewport: { w: window.innerWidth, h: window.innerHeight }
});
```

```
// Step B: 用以下公式換算座標（參考座標基於 430×932）
x_viewport = iframe.left + (x_ref / 430) * iframe.width
y_viewport = iframe.top  + (y_ref / 932) * iframe.height
```

> **實測範例**：設定 `resize_window(430, 932)` 後，瀏覽器因最小寬度限制，實際 viewport 為 500×697。iframe 位於 `{ left: 31, top: 0, width: 438, height: 697 }`。

### 3. 用 zoom 校準比盲猜座標快得多

如果換算座標仍然點不到，不要反覆微調座標碰運氣。用 `zoom` 放大按鈕所在區域（建議 100×120 px 範圍），直接從放大圖中判斷按鈕中心的 viewport 座標。

**有效的 zoom 策略**：
- 先 zoom 較大的區域（如 100×120 px）確認按鈕在不在這個範圍內
- 按鈕外觀：箭頭按鈕是**深色圓底 + 黃色箭頭圖標**，不是文字
- 從放大圖中估算按鈕中心在原始座標系統中的位置

### 4. 遊戲數值只能從截圖目視讀取

因為跨域限制，BALANCE / WIN / BET **無法用程式讀取**。正確的做法：
- 每次 SPIN 前後都截圖
- 從截圖底部資訊列讀取數值，格式為：`[幣種] [BALANCE] [WIN] [BET]`
- 如果數字看不清楚，用 `zoom` 放大底部資訊列區域

---

## 前置準備

開始測試前，確認以下事項：

1. **取得測試參數** — 從使用者提供的文件或對話中提取：
   - `TEST_URL`: QA 測試工具網址（預設: `https://gp001-qa1-simulation.xwautc.online`）
   - `Agent`: 代理商名稱（預設: `DevPHP`）
   - `SubAgent`: 子代理商（預設: `Default`）
   - `Account`: 測試帳號（預設: `nunu1`）
   - `GameID`: 遊戲 ID（如 `230003`）
   - `Language`: 語言（預設: `en`）

2. **建立 Chrome 標籤** — 使用 `tabs_context_mcp` 取得或建立 tab group，再用 `tabs_create_mcp` 建新分頁。

3. **確認測試步驟範圍** — 如果使用者的測試文件有多個步驟，確認要執行哪些。本 Skill 涵蓋前三步：Login → Loading Page → Basic Game Play。

---

## 測試流程

### Step 1: Login（登入）

登入頁面是標準 HTML，使用 DOM 操作：

1. **導航至測試工具頁**
   ```
   navigate → {TEST_URL}/index
   ```

2. **驗證頁面載入** — 確認標題包含「遊戲測試工具」

3. **截圖記錄** — 對當前頁面截圖留證

4. **讀取表單結構** — 使用 `read_page` 或 `javascript_tool` 取得所有 `<select>` 和 `<input>` 元素，確認欄位索引：
   - `select` nth(0) = Agent
   - `select` nth(1) = Sub Agent（此欄位依賴 Agent 選擇，需等待動態載入）
   - `input[type="text"]` 第一個 = Account
   - `select` nth(3) = Game ID
   - `select` nth(4) = Language
   - `select` nth(5) = Kick Flow
   - `select` nth(6) = Launch Type

5. **設定表單值** — 重要：不要假設預設值正確，必須主動設定每個欄位：
   - 先設定 Agent → **等待 2~3 秒**讓 Sub Agent 選項動態載入 → 再設定 Sub Agent
   - 使用 `form_input` 或 `javascript_tool` 設定 select 值
   - Account 欄位用 `form_input` 填入

6. **驗證設定值** — 設定後截圖，用 JavaScript 讀回各欄位值確認正確

7. **點擊 Login** — 找到 `button:has-text("Login")` 並點擊

8. **等待遊戲頁面開啟** — Login 會透過 `window.open` 開啟新分頁。等待 5~10 秒後，用 `tabs_context_mcp` 檢查是否有新的 "Vertex Play" 分頁出現

9. **驗證遊戲頁面** — 切換到新分頁，確認標題為 "Vertex Play"，截圖留證

**Login 結果判定**:
- PASS: 成功開啟新分頁且標題為 "Vertex Play"
- FAIL: 未開啟新分頁、API 回傳錯誤、或逾時

---

### Step 2: Loading Page（載入頁面驗證）

遊戲載入後會顯示說明頁面，這部分是 Canvas 渲染，需要座標點擊。

詳細的座標參考值請見 `skill.md`。

**⚡ 進入 Loading Page 後，在做任何座標點擊前，必須先執行「座標校準流程」（見上方「關鍵架構知識」第 2 點）。**

1. **調整視窗大小** — 用 `resize_window(430, 932)` 設定手機模式（實際可能為 ~500×697）

2. **偵測 iframe 位置** — 用 JavaScript 取得 iframe 的 BoundingClientRect，記錄 `left, top, width, height`

3. **截圖 Loading Page 第 1 頁** — 記錄初始畫面

4. **點擊右箭頭** — 使用**換算後的座標**點擊右箭頭切換到第 2 頁
   - 如果點擊無反應，用 `zoom` 放大右箭頭區域（約 iframe 右側邊緣 ± 50px 範圍），從放大圖確認按鈕中心座標
   - 箭頭外觀：**深色圓底 + 黃色 ">" 箭頭圖標**
   - 等待 1.5~2 秒讓動畫完成
   - 截圖第 2 頁

5. **驗證頁面切換** — 目視比較截圖（或用 zoom 檢查局部），確認內容有變化

6. **繼續點擊右箭頭** → 第 3 頁，截圖並驗證

7. **點擊左箭頭** — 確認可以回到前一頁，截圖並驗證
   - 左箭頭外觀：**深色圓底 + 黃色 "<" 箭頭圖標**

8. **點擊 PLAY REAL** — 使用換算後的座標點擊 PLAY REAL 按鈕（綠色大按鈕）
   - 等待 5~8 秒讓遊戲主畫面載入
   - 截圖確認已進入遊戲主畫面（應看到麻將牌盤 + 底部 BALANCE/WIN/BET 資訊列）

**Loading Page 結果判定**:
- PASS: 箭頭切換正常（畫面有變化）、PLAY REAL 成功進入遊戲主畫面
- FAIL: 箭頭點擊無反應、畫面未切換、進入遊戲失敗

---

### Step 3: Basic Game Play（基本遊戲玩法）

遊戲主畫面全部在 Canvas 上，底部有資訊列顯示 BALANCE / WIN / BET。

1. **讀取遊戲數值** — 從截圖目視讀取底部資訊列的數值：
   - 底部資訊列格式：`[幣種] [BALANCE]    [WIN]    [BET]`
   - 例如：`PHP  9,999,992.19    0.00    0.5`
   - BALANCE 是最大的數字、BET 是最小的、WIN 在中間
   - 如果數字不清楚，用 `zoom` 放大底部區域確認

   > **重要**：不要嘗試用 `get_page_text` 或 `javascript_tool` 讀取遊戲數值——因為跨域 iframe 限制，這些方法無法取得 canvas 內的數據。直接從截圖讀取是最可靠的方式。

2. **記錄 SPIN 前的 BALANCE**

3. **點擊 SPIN 按鈕** — 使用換算後的座標點擊（參見 `skill.md`）
   - SPIN 按鈕外觀：底部中央的**大型圓形青綠色按鈕**，有旋轉箭頭圖標

4. **等待動畫結束** — 等待 6~8 秒讓轉盤停止

5. **讀取 SPIN 後數值** — 截圖並從截圖目視讀取 BALANCE / WIN / BET

6. **驗證 BALANCE 計算**:
   - 公式: `BALANCE_after ≈ BALANCE_before - BET + WIN`
   - 容許浮點誤差 ±0.10
   - 無中獎時 WIN = 0，BALANCE 應減少 BET 的金額
   - 有中獎時 WIN > 0，BALANCE 應為 `前值 - BET + WIN`

7. **重複 SPIN** — 至少要驗證：
   - 一次無中獎（WIN = 0）：確認 BALANCE 正確扣除 BET
   - 一次有中獎（WIN > 0）：確認 BALANCE 正確加上 WIN
   - 如果連續 15 次都沒中獎，記錄警告但不判定為 FAIL

8. **截圖關鍵時刻** — 至少截圖：前 2 次 SPIN 的前後狀態、每次中獎的畫面、最終狀態

**Basic Game Play 結果判定**:
- PASS: BALANCE 計算正確（誤差 < 0.10）、轉盤正常停止
- FAIL: BALANCE 計算錯誤、轉盤未停止、頁面崩潰

---

## 測試報告輸出

測試完成後，在對話中輸出 Markdown 格式的測試摘要：

```markdown
## QA 測試報告 — {遊戲名稱} ({GameID})

**測試日期**: YYYY-MM-DD
**測試網址**: {TEST_URL}
**測試帳號**: {Account}

### 測試結果摘要

| 步驟 | 測試項目 | 結果 | 備註 |
|------|----------|------|------|
| 1 | Login | PASS/FAIL | ... |
| 2 | Loading Page — 箭頭切換 | PASS/FAIL | ... |
| 2 | Loading Page — PLAY REAL | PASS/FAIL | ... |
| 3 | Basic Game Play — SPIN (無中獎) | PASS/FAIL | BALANCE: before → after |
| 3 | Basic Game Play — SPIN (有中獎) | PASS/FAIL | WIN: X, BALANCE: before → after |

### SPIN 紀錄

| # | BALANCE (前) | BET | WIN | BALANCE (後) | 期望值 | 誤差 | 結果 |
|---|-------------|-----|-----|-------------|--------|------|------|
| 1 | 9,999,998.88 | 0.50 | 0.00 | 9,999,998.38 | 9,999,998.38 | 0.00 | PASS |
| ... | ... | ... | ... | ... | ... | ... | ... |
```

---

## 重要注意事項

- **座標校準是必要步驟，不是可選的**: 每次進入遊戲頁面後，第一件事就是用 JavaScript 偵測 iframe 位置，然後根據 iframe 的 `left, top, width, height` 換算所有座標。永遠不要直接使用 `skill.md` 中的原始座標——那些是基於 430×932 理想 viewport 的參考值。
- **視窗 resize 結果不可預測**: `resize_window(430, 932)` 的實際結果可能是 500×697 或其他尺寸，取決於瀏覽器的最小寬度限制。所以一定要在 resize 後用 JavaScript 確認 `window.innerWidth` 和 `window.innerHeight` 的真實值。
- **等待時間**: 遊戲載入和動畫需要等待。如果操作太快會導致失敗。寧可多等幾秒也不要跳過等待。
- **新分頁處理**: Login 後遊戲會在新分頁開啟。要用 `tabs_context_mcp` 找到新分頁的 tabId，後續操作都在新分頁上進行。
- **多遊戲適用**: 不同遊戲的 Canvas 座標可能不同。首次測試新遊戲時，先截圖確認 UI 佈局，再決定座標。Loading Page 的箭頭和 PLAY REAL 位置通常是固定的，但 SPIN 按鈕位置可能因遊戲而異。

---

## 與專案其他文件的關係

| 文件 | 關係 |
|------|------|
| **CLAUDE.md** | 執行指令集（RunTest、Manual 等），會調用本 Skill |
| **skill.md** | 通用規格（座標表、異常處理規則），本 Skill 參考其中的座標 |
| **scripts/manifest.json** | 測試腳本註冊表，定義測試步驟 |
| **specs/manifest.json** | Specs 動態版本控制，每次執行前檢測是否有新的測試規格 |

---

**版本歷史**：
- v1.0 (2026-03-05)：初版建立，從全域 h5-game-qa skill 移入專案本地
