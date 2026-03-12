#!/usr/bin/env python3
"""
YouTube 字幕擷取工具
用法: python3 youtube_transcript.py <YouTube_URL 或 Video_ID>
"""
import sys
import requests
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url):
    """從 URL 提取影片 ID"""
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return url

def fetch_transcript(video_id):
    """擷取影片字幕"""
    ytt_api = YouTubeTranscriptApi()
    
    # 嘗試不同語言
    languages = ['zh-TW', 'zh', 'en', 'ja']
    
    for lang in languages:
        try:
            transcript = ytt_api.fetch(video_id, languages=[lang])
            transcript_data = list(transcript)
            return transcript_data, lang
        except Exception as e:
            continue
    
    raise Exception(f'無法取得影片 {video_id} 的字幕')

def format_transcript(transcript):
    """格式化字幕為文字"""
    lines = []
    current_time = None
    
    for item in transcript:
        start = item.start
        text = item.text
        
        # 每 5 秒換行
        if current_time is None or start - current_time > 5:
            lines.append(f'\n[{int(start)//60}:{int(start)%60:02d}] ')
            current_time = start
        else:
            lines.append(' ')
        
        lines.append(text)
    
    return ''.join(lines)

def main():
    if len(sys.argv) < 2:
        print('用法: python3 youtube_transcript.py <YouTube_URL 或 Video_ID>')
        sys.exit(1)
    
    video_id = get_video_id(sys.argv[1])
    print(f'正在擷取影片 {video_id} 的字幕...')
    
    transcript, lang = fetch_transcript(video_id)
    print(f'成功擷取 {len(transcript)} 條字幕 (語言: {lang})')
    
    # 輸出格式化字幕
    formatted = format_transcript(transcript)
    
    # 保存到檔案
    output_file = f'youtube_transcript_{video_id}.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted)
    
    print(f'字幕已保存到: {output_file}')
    
    # 輸出前 50 條
    print('\n=== 字幕預覽（前50條）===')
    for item in transcript[:50]:
        print(f"[{int(item.start)//60}:{int(item.start)%60:02d}] {item.text}")

if __name__ == '__main__':
    main()
