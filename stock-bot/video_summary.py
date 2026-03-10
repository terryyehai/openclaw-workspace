#!/usr/bin/env python3
"""
YouTube 影片字幕摘要
"""

import sys, urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi
import requests

BOT_TOKEN = "8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID = "6490946430"

def extract_video_id(url_or_id):
    if len(url_or_id) == 11:
        return url_or_id
    parsed = urllib.parse.urlparse(url_or_id)
    if parsed.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
        if parsed.path == '/watch':
            qs = urllib.parse.parse_qs(parsed.query)
            return qs.get('v', [None])[0]
    elif parsed.hostname in ['youtu.be']:
        return parsed.path[1:]
    return url_or_id

def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        result = api.fetch(video_id)
        
        # 提取文字
        texts = []
        for snippet in result.snippets:
            if snippet.text:
                texts.append(snippet.text)
        
        return texts
    except Exception as e:
        print(f"錯誤: {e}")
        return None

def generate_summary(transcript, max_length=800):
    full_text = " ".join(transcript)
    if len(full_text) > max_length:
        return full_text[:max_length] + "..."
    return full_text

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def main():
    if len(sys.argv) < 2:
        video_id = "dQw4w9WgXcQ"  # 測試
    else:
        video_id = extract_video_id(sys.argv[1])
    
    print(f"處理影片: {video_id}")
    
    transcript = get_transcript(video_id)
    
    if transcript:
        print(f"字幕獲取成功！共 {len(transcript)} 句")
        summary = generate_summary(transcript)
        
        message = f"📹 *YouTube 影片字幕*\n\n影片: https://youtu.be/{video_id}\n\n"
        message += f"字幕摘要:\n{summary}\n\n"
        message += f"--- 共 {len(transcript)} 句"
        
        send_to_telegram(message)
        print("已發送到 Telegram！")
    else:
        print("無法獲取字幕")

if __name__ == "__main__":
    main()
