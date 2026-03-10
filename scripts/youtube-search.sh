#!/bin/bash
# YouTube 影片推薦 - 搜尋繁體中文內容
# 每日 10:30 發送

BOT_TOKEN="8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID="6490946430"

echo "🎬 開始搜尋 YouTube 影片..."

get_youtube_videos() {
    local query="$1"
    local count=3
    local encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query', safe=''))")
    curl -s "https://www.youtube.com/results?search_query=$encoded" 2>/dev/null | \
        grep -oP '"videoId":"\K[^"]+' | head -$count | sort -u
}

# 主題列表 - 繁體中文
declare -A TOPICS=(
    ["🤖 AI 人工智慧"]="AI 人工智慧"
    ["📈 股票投資理財"]="股票 投資"
    ["💻 科技趨勢"]="科技 趨勢"
    ["🏯 成都旅遊"]="成都 旅遊"
    ["🏔️ 冰島旅遊"]="冰島 旅遊"
)

message="🎬 *YouTube 影片推薦*

*今日熱門：*

"

for topic in "${!TOPICS[@]}"; do
    query="${TOPICS[$topic]}"
    message+="$topic
"
    
    video_ids=$(get_youtube_videos "$query")
    if [ -n "$video_ids" ]; then
        for vid in $video_ids; do
            message+="   ▶ https://youtu.be/$vid
"
        done
    else
        message+="   暫無結果
"
    fi
    message+="
"
done

message+="---
🔄 更新於 $(date '+%Y-%m-%d %H:%M')"

echo "$message"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${message}" \
    -d "parse_mode=Markdown" > /dev/null

echo "✅ 完成！"
