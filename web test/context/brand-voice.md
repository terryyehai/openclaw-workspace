# 品牌語氣與寫作風格 (Brand Voice & Tone)
本文件定義 QA 團隊對內外溝通、撰寫 Bug Report、SOP、測試報告及要求 AI 產出內容時的標準風格。

## 1. 語氣 (Tone)
- **客觀理性 (Objective)**：只描述事實、數據與系統行為，不夾帶個人情緒或主觀評價。
- **精準明確 (Precise)**：不留模糊空間。明確指出問題發生的環境、前置條件與觸發機率。
- **建設性 (Constructive)**：提出問題的同時，盡可能附帶 Log、截圖或初步排查線索，以協助開發者快速定位問題。
- **堅定且協作 (Firm but Collaborative)**：對品質標準踩線（Quality Gates）保持堅定，但在溝通態度上將 RD 視為解決問題的夥伴，而非對立面。

## 2. 用詞 (Vocabulary / Diction)
- **統一 QA 術語**：精準使用 Happy Path, Edge Case, Regression Test, Smoke Test, Flaky Test 等專業詞彙。
- **明確的狀態描述**：使用「無法重現 (Cannot Reproduce)」、「阻礙測試 (Blocked)」、「預期結果 (Expected)」、「實際結果 (Actual)」。
- **動作導向的動詞**：使用「點擊 (Click)」、「輸入 (Enter)」、「導覽至 (Navigate to)」、「驗證 (Verify)」、「斷言 (Assert)」。
- **量化指標**：盡可能數據化，例如「10 次測試中發生 3 次 (30% 重現率)」、「API 回應時間超過 2000ms」。

## 3. 禁用詞 (Banned Words)
- **模糊的頻率詞**：禁止使用「好像 (seems)」、「有時候 (sometimes)」、「偶爾 (occasionally)」。改用具體的重現機率或特定條件。
- **情緒化或批判性字眼**：禁止使用「寫得很爛」、「這邏輯不對」、「嚴重錯誤 (除非符合 Critical 定義)」。改用「與預期行為不符」、「發生 Crash」。
- **無意義的 AI 冗言贅字**：禁止輸出「這是一個很好的問題」、「總結來說」、「很高興為您服務」、「了解您的需求了」。直接給出結果。
- **不明確的代名詞**：盡量少用「這個」、「那個」，直接寫出具體的元件名稱或變數名稱。

## 4. 格式習慣 (Formatting Habits)
- **結構化優先**：捨棄長篇大論，全面採用條列式 (Bullet points) 或編號 (Numbered lists)。
- **Bug Report 標準格式**：永遠包含 `[環境/版本]`, `[前置條件]`, `[重現步驟]`, `[預期結果]`, `[實際結果]`。
- **UI 元件標示**：提及畫面上的按鈕或文字時，一律使用粗體或引號標示（例如：點擊 **[確認送出]** 按鈕）。
- **程式碼與 Log**：所有 Command line 指令、API Endpoint、JSON payload 或 Error Log，一律使用 Markdown 的程式碼區塊 (Code blocks) 包覆，並正確標註語言。
- **重點高亮**：使用 `**粗體**` 來強調關鍵字或危險警告，但不濫用。