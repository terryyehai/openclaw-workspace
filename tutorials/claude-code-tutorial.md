# Claude Code 繁體中文教學

> 來源：[Anthropic Academy - Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action)
> 翻譯：小蝦 🦐
> 日期：2026-03-09

---

## 目錄

1. [什麼是 Claude Code？](#1-什麼是-claude-code)
2. [Claude Code 基礎設定](#2-claude-code-基礎設定)
3. [工具使用系統](#3-工具使用系統)
4. [上下文管理技巧](#4-上下文管理技巧)
5. [視覺溝通工作流](#5-視覺溝通工作流)
6. [自定義自動化](#6-自定義自動化)
7. [MCP 伺服器](#7-mcp-伺服器)
8. [GitHub 整合](#8-github-整合)
9. [Hooks 與 SDK](#9-hooks-與-sdk)

---

## 1. 什麼是 Claude Code？

### 1.1 編碼助手的基礎

Claude Code 是一個 AI 編碼助手，能夠：
- 讀取和分析程式碼
- 執行終端命令
- 瀏覽器和檔案操作
- 自動完成開發任務

### 1.2 核心能力

| 能力 | 說明 |
|------|------|
| **對話理解** | 理解自然語言指令 |
| **工具調用** | 使用終端、檔案、瀏覽器等工具 |
| **上下文管理** | 維護專案相關資訊 |
| **MCP 擴展** | 透過 MCP 伺服器擴展功能 |

---

## 2. Claude Code 基礎設定

### 2.1 安裝

```bash
# macOS / Linux
curl -fsSL https://CLAUDE.md/install.sh | sh

# 或使用 Homebrew
brew install claude-cli
```

### 2.2 初始化

```bash
claude auth login
claude init
```

### 2.3 基本配置

建立 `CLAUDE.md` 檔案在專案根目錄：

```markdown
# 專案設定

## 語言
繁體中文

## 框架
React, Node.js

## 常用命令
npm run dev
npm test
```

---

## 3. 工具使用系統

### 3.1 內建工具

Claude Code 提供的工具：

| 工具 | 功能 |
|------|------|
| `Bash` | 執行終端命令 |
| `Read` | 讀取檔案 |
| `Edit` | 編輯檔案 |
| `Write` | 寫入檔案 |
| `Glob` | 搜尋檔案 |
| `Grep` | 搜尋內容 |
| `WebFetch` | 擷取網頁 |
| `Browser` | 瀏覽器自動化 |

### 3.2 工具組合使用

範例：建立一個 React 元件

```
帮我建立一个 Button 组件，包含：
- 基本按钮样式
- hover 效果
- TypeScript 类型
```

Claude Code 會：
1. 搜尋現有元件結構
2. 讀取相關檔案
3. 建立新元件
4. 寫入檔案

---

## 4. 上下文管理技巧

### 4.1 上下文的來源

| 來源 | 說明 |
|------|------|
| 對話歷史 | 目前的對話內容 |
| 專案檔案 | 讀取過的檔案 |
| 相關檔案 | 語法上下文 |
| 外部資源 | 網頁內容 |

### 4.2 有效管理上下文

**使用 `/compact` 命令**
```
/compact - 壓縮上下文，保留重要資訊
```

**使用 `/clear` 命令**
```
/clear - 清除對話歷史
```

**指定具體範圍**
```
"只檢查 src/components 資料夾"
```

---

## 5. 視覺溝通工作流

### 5.1 截圖溝通

可以截圖 UI 介面，讓 Claude Code 理解視覺設計：

1. 截圖 UI 設計
2. 傳給 Claude Code
3. 描述你想要什麼改變

### 5.2 差異比對

```
"这个新的设计稿和之前的有什麼不同？"
```

---

## 6. 自定義自動化

### 6.1 自定義指令

在 `CLAUDE.md` 中加入：

```markdown
## 自定義指令

### /test
執行所有測試並報告結果

### /build
建置專案並檢查錯誤

### /review
Code Review 當前變更
```

### 6.2 常用腳本

```bash
# .claude/scripts/test.sh
#!/bin/bash
npm test -- --coverage
```

---

## 7. MCP 伺服器

### 7.1 什麼是 MCP？

**Model Context Protocol (MCP)** 是一個開放協定，讓 AI 能夠連接外部工具和服務。

### 7.2 常用 MCP 伺服器

| 伺服器 | 功能 |
|--------|------|
| `filesystem` | 檔案系統操作 |
| `browser` | 瀏覽器自動化 |
| `git` | Git 操作 |
| `database` | 資料庫查詢 |
| `search` | 網路搜尋 |

### 7.3 設定範例

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
  }
}
```

---

## 8. GitHub 整合

### 8.1 自動化 Code Review

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Claude Code Review
        run: |
          claude review --pr ${{ github.event.pull_request.number }}
```

### 8.2 Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
claude check --staged
```

---

## 9. Hooks 與 SDK

### 9.1 什麼是 Hooks？

Hooks 讓你自定義 Claude Code 的行為：

| Hook | 時機 |
|------|------|
| `PreToolUse` | 工具執行前 |
| `PostToolUse` | 工具執行後 |
| `Notification` | 通知時 |
| `Stop` | 對話結束時 |

### 9.2 SDK 使用

```javascript
// claude-sdk.js
const { Claude } = require('@anthropic-ai/claude-sdk');

const claude = new Claude({
  apiKey: process.env.ANTHROPIC_API_KEY
});

await claude.messages.create({
  model: 'claude-3-opus-20240229',
  messages: [{ role: 'user', content: 'Hello!' }]
});
```

---

## 常見問題

### Q1: Claude Code 免費嗎？
> 有免費額度，升級請見 [官網定價](https://www.anthropic.com/pricing)

### Q2: 可以用在商業專案嗎？
> 可以，詳情閱讀 [使用條款](https://www.anthropic.com/legal)

### Q3: 如何設定繁體中文？
> 在對話中直接使用繁體中文即可

---

## 相關資源

- [官方文檔](https://docs.anthropic.com/en/docs/claude-code/overview)
- [GitHub](https://github.com/anthropics/claude-code)
- [Discord 社群](https://discord.gg/anthropic)

---

*教學內容翻譯自 Anthropic Academy 官方課程*
