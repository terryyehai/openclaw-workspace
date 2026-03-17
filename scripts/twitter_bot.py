#!/usr/bin/env python3
"""
Twitter Bot - 讀寫分離
讀取：使用 Bearer Token (需要 credits)
發推：使用 OAuth (需要 Write 權限)
"""

import tweepy
import os
import json

# API Keys
API_KEY = "mkv9ZEkxw5LJ2WOvWGuLChPGc"
API_SECRET = "YM3HvylGPZ6ZJUfNtGeP92O9ra8cpaF2m9so5DFlpz2LL2hDuP"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAORP8QEAAAAA25iTzuLMcmy8fo1cSbYP1%2BYFHPA%3D4BS5AtYwKZPG6TXghFzMmKcW7LdJ0ZAlbFJQNLlLlLav0QW5p1"

# Load OAuth tokens
def load_tokens():
    try:
        with open("/home/terry/.openclaw/twitter/tokens.json") as f:
            return json.load(f)
    except:
        return None

class TwitterBot:
    def __init__(self):
        self.tokens = load_tokens()
        self.read_client = None
        self.write_client = None
        
        # 初始化讀取客戶端 (Bearer Token)
        try:
            self.read_client = tweepy.Client(bearer_token=BEARER_TOKEN)
        except:
            pass
        
        # 初始化寫入客戶端 (OAuth 1.0a)
        if self.tokens:
            try:
                self.write_client = tweepy.Client(
                    consumer_key=API_KEY,
                    consumer_secret=API_SECRET,
                    access_token=self.tokens.get("access_token"),
                    access_token_secret=self.tokens.get("access_token_secret")
                )
            except:
                pass
    
    def post_tweet(self, text):
        """發推文"""
        if not self.write_client:
            return {"error": "OAuth 客戶端未初始化"}
        
        try:
            response = self.write_client.create_tweet(text=text)
            return {"success": True, "id": response.data['id']}
        except tweepy.Forbidden as e:
            return {"error": "權限不足", "message": str(e)}
        except Exception as e:
            return {"error": str(e)}
    
    def get_timeline(self, max_results=10):
        """取得時間線"""
        if not self.read_client:
            return [{"error": "Bearer Token 無法使用（可能需要 credits）"}]
        
        try:
            tweets = self.read_client.get_home_timeline(max_results=max_results)
            return [{"id": t.id, "text": t.text} for t in tweets.data] if tweets.data else []
        except Exception as e:
            return [{"error": str(e)}]
    
    def search(self, query, max_results=10):
        """搜尋推文"""
        if not self.read_client:
            return [{"error": "Bearer Token 無法使用"}]
        
        try:
            tweets = self.search_recent_tweets(query=query, max_results=max_results)
            return [{"id": t.id, "text": t.text} for t in tweets.data] if tweets.data else []
        except Exception as e:
            return [{"error": str(e)}]

def main():
    bot = TwitterBot()
    
    print("=" * 50)
    print("Twitter Bot 測試")
    print("=" * 50)
    
    # 測試發推
    print("\n[1] 測試發推...")
    result = bot.post_tweet("🤖 Test from OpenClaw Bot")
    print(f"結果: {result}")
    
    # 測試讀取
    print("\n[2] 測試讀取時間線...")
    timeline = bot.get_timeline(3)
    print(f"結果: {timeline[:2] if len(timeline) > 2 else timeline}")

if __name__ == "__main__":
    main()
