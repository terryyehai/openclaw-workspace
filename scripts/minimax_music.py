#!/usr/bin/env python3
"""
MiniMax Music Generation API 調用腳本
用法: python minimax_music.py --prompt "流行音樂,快樂,適合派對" [--lyrics "歌詞"] [--instrumental] [--output music.mp3]
"""

import os
import json
import requests
from pathlib import Path


MINIMAX_MUSIC_API = "https://api.minimaxi.com/v1/music_generation"
DEFAULT_MODEL = "music-2.5+"


def generate_music(
    api_key: str,
    prompt: str,
    lyrics: str = None,
    model: str = DEFAULT_MODEL,
    is_instrumental: bool = False,
    output_format: str = "url",
    audio_setting: dict = None,
    output_path: str = "output.mp3"
) -> dict:
    """調用 MiniMax Music API 生成音樂"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "is_instrumental": is_instrumental,
        "output_format": output_format,
    }
    
    if lyrics:
        payload["lyrics"] = lyrics
    
    if audio_setting:
        payload["audio_setting"] = audio_setting
    
    resp = requests.post(MINIMAX_MUSIC_API, headers=headers, json=payload, timeout=120)
    result = resp.json()
    
    if resp.status_code != 200:
        print(f"Error: {result}")
        return result
    
    # 處理 URL 格式
    if output_format == "url" and result.get("data", {}).get("audio_url"):
        audio_url = result["data"]["audio_url"]
        # 下載音頻文件
        audio_resp = requests.get(audio_url)
        with open(output_path, "wb") as f:
            f.write(audio_resp.content)
        print(f"Music saved to: {output_path}")
        return {"status": "success", "file": output_path, "url": audio_url}
    
    # 處理 hex 格式
    elif output_format == "hex" and result.get("data", {}).get("audio"):
        audio_hex = result["data"]["audio"]
        audio_data = bytes.fromhex(audio_hex)
        with open(output_path, "wb") as f:
            f.write(audio_data)
        print(f"Music saved to: {output_path}")
        return {"status": "success", "file": output_path}
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MiniMax Music Generation")
    parser.add_argument("--api-key", "-k", default=os.environ.get("MINIMAX_API_KEY"), 
                        help="MiniMax API Key (或設定 MINIMAX_API_KEY 環境變數)")
    parser.add_argument("--prompt", "-p", required=True, 
                        help="音樂描述：風格、年緒、場景")
    parser.add_argument("--lyrics", "-l", default=None, 
                        help="歌詞 (用 \\n 分隔每行)")
    parser.add_argument("--instrumental", "-i", action="store_true", 
                        help="生成純音樂 (無歌詞)")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, 
                        choices=["music-2.5+", "music-2.5"], 
                        help="使用的模型")
    parser.add_argument("--output", "-o", default="output.mp3", 
                        help="輸出檔案名稱")
    parser.add_argument("--format", default="url", 
                        choices=["url", "hex"], 
                        help="輸出格式")
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("錯誤: 請提供 API Key (--api-key) 或設定 MINIMAX_API_KEY 環境變數")
        exit(1)
    
    audio_setting = {
        "sample_rate": 44100,
        "bitrate": 256000,
        "format": "mp3"
    }
    
    result = generate_music(
        api_key=args.api_key,
        prompt=args.prompt,
        lyrics=args.lyrics,
        model=args.model,
        is_instrumental=args.instrumental,
        output_format=args.format,
        audio_setting=audio_setting,
        output_path=args.output
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
