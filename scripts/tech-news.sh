#!/bin/bash
# 科技新聞摘要 - 每日 10:00
# 整合多個免費新聞 API

BOT_TOKEN="8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID="6490946430"

echo "💻 開始獲取科技新聞..."

NEWS_TECH=""
NEWS_TOP=""

# 1. Hacker News Best (最佳)
BEST_IDS=$(curl -s --max-time 10 "https://hacker-news.firebaseio.com/v0/beststories.json" 2>/dev/null | jq -r '.[]' | head -10)
count=0
for id in $BEST_IDS; do
    if [ $count -ge 5 ]; then break; fi
    item=$(curl -s --max-time 5 "https://hacker-news.firebaseio.com/v0/item/${id}.json" 2>/dev/null)
    title=$(echo "$item" | jq -r '.title')
    score=$(echo "$item" | jq -r '.score')
    if [ -n "$title" ] && [ "$title" != "null" ]; then
        NEWS_TECH+="• $title ($score)\n"
        count=$((count + 1))
    fi
done

# 2. Hacker News Top (熱門)
TOP_IDS=$(curl -s --max-time 10 "https://hacker-news.firebaseio.com/v0/topstories.json" 2>/dev/null | jq -r '.[]' | head -10)
count=0
for id in $TOP_IDS; do
    if [ $count -ge 5 ]; then break; fi
    item=$(curl -s --max-time 5 "https://hacker-news.firebaseio.com/v0/item/${id}.json" 2>/dev/null)
    title=$(echo "$item" | jq -r '.title')
    score=$(echo "$item" | jq -r '.score')
    if [ -n "$title" ] && [ "$title" != "null" ]; then
        NEWS_TOP+="• $title ($score)\n"
        count=$((count + 1))
    fi
done

message="💻 *科技新聞摘要*

*Hacker News 最佳:*
$NEWS_TECH

*熱門趨勢:*
$NEWS_TOP

---
🔄 更新於 $(date '+%Y-%m-%d %H:%M')"

echo "$message"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${message}" \
    -d "parse_mode=Markdown" > /dev/null

echo "✅ 完成！"
