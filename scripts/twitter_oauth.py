#!/usr/bin/env python3
"""
Twitter OAuth Setup - 產生 OAuth Access Token
使用 OAuth 1.0a + PIN (oob)
"""

import tweepy
import os
import json

# Twitter API Keys
API_KEY = "mkv9ZEkxw5LJ2WOvWGuLChPGc"
API_SECRET = "YM3HvylGPZ6ZJUfNtGeP92O9ra8cpaF2m9so5DFlpz2LL2hDuP"

def main():
    print("=" * 50)
    print("Twitter OAuth 1.0a 授權 (OOB)")
    print("=" * 50)
    
    # 建立 OAuth1 handler with OOB callback
    auth = tweepy.OAuth1UserHandler(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        callback="oob"  # Out-of-band for CLI
    )
    
    # 取得授權 URL
    try:
        authorization_url = auth.get_authorization_url()
        print(f"\n請訪問以下網址進行授權：\n")
        print(authorization_url)
        print(f"\n" + "=" * 50)
        
        # 讓用戶輸入 PIN 碼
        verifier = input("請輸入顯示的 7 位數 PIN 碼： ").strip()
        
        if not verifier:
            print("❌ 沒有輸入 PIN 碼")
            return
        
        print("\n正在交換 access token...")
        
        # 取得 access token
        auth.get_access_token(verifier)
        
        print("\n" + "=" * 50)
        print("✅ OAuth 授權成功！")
        print("=" * 50)
        print(f"\nAccess Token: {auth.access_token}")
        print(f"Access Token Secret: {auth.access_token_secret}")
        
        # 儲存
        os.makedirs("/home/terry/.openclaw/twitter", exist_ok=True)
        tokens = {
            "access_token": auth.access_token,
            "access_token_secret": auth.access_token_secret,
            "consumer_key": API_KEY,
            "consumer_secret": API_SECRET
        }
        with open("/home/terry/.openclaw/twitter/tokens.json", "w") as f:
            json.dump(tokens, f, indent=2)
        os.chmod("/home/terry/.openclaw/twitter/tokens.json", 0o600)
        
        print("\nTokens 已儲存到 ~/.openclaw/twitter/tokens.json")
        
        # 測試發推
        print("\n正在測試發推...")
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=auth.access_token,
            access_token_secret=auth.access_token_secret
        )
        response = client.create_tweet(text="🤖 Test tweet from OpenClaw Twitter Bot!")
        print(f"✅ 測試推文成功！ Tweet ID: {response.data['id']}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
