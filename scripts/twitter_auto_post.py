#!/usr/bin/env python3
"""
Twitter Auto Poster - 每日自動發推 + 免費圖片
最終優化版
"""

import asyncio
import os
import random
import requests
from datetime import datetime
from playwright.async_api import async_playwright

# 免費圖片 URL (Unsplash)
FREE_IMAGE_URLS = [
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
    "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800",
    "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800",
    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
    "https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=800",
    "https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=800",
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800",
    "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800",
    "https://images.unsplash.com/photo-1497215842964-222b430dc094?w=800",
]

# 40+ 爆款內容模板
CONTENT_TEMPLATES = [
    """
🏆 40歲後最大的領悟

不是賺更多錢
而是【守住錢】

------------------------------------------
今天分享3個穩健理財原則：

1️⃣ 不懂不要碰
2️⃣ 分散風險
3️⃣ 長期持有

#理財 #投資 #中年人 #退休金
""",
    """
💰 退休金夠嗎？

很多人到了40歲才發現
退休金遠遠不夠...

------------------------------------------
3個行動建議：

✅ 每月固定存
✅ 買指數型基金
✅ 別把雞蛋放同一籃子

#理財 #退休金 #投資 #財務自由
""",
    """
⚠️ 給40歲以上的投資提醒

市場越是恐慌
越要保持冷靜

------------------------------------------
巴菲特說：
「別人貪婪時我恐懼
別人恐懼時我貪婪」

現在該貪婪還是恐懼？

#投資 #股市 #理財 #美股
""",
    """
📈 今天的市場觀察

川普政策影響全球市場
追蹤信號掌握先機

------------------------------------------
每晚8點更新
記得追蹤取得最新資訊

#市場分析 #投資 #川普密碼
""",
    """
💎 富人與窮人的差距

不在於收入多少
而在於【理財觀念】

------------------------------------------
有錢人懂的5個理財原則：

1. 收入減去儲蓄 = 支出
2. 別讓支出超過收入
3. 持續投資複利
4. 風險管理很重要
5. 終身學習

#理財 #有錢人 #投資
""",
    """
🎯 40歲是最重要的理財轉折點

子女教育、父母照顧、退休金
三座大山同時來臨

------------------------------------------
現在不做、以後會後悔：

✅ 檢視保險夠不夠
✅ 計算退休金缺口
✅ 設定每月儲蓄目標

#理財 #中年人 #退休金規劃
""",
    """
📊 為什麼散戶總是赔錢？

因為【人性】

------------------------------------------
貪心 → 高點買進
恐懼 → 低點賣出
從眾 → 跟著大家走

要賺錢，先戰勝自己！

#投資 #股市 #理財
""",
    """
💡 給中年人的理財建議

不要把所有錢都給孩子

------------------------------------------
你的退休金自己要存

✅ 優先照顧好自己
✅ 才有能力照顧家人
✅ 別讓自己成為下一代的負擔

#理財 #退休金 #家庭
"""
]

def download_image():
    """下載隨機免費圖片"""
    url = random.choice(FREE_IMAGE_URLS)
    save_path = "/tmp/twitter_img.jpg"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return save_path
    except Exception as e:
        print(f"下載失敗: {e}")
    return None

def generate_content():
    """生成每日內容"""
    return random.choice(CONTENT_TEMPLATES)

async def post_tweet(text: str, image_path: str = None):
    """發推文"""
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        
        for ctx in browser.contexts:
            for page in ctx.pages:
                if 'x.com' in page.url:
                    # 使用鍵盤 N 新建推文
                    await page.keyboard.press('n')
                    await asyncio.sleep(2)
                    
                    # 如果有圖片，附加
                    if image_path and os.path.exists(image_path):
                        try:
                            # 等待頁面載入
                            await asyncio.sleep(1)
                            
                            # 嘗試直接找 input[type="file"]
                            inputs = await page.query_selector_all('input[type="file"]')
                            if inputs:
                                await inputs[0].set_input_files(image_path)
                                print("✅ 圖片已附加")
                                await asyncio.sleep(2)
                            else:
                                print("⚠️ 找不到圖片輸入框")
                        except Exception as e:
                            print(f"附加圖片失敗: {e}")
                    
                    # 輸入文字
                    await page.keyboard.type(text, delay=15)
                    await asyncio.sleep(0.5)
                    
                    # 發送 (Ctrl+Enter)
                    await page.keyboard.press('Control+Enter')
                    await asyncio.sleep(2)
                    print("✅ 推文已發送!")
                    break
        
        await browser.close()

async def main():
    # 生成內容
    content = generate_content()
    print(f"今日內容：\n{content[:100]}...\n")
    
    # 下載圖片
    img_path = download_image()
    if img_path:
        print(f"✅ 圖片下載成功")
    
    # 發送推文
    await post_tweet(content, img_path)

if __name__ == "__main__":
    asyncio.run(main())
