# OpenClaw + AI Operator 搬移指南

## 需要搬移的項目

### 1. 系統配置
```bash
~/.openclaw/                    # OpenClaw 主目錄
├── openclaw.json              # 設定檔
├── ai-operator/               # AI Operator 系統
│   ├── logs/                  # 日誌
│   ├── data/                  # 數據
│   ├── models/                # ML 模型
│   └── strategies/            # 策略
├── browser/                   # 瀏覽器資料
├── memory/                    # 記憶檔案
└── skills/                   # 自定義 Skills
```

### 2. 環境
- Python 虛擬環境（可重建）
- npm 全域套件（可重建）

---

## 搬移方式

### 方式一：完整備份（推薦）

#### 步驟 1：打包
```bash
# 壓縮整個 .openclaw 目錄
cd ~/.openclaw
tar -czvf openclaw_backup_$(date +%Y%m%d).tar.gz \
  --exclude='browser' \
  --exclude='*.log' \
  --exclude='node_modules' \
  .
```

#### 步驟 2：傳送到新電腦
```bash
# 方法 A：使用 scp
scp openclaw_backup_20260309.tar.gz user@new-computer:~/

# 方法 B：使用雲端硬碟
# 上傳到 Google Drive、Dropbox 等
```

#### 步驟 3：在新電腦還原
```bash
# 解壓縮
tar -xzvf openclaw_backup_20260309.tar.gz -C ~/.openclaw

# 重新建立符號連結（如需要）
```

---

### 方式二：分開備份

#### 1. 設定檔
```bash
# 獨立備份設定
cp ~/.openclaw/openclaw.json ~/openclaw_config.json
```

#### 2. AI Operator
```bash
# 備份 AI Operator 目錄
cp -r ~/.openclaw/ai-operator ~/ai_operator_backup
```

#### 3. 記憶檔案
```bash
# 備份記憶
cp -r ~/.openclaw/workspace-dev/memory ~/memory_backup
```

---

### 方式三：Git 版本控制

```bash
# 初始化 Git
cd ~/.openclaw/workspace-dev
git init
git add .
git commit -m "OpenClaw setup backup"

# 推送到 GitHub
git remote add origin https://github.com/你的帳號/openclaw-setup.git
git push -u origin main
```

在新電腦：
```bash
git clone https://github.com/你的帳號/openclaw-setup.git
```

---

## 新電腦還原步驟

### 1. 安裝 OpenClaw
```bash
# 安裝 OpenClaw
npm install -g openclaw

# 設定 API Keys
openclaw config set apiKeys.openai "你的Key"
```

### 2. 還原設定
```bash
# 還原設定檔
cp ~/openclaw_config.json ~/.openclaw/openclaw.json
```

### 3. 重建 Python 環境
```bash
# 建立虛擬環境
python3 -m venv ~/.openclaw/ai-operator

# 啟動並安裝套件
source ~/.openclaw/ai-operator/bin/activate
pip install -r requirements.txt
```

### 4. 設定排程
```bash
# 重新設定 cron 任務
openclaw cron list
```

---

## 檢查清單

搬移前檢查：
- [ ] 記錄所有 API Keys
- [ ] 記錄 cron 任務
- [ ] 記錄自定義 Skills
- [ ] 確認瀏覽器書籤
- [ ] 備份 Chrome Remote Debugging 設定

---

## 快速搬移腳本

```bash
#!/bin/bash
# backup_openclaw.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="$HOME/openclaw_backup_$DATE"

mkdir -p $BACKUP_DIR

# 1. 設定檔
cp ~/.openclaw/openclaw.json $BACKUP_DIR/

# 2. AI Operator
cp -r ~/.openclaw/ai-operator $BACKUP_DIR/

# 3. 記憶
cp -r ~/.openclaw/workspace-dev/memory $BACKUP_DIR/
cp -r ~/.openclaw/workspace-dev/MEMORY.md $BACKUP_DIR/
cp -r ~/.openclaw/workspace-dev/TOOLS.md $BACKUP_DIR/

# 4. Skills
cp -r ~/.openclaw/skills $BACKUP_DIR/

# 5. 打包
cd $HOME
tar -czvf openclaw_backup_$DATE.tar.gz openclaw_backup_$DATE/

echo "備份完成: openclaw_backup_$DATE.tar.gz"
```

---

*最後更新: 2026-03-09*
