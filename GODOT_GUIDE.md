# 🎮 Godot 遊戲開發規範

## 避免常見錯誤

### 1. 繪圖函數正確用法
```gdscript
# ❌ 錯誤 - 太多參數
draw_circle(Vector2(x, y), radius, color, false, 2)

# ✅ 正確
draw_circle(Vector2(x, y), radius, color)
draw_arc(Vector2(x, y), radius, 0, TAU, 32, Color.WHITE, 2.0)
```

### 2. 空值處理
```gdscript
# ❌ 錯誤
var x = nil

# ✅ 正確
var x = null
if x == null:
```

### 3. 變數初始化
```gdscript
# 確保畫布初始化完成後再繪製
func _ready():
    set_timeout(func(): draw(), 100)  # 延遲繪製

# 檢查變數存在
func draw():
    if ctx == null:
        return
    # 繪製邏輯
```

### 4. 場景初始化順序
```gdscript
func initGame(container):
    # 1. 創建 DOM
    content.innerHTML = "..."
    
    # 2. 初始化數據
    initBoard()
    
    # 3. 延遲設定畫布大小
    set_timeout(func():
        resizeCanvas()
        draw()
    , 100)
```

## 導出檢查清單
- [ ] `--script-check` 語法檢查
- [ ] 所有 draw_circle/arc 語法正確
- [ ] null 而不是 nil
- [ ] 畫布在 DOM 渲染後初始化

## 常用代碼片段
```gdscript
# 繪製圓形帶邊框
func _draw_piece(x, y, color):
    draw_circle(Vector2(x, y), radius, color)
    draw_arc(Vector2(x, y), radius, 0, TAU, 32, Color.WHITE, 2.0)

# 安全的變數訪問
func get_piece(x, y):
    if y < 0 or y >= board.size():
        return null
    if x < 0 or x >= board[y].size():
        return null
    return board[y][x]
```
