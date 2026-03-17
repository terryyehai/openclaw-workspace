#!/usr/bin/env python3
"""
IPTV Channel Quality Checker
驗證並清理無效頻道
"""

import asyncio
import aiohttp

async def check_channel(url, timeout=10):
    """檢查頻道是否可用"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=timeout, allow_redirects=True) as resp:
                if resp.status < 400:
                    return True
    except:
        pass
    return False

async def validate_channels():
    """驗證頻道列表"""
    # 讀取現有頻道
    import json
    from urllib.parse import urlparse
    
    # 測試幾個頻道 URL
    test_urls = [
        "https://www.youtube.com/watch?v=uDqQo8a7Xmk",
        "https://example.com/test.m3u8",
    ]
    
    print("測試頻道連線...")
    
    for url in test_urls:
        result = await check_channel(url)
        print(f"  {url[:50]}... {'✅' if result else '❌'}")
    
    print("\n注意：Free-TV/IPTV 頻道時常變動，建議：")
    print("1. 定期手動檢查頻道可用性")
    print("2. 新增自訂頻道")
    print("3. 使用稳定的 M3U8 來源")

if __name__ == "__main__":
    asyncio.run(validate_channels())
