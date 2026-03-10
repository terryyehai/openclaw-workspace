# 專案級 Skills（Project-Level Skills）

> 本目錄存放專案特定的測試工具與執行指南。
> 與全域 Skills 不同，這些是為本專案量身定做的。

---

## 📋 Skills 清單

### H5_GAME_QA_GUIDE.md
- **用途**：Chrome 瀏覽器自動化測試指南
- **涵蓋**：Login → Loading Page → Basic Game Play 三大步驟
- **重點**：iframe 架構、座標校準、動態座標計算公式
- **適用場景**：需要在 Chrome 瀏覽器上執行 H5 遊戲的 QA 自動化測試
- **參考文件**：
  - `skill.md`（座標表、異常處理規則）
  - `CLAUDE.md`（執行指令集）
- **最後更新**：2026-03-05

---

## 🔗 如何使用

### 在執行自動化測試時
```
1. 檢查 CLAUDE.md 的「動態記憶更新機制」(Specs Init)
   → 自動讀取 specs/manifest.json，檢測新增/修改的規格

2. 執行 RunTest <script-id>
   → 啟動 Subagent，按照 scripts/*.xlsx 的 Steps sheet 執行

3. 遇到 iframe 座標問題
   → 參考本目錄下 H5_GAME_QA_GUIDE.md 的「座標校準流程」

4. 完成測試後
   → 自動輸出測試報告（見 H5_GAME_QA_GUIDE.md 的「測試報告輸出」）
```

### 擴展新的 Project-Level Skills
```
1. 新增 {SkillName}.md 到本目錄
2. 在本 README 中新增條目
3. 在 CLAUDE.md 中新增參考指令（如需要）
4. 更新 manifest.json 版本
```

---

## 📊 Skills 架構圖

```
Project-Level Skills (skills/)
├── H5_GAME_QA_GUIDE.md
│   ├── 參考座標 ← skill.md
│   ├── 異常處理 ← skill.md
│   └── 執行時機 ← CLAUDE.md (RunTest)
│
└── [Future Skills]
    ├── API_TEST_GUIDE.md
    ├── PERFORMANCE_BENCHMARK.md
    └── ...

Global Skills
├── anthropic-skills:h5-game-qa （全域版，已被本地版本替代）
├── anthropic-skills:docx
├── anthropic-skills:xlsx
└── ...
```

---

## 🔄 與其他文件的關係

| 文件 | 層級 | 用途 | 更新頻率 |
|------|------|------|:--:|
| **H5_GAME_QA_GUIDE.md** | 專案本地 | 執行指南 | 低 |
| **skill.md** | 專案全局 | 技術規格（座標、異常處理） | 低 |
| **CLAUDE.md** | 專案全局 | 執行指令集、初始化邏輯 | 中 |
| **specs/manifest.json** | 動態 | 規格版本控制、自動檢測 | **高** |
| **scripts/manifest.json** | 靜態 | 腳本註冊表 | 低 |

---

## 💡 最佳實踐

1. **本地化 Project-Level Skills**
   - 優點：版本控制與專案綁定，便於迭代
   - 優點：避免全域 Skills 升級時的衝突
   - 優點：便於團隊成員檢查與改進

2. **保持 skill.md 穩定**
   - 只在重大版本變更或異常處理規則改變時更新
   - 記錄版本歷史於檔案頂部

3. **動態規格用 specs/manifest.json**
   - 新遊戲規格、測試流程更新 → specs/
   - 執行時自動檢測版本 (Specs Init)

4. **工具特定的指南用 Project-Level Skills**
   - Chrome 自動化 → H5_GAME_QA_GUIDE.md
   - API 測試 → API_TEST_GUIDE.md（未來）
   - 性能測試 → PERFORMANCE_BENCHMARK.md（未來）

---

**資料夾建立日期**：2026-03-05
**維護責任**：Terry（QA Engineer & Full Stack Developer）
