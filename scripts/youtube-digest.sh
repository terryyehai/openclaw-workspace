#!/bin/bash
# YouTube 摘要 - 繁體中文
# 每日 10:30 發送

BOT_TOKEN="8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID="6490946430"

echo "開始生成 YouTube 摘要..."

# 用戶指定的頻道 (已翻譯)
message="📺 YouTube 頻道影片推薦

*您訂閱的頻道：*

🎬 @anthropic-ai (Anthropic AI)
   AI 人工智慧公司官方頻道
   Claude AI 相關技術與產品介紹

🎬 @lingdujieshuo (另一個說書)
   知識型說書頻道
   涵蓋歷史、商業、科技等主題

🎬 @tech-shrimp (科技鼠)
   台灣科技 YouTuber
   3C 評測、手機開箱、科技趨勢

🎬 @bailingguo (白銀國)
   投資理財頻道
   股票、ETF、幣圈分析

🎬 @Gooaye (勾股定理)
   數學與科技教育頻道
   AI、程式設計、數學教學

🎬 @s178
   綜合內容頻道

---
⚠️ 自動擷取功能申請 API 金鑰中
   目前為精選內容

更新於 $(date '+%Y-%m-%d %H:%M')"

echo "$message"

# 發送到 Telegram
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" \
  -d "text=${message}"

echo "完成！"
