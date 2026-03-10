**DEMO MODE**

**遊戲規格說明文件**

Specification & Testing SOP

文件版本：v1.0

更新日期：2026-03-05

1\. 遊戲功能選擇頁面

玩家從 QA 測試工具登入後，進入該遊戲的功能選擇頁面。此頁面提供 DEMO MODE
與 PLAY REAL 兩個主要入口。

![SLOT
遊戲功能選擇介面](media/6843a3be532d356ecc3bafb763fb446382706c3f.jpeg "遊戲功能選擇頁面"){width="1.875in"
height="2.9791666666666665in"}

*▲ 遊戲功能選擇頁面示意圖*

1.1 頁面功能說明

  -------------- ---------------------------------------------------------------------
  **功能項目**   **說明**
  DEMO MODE      點擊後進入 SLOT DEMO 模式頁面，玩家可體驗遊戲功能而無需投入真實金額
  PLAY REAL      點擊後進入正式遊戲頁面，使用真實金額進行遊玩
  -------------- ---------------------------------------------------------------------

1.2 注意事項

⚠ 不同遊戲的頁面按鈕文字依語言設定而變化（例：English → PLAY
REAL；繁體中文 → 開始遊戲）

⚠ 該頁面可能包含多頁遊戲特色說明，可透過左右翻頁按鈕進行切換

2\. DEMO MODE 遊戲頁面

進入 DEMO MODE 後，遊戲頁面會顯示 DEMO MODE 字樣，並包含 PLAY REAL 與
FEATURE LIST 兩個主要控制按鈕。

![DEMO MODE
遊戲介面示意](media/4c790011677f8d76e411e29b99100f6a13c62063.jpeg "DEMO MODE 遊戲頁面"){width="1.875in"
height="2.9791666666666665in"}

*▲ DEMO MODE 遊戲頁面示意圖*

2.1 主要功能按鈕

**PLAY REAL 按鈕**

![PLAY REAL
按鈕圖示](media/9c5e90b29207ef91bb7f6288dea26eb1755179ff.jpeg "PLAY REAL 按鈕"){width="1.625in"
height="0.59375in"}

點擊後會離開 DEMO MODE 模式，前往正式遊戲頁面進行真實金額遊玩。

**FEATURE LIST 按鈕**

![FEATURE LIST
按鈕圖示](media/2ff0c6eab19fcdcd77dc89aaeab22a48a68ffaef.jpeg "FEATURE LIST 按鈕"){width="0.9270833333333334in"
height="0.3854166666666667in"}

點擊後展示遊戲特色清單。點擊各個 FEATURE 項目（FEATURE 1～FEATURE
N）會觸發對應的特色演示流程。

**FEATURE 1～N 演示圖示示例**

![FEATURE 1
圖示](media/62a9eadab29b3cc6ada945e6f7d8ffa4c28abd0e.jpeg "FEATURE 1"){width="0.9375in"
height="0.3854166666666667in"} ![FEATURE 2
圖示](media/73452d306dcc84303a9227f73d027447cf1a0eea.jpeg "FEATURE 2"){width="0.9375in"
height="0.3854166666666667in"} ![FEATURE 3
圖示](media/5104e4a4e878fb05227b1d747f04dbd621f8e8ed.jpeg "FEATURE 3"){width="0.9375in"
height="0.3854166666666667in"}

3\. DEMO MODE 測試流程（SOP）

以下為完整的 DEMO MODE 功能測試流程，確保遊戲所有功能正常運作。

3.1 測試步驟清單

  ---------- --------------------------- ---------------------------------------------------------------------------------------
  **步驟**   **操作內容**                **預期結果與驗證點**
  1          DEMO MODE 中進行多場 SPIN   Credit 隨著 BET 值正確扣除；搭配不同的 BET 金額，驗證每場 SPIN 的扣款計算正確
  2          FEATURE 1～N 全部執行一輪   每個 FEATURE 點擊後滾輪開始滾動，特色演示完整呈現，畫面完全靜止後可執行下一個 FEATURE
  3          驗證設定功能                SOUND、INFO、AUTO、CLOSE 功能都能正常操作，無異常提示或卡頓
  4          點擊 PLAY REAL              成功跳轉至正式遊戲頁面，頁面不再顯示 DEMO MODE 標示，進入真實金額遊玩模式
  ---------- --------------------------- ---------------------------------------------------------------------------------------

3.2 各步驟詳細說明

**Step 1：DEMO MODE SPIN 與 BALANCE 驗算**

在 DEMO MODE 進行至少 3～5 場 SPIN，每場使用不同的 BET 金額。驗證 Credit
扣除是否與 BET 金額一致，例如：Original Credit 100,000、BET 100、Spin 後
Credit 應為 99,900。若遊戲有中獎，WIN 金額應正確累加至 Credit。

**Step 2：FEATURE 演示流程**

依次點擊 FEATURE 1～N（實際數量由遊戲決定），每個 FEATURE 點擊後： •
滾輪開始自動滾動 • 特色視覺效果呈現（如免費遊戲、倍數加成等） •
等待滾輪完全停止（動畫結束） • 驗證無卡頓或異常行為

**Step 3：設定功能驗證**

完成 FEATURE 演示後，驗證以下設定功能是否可用： • SOUND：音效開/關切換 •
INFO：遊戲資訊/規則說明 • AUTO：自動遊玩模式 • CLOSE：關閉/返回按鈕

**Step 4：轉換至正式模式**

點擊 PLAY REAL 按鈕，確認遊戲頁面跳轉至正式遊戲頁面。DEMO MODE
字樣應完全消失，玩家進入真實金額投注模式。

3.3 測試注意事項

⚠ 若 FEATURE 演示中出現掉卡現象，應截圖記錄，並關閉視窗後重新進入 DEMO
MODE

⚠ 若 Free SPIN 或 Feature 自動觸發，應等待完整演示結束，不中斷遊戲流程

⚠ 若遊戲 Session 被中斷（如網路異常、瀏覽器卡頓），應重新登入並從
Loading Page 重新開始

⚠ 所有操作應記錄截圖或影片，便於 QA 報告和問題追蹤
