#!/bin/bash
# 每日記憶備份 - 只備份公開版
# 自動排除敏感資訊

cd ~/.openclaw/workspace-dev

# 檢查是否有變更
git status --short > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # 有變更才提交
    git add MEMORY-public.md .gitignore scripts/ webapp/ stock-bot/investment.db 2>/dev/null
    
    # 檢查是否有東西要提交
    if git diff --cached --quiet; then
        echo "沒有變更需要備份"
    else
        git commit -m "每日自動備份 - $(date '+%Y-%m-%d %H:%M')"
        git push origin gh-pages
        echo "備份完成: $(date)"
    fi
else
    echo "Git 倉庫有問題"
fi
