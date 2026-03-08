#!/bin/bash
# OpenClaw 對話記憶備份腳本
# 每日自動備份

BACKUP_DIR="/home/terry/.openclaw/workspace-dev/backups"
SOURCE_DIR="$HOME/.openclaw/agents/dev/sessions"
DATE=$(date "+%Y-%m-%d_%H%M%S")

# 創建備份目錄
mkdir -p "$BACKUP_DIR"

# 複製對話紀錄
if [ -f "$SOURCE_DIR/sessions.json" ]; then
    cp "$SOURCE_DIR/sessions.json" "$BACKUP_DIR/sessions_${DATE}.json"
    echo "sessions.json 已備份"
fi

if [ -f "$SOURCE_DIR"/*.jsonl ]; then
    cp "$SOURCE_DIR"/*.jsonl "$BACKUP_DIR/conversations_${DATE}.jsonl"
    echo "對話紀錄已備份"
fi

# 提交到 Git
cd /home/terry/.openclaw/workspace-dev
git add -A
git commit -m "Auto backup: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null
git push origin master 2>/dev/null || echo "Git push skipped (no changes or remote not set)"

# 保留所有備份（不刪除舊檔案）
# find "$BACKUP_DIR" -name "*.json*" -mtime +30 -delete
echo "所有備份都會保留"
