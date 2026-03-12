#!/usr/bin/env python3
"""
影片生成器 - 完整版
包含：圖片 + 語音 + BGM + 轉場效果
"""
import os
import asyncio
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip, ColorClip,
    CompositeVideoClip, CompositeAudioClip, concatenate_videoclips
)
from moviepy.video.fx import fadein, fadeout
from PIL import Image, ImageDraw, ImageFont
import requests
from pathlib import Path
import json

class VideoGenerator:
    def __init__(
        self,
        output_dir=".",
        image_duration=3,      # 每張圖片顯示秒數
        transition_duration=0.5,  # 轉場時長
        bgm_volume=0.3,       # BGM 音量
        voice_volume=1.0,      # 語音音量
        fps=24
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.image_duration = image_duration
        self.transition_duration = transition_duration
        self.bgm_volume = bgm_volume
        self.voice_volume = voice_volume
        self.fps = fps
        
        # 免費 BGM URL（可直接使用）
        self.bgm_sources = {
            "epic": "https://cdn.pixabay.com/audio/2022/10/25/audio_946e9730e6.mp3",
            "ambient": "https://cdn.pixabay.com/audio/2022/03/15/audio_51dcb3f8d2.mp3",
            "upbeat": "https://cdn.pixabay.com/audio/2022/01/18/audio_d0a13f69d2.mp3",
            "peaceful": "https://cdn.pixabay.com/audio/2022/06/07/audio_638d02d7c3.mp3"
        }
    
    def download_bgm(self, url, output_path):
        """下載 BGM"""
        try:
            response = requests.get(url, timeout=30)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ BGM 下載成功: {output_path}")
            return True
        except Exception as e:
            print(f"❌ BGM 下載失敗: {e}")
            return False
    
    def create_text_overlay(self, text, size=(1920, 1080), duration=3):
        """建立文字疊加層"""
        # 創建透明圖層
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 載入字體（嘗試系統字體）
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 48)
        except:
            font = ImageFont.load_default()
        
        # 繪製文字
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 計算置中位置
        x = (size[0] - text_width) // 2
        y = size[1] - text_height - 100
        
        # 繪製文字陰影（增加可讀性）
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        # 轉換為 moviepy clip
        img.save("/tmp/text_overlay.png")
        clip = ImageClip("/tmp/text_overlay.png").set_duration(duration)
        
        return clip
    
    def add_text_subtitle(self, video_clip, subtitles):
        """
        添加字幕
        subtitles: [{"text": "文字", "start": 0, "end": 3}, ...]
        """
        text_clips = []
        
        for sub in subtitles:
            txt_clip = TextClip(
                sub["text"],
                fontsize=36,
                color='white',
                font='NotoSansCJK',
                size=(video_clip.w - 100, None),
                method='caption'
            )
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(
                sub["end"] - sub["start"]
            ).set_start(sub["start"])
            
            # 添加陰影效果
            txt_clip = txt_clip.add_mask()
            
            text_clips.append(txt_clip)
        
        if text_clips:
            return CompositeVideoClip([video_clip] + text_clips)
        return video_clip
    
    async def generate_video(
        self,
        voice_file,
        images_dir=None,
        bgm_style="epic",
        output_name="output.mp4",
        title=None,
        subtitles=None
    ):
        """生成完整影片"""
        
        output_path = self.output_dir / output_name
        
        print(f"=== 開始生成影片 ===")
        print(f"輸出: {output_path}")
        
        # 1. 準備圖片
        if images_dir:
            images = sorted(Path(images_dir).glob("*.jpg")) + \
                    sorted(Path(images_dir).glob("*.png"))
            
            if not images:
                print("⚠️ 無圖片，使用黑色背景")
                # 建立黑色背景
                img = Image.new('RGB', (1920, 1080), (0, 0, 0))
                img.save("/tmp/black_bg.jpg")
                images = [Path("/tmp/black_bg.jpg")]
        else:
            # 預設黑色背景
            img = Image.new('RGB', (1920, 1080), (0, 0, 0))
            img.save("/tmp/black_bg.jpg")
            images = [Path("/tmp/black_bg.jpg")]
        
        print(f"📷 使用 {len(images)} 張圖片")
        
        # 2. 建立影片片段
        clips = []
        
        # 計算每張圖片應該顯示多久
        voice_duration = AudioFileClip(str(voice_file)).duration
        per_image_duration = voice_duration / len(images)
        
        for i, img_path in enumerate(images):
            # 載入圖片
            clip = ImageClip(str(img_path)).set_duration(per_image_duration)
            
            # 設定大小（確保 1920x1080）
            clip = clip.resize(height=1080)
            
            # 添加淡入淡出效果
            if self.transition_duration > 0:
                clip = clip.fadein(self.transition_duration)
                clip = clip.fadeout(self.transition_duration)
            
            clips.append(clip)
        
        print(f"✂️ 建立 {len(clips)} 個片段")
        
        # 3. 合併影片
        if len(clips) > 1:
            video = concatenate_videoclips(clips, method="compose")
        else:
            video = clips[0]
        
        print(f"🎬 影片時長: {video.duration:.1f}秒")
        
        # 4. 添加片頭標題（跳過，需要 ImageMagick）
        # if title:
        #     print(f"📝 添加片頭: {title}")
                title,
                fontsize=72,
                color='white',
                font='NotoSansCJK',
                size=(1920, None),
                method='caption'
            )
            title_clip = title_clip.set_position('center').set_duration(3)
            title_clip = title_clip.fadein(1).fadeout(1)
            
            # 添加黑色背景
            bg = ColorClip(size=(1920, 1080), color=(0, 0, 0)).set_duration(3)
            
            video = concatenate_videoclips([bg, title_clip, video])
        
        # 5. 添加字幕（跳過，需要 ImageMagick）
        # if subtitles:
        #     print(f"📝 添加字幕: {len(subtitles)} 條")
        
        # 6. 添加語音
        if voice_file and os.path.exists(voice_file):
            print(f"🔊 添加語音: {voice_file}")
            voice = AudioFileClip(str(voice_file))
            voice = voice.volumex(self.voice_volume)
            video = video.set_audio(voice)
        
        # 7. 添加 BGM
        bgm_url = self.bgm_sources.get(bgm_style, self.bgm_sources["epic"])
        bgm_path = self.output_dir / "temp_bgm.mp3"
        
        if self.download_bgm(bgm_url, bgm_path):
            print(f"🎵 添加 BGM: {bgm_style}")
            bgm = AudioFileClip(str(bgm_path))
            
            # 裁剪 BGM 長度
            if bgm.duration > video.duration:
                bgm = bgm.subclip(0, video.duration)
            else:
                # 循環 BGM
                loops = int(video.duration / bgm.duration) + 1
                bgm = mp.audio.loop(bgm, loops=loops).subclip(0, video.duration)
            
            bgm = bgm.volumex(self.bgm_volume)
            
            # 混合語音和 BGM
            if video.audio:
                final_audio = CompositeAudioClip([video.audio, bgm])
            else:
                final_audio = bgm
            
            video = video.set_audio(final_audio)
        
        # 8. 輸出影片
        print(f"💾 輸出影片中...")
        video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile="/tmp/temp_audio.aac",
            remove_temp=True
        )
        
        # 9. 清理臨時檔案
        if bgm_path.exists():
            bgm_path.unlink()
        
        print(f"✅ 影片生成完成: {output_path}")
        
        # 回傳資訊
        return {
            "output_path": str(output_path),
            "duration": video.duration,
            "resolution": f"{video.w}x{video.h}",
            "has_audio": video.audio is not None,
            "bgm_style": bgm_style
        }


# 測試
async def main():
    generator = VideoGenerator(
        output_dir=".",
        image_duration=3,
        bgm_volume=0.3,
        voice_volume=1.0
    )
    
    # 測試生成（如果有語音檔案）
    voice_file = "voice_002.mp3"
    images_dir = "images"
    
    if os.path.exists(voice_file):
        result = await generator.generate_video(
            voice_file=voice_file,
            images_dir=images_dir if os.path.exists(images_dir) else None,
            bgm_style="epic",
            output_name="final_video_002.mp4",
            title="兵馬俑的秘密"
        )
        print(f"\n生成結果: {json.dumps(result, indent=2)}")
    else:
        print(f"找不到語音檔案: {voice_file}")


if __name__ == "__main__":
    asyncio.run(main())
