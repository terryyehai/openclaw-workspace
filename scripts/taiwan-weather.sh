#!/bin/bash
# 台灣天氣通知
# 每日 09:00 發送

BOT_TOKEN="8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID="6490946430"
API_KEY="03645aaf773479b05850b3e30ee5b082"

echo "開始獲取天氣資料..."

get_weather() {
    local lat=$1
    local lon=$2
    
    data=$(curl -s "https://api.openweathermap.org/data/2.5/weather?lat=$lat&lon=$lon&units=metric&appid=$API_KEY&lang=zh_TW" 2>/dev/null)
    
    if [ -n "$data" ]; then
        echo "$data" | jq -r ".name, .main.temp, .weather[0].description, .main.humidity"
    fi
}

# 台灣城市 (lat, lon)
cities=("25.033:121.565" "24.146:120.684" "22.627:120.301")
names=("台北" "台中" "高雄")

message="🌤️ *台灣天氣預報*

"

for i in "${!cities[@]}"; do
    coords="${cities[$i]}"
    lat="${coords%%:*}"
    lon="${coords##*:}"
    name="${names[$i]}"
    
    data=$(get_weather "$lat" "$lon")
    
    if [ -n "$data" ]; then
        city_name=$(echo "$data" | head -1)
        temp=$(echo "$data" | sed -n '2p')
        desc=$(echo "$data" | sed -n '3p')
        humidity=$(echo "$data" | tail -1)
        
        message+="📍 *$city_name*
   溫度: ${temp}°C
   天氣: $desc
   濕度: ${humidity}%

"
    fi
done

message+="---
🔄 更新於 $(date '+%Y-%m-%d %H:%M')"

echo "$message"

# 發送到 Telegram
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${message}" \
    -d "parse_mode=Markdown"

echo "完成！"
