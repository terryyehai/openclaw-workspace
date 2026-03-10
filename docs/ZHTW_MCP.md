# zhtw-mcp 整合

## 安裝狀態

- **位置**: `~/.local/bin/zhtw-mcp`
- **版本**: Release build (10.5 MB)

## 使用方式

### 命令列
```bash
# 檢查檔案
zhtw-mcp lint file.md

# 自動修復
zhtw-mcp lint file.md --fix

# 預覽修復
zhtw-mcp lint file.md --fix --dry-run
```

### OpenClaw 整合

建立工具脚本 `~/.local/bin/zhtw-lint`:

```bash
#!/bin/bash
FILE="$1"
~/.local/bin/zhtw-mcp lint "$FILE"
```

## 規則類型

- **cross_strait**: 兩岸詞彙轉換
- **punctuation**: 標點符號（全形）
- **character**: 字形標準（教育部）
- **spacing**: CJK 與拉丁文字間距
- **casing**: 品牌名稱大小寫

## 常用轉換

| 中國用語 | 台灣用語 |
|---------|---------|
| 软件 | 軟體 |
| 内存 | 記憶體 |
| 进程 | 行程 |
| 并行 | 平行 |
| 渲染 | 算繪 |
| 遍历 | 走訪 |
