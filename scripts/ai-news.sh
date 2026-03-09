#!/bin/bash
# AI 新知推送 - 每日 10:00
# 近 24 小時最新 AI 消息

BOT_TOKEN="8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID="6490946430"

echo "開始獲取 AI 新知..."

# 使用 web search 找 AI 新聞
NEWS=$(curl -s "https://ddg-api.vercel.app/search?q=AI artificial intelligence news 2025&format=json&num=15" 2>/dev/null | jq -r '.[] | select(.title != null) | "\n📰 \(.title)\n🔗 \(.url)"' 2>/dev/null | head -20)

if [ -z "$NEWS" ]; then
    # 備用：用 Bing RSS
    NEWS=$(curl -s "https://www.bing.com/news/search?q=AI+artificial+intelligence&format=rss" 2>/dev/null | grep -oP '(?<=<title>)[^<]+' | head -15)
fi

# 生成訊息
message="🤖 *AI 新知 - 近24小時*

*最新 AI 應用與技術：*

$NEWS

---
🔄 自動生成於 $(date '+%Y-%m-%d %H:%M')"

echo "$message"

# 發送到 Telegram
echo "發送到 Telegram..."

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" \
  -d "text=${message}" \
  -d "parse_mode=Markdown"

echo "完成！"
