#!/bin/bash
# 中東 RSS 新聞
# 每日 08:30 發送

BOT_TOKEN="8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID="6490946430"

echo "開始獲取中東新聞..."

# RSS 來源
RSS_URLS=(
    "https://feeds.alarabiya.net/ala-foreign"
    "https://www.reutersagency.com/feed/?taxonomy=regions&post_type=best"
)

message="📰 *中東新聞摘要*

"

# 獲取 Al Arabiya
echo "獲取 Al Arabiya..."
articles=$(curl -s "${RSS_URLS[0]}" 2>/dev/null | grep -oP '<title><!\[CDATA\[[^]]+\]\]></title>' | head -5 | sed 's/<title><!\[CDATA\[//g; s/\]\]><\/title>//g')

if [ -n "$articles" ]; then
    message+="*Al Arabiya:*
"
    echo "$articles" | while read title; do
        if [ -n "$title" ]; then
            message+="• $title
"
        fi
    done
    message+="
"
fi

message+="---
🔄 更新於 $(date '+%Y-%m-%d %H:%M')"

echo "$message"

# 發送到 Telegram
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${message}" \
    -d "parse_mode=Markdown"

echo "完成！"
