#!/bin/bash
# 綜合新聞摘要 - 每日 08:30
# 多來源備援機制

BOT_TOKEN="8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID="6490946430"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

log "📰 開始獲取綜合新聞..."

NEWS_SFN=""
NEWS_BEST=""
NEWS_TOP=""

# 來源1: Spaceflight News
log "取得 Spaceflight News..."
SFN=$(curl -s --max-time 8 "https://api.spaceflightnewsapi.net/v4/articles/?limit=3" 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$SFN" ]; then
    count=0
    while [ $count -lt 3 ]; do
        title=$(echo "$SFN" | jq -r ".results[$count].title" 2>/dev/null)
        if [ "$title" != "null" ] && [ -n "$title" ]; then
            NEWS_SFN+="• $title\n"
        fi
        count=$((count + 1))
    done
fi

# 來源2: Hacker News Best
log "取得 Hacker News Best..."
BEST_IDS=$(curl -s --max-time 8 "https://hacker-news.firebaseio.com/v0/beststories.json" 2>/dev/null | jq -r '.[]' | head -5)
count=0
for id in $BEST_IDS; do
    if [ $count -ge 3 ]; then break; fi
    title=$(curl -s --max-time 5 "https://hacker-news.firebaseio.com/v0/item/${id}.json" 2>/dev/null | jq -r '.title')
    if [ "$title" != "null" ] && [ -n "$title" ]; then
        NEWS_BEST+="• $title\n"
        count=$((count + 1))
    fi
done

# 來源3: Hacker News Top
log "取得 Hacker News Top..."
TOP_IDS=$(curl -s --max-time 8 "https://hacker-news.firebaseio.com/v0/topstories.json" 2>/dev/null | jq -r '.[]' | head -8)
count=0
for id in $TOP_IDS; do
    if [ $count -ge 4 ]; then break; fi
    title=$(curl -s --max-time 5 "https://hacker-news.firebaseio.com/v0/item/${id}.json" 2>/dev/null | jq -r '.title')
    if [ "$title" != "null" ] && [ -n "$title" ]; then
        NEWS_TOP+="• $title\n"
        count=$((count + 1))
    fi
done

# 組合訊息
message="📰 *綜合新聞摘要*

*🌍 國際/科技頭條:*
$NEWS_BEST

*💻 熱門技術新聞:*
$NEWS_TOP

*🚀 太空科技:*
$NEWS_SFN

---
🔄 更新於 $(date '+%Y-%m-%d %H:%M')"

log "發送至 Telegram..."
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${message}" \
    -d "parse_mode=Markdown" > /dev/null

log "✅ 完成！"
