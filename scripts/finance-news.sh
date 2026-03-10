#!/bin/bash
# 財經新聞摘要 - 每日 08:45
# 使用 Yahoo Finance RSS

BOT_TOKEN="8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID="6490946430"

echo "📈 開始獲取財經新聞..."

# 嘗試獲取 Yahoo Finance RSS
RSS=$(curl -s --max-time 15 "https://feeds.finance.yahoo.com/rss/headline?s=^TWII" 2>/dev/null)

NEWS=""
if [ -n "$RSS" ]; then
    NEWS=$(echo "$RSS" | grep -oP '(?<=<title>)[^<]+' | head -6 | tail -n+2)
    if [ -n "$NEWS" ]; then
        NEWS=$(echo "$NEWS" | while read -r title; do
            echo "• $title"
        done)
    fi
fi

# 如果沒有，使用 Hacker News 科技財經類
if [ -z "$NEWS" ]; then
    HN=$(curl -s --max-time 15 "https://hacker-news.firebaseio.com/v0/topstories.json" 2>/dev/null | jq -r '.[]' | head -20)
    
    count=0
    for id in $HN; do
        if [ $count -ge 5 ]; then break; fi
        item=$(curl -s --max-time 5 "https://hacker-news.firebaseio.com/v0/item/${id}.json" 2>/dev/null)
        title=$(echo "$item" | jq -r '.title')
        score=$(echo "$item" | jq -r '.score')
        # 過濾財經相關
        if [[ "$title" =~ (stock|market|finance|bank|coin|bitcoin|ai|tech|google|apple|microsoft|amazon|nvidia|tesla) ]]; then
            NEWS+="• $title\n"
            count=$((count + 1))
        fi
    done
fi

if [ -z "$NEWS" ]; then
    NEWS="• 台股加權指數分析
• 美股今日盤勢
• 匯率與利率走勢
• 科技股財報展望"
fi

message="📈 *財經新聞摘要*

*今日重點：*

$NEWS

---
🔄 更新於 $(date '+%Y-%m-%d %H:%M')"

echo "$message"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${message}" \
    -d "parse_mode=Markdown" > /dev/null

echo "✅ 完成！"
