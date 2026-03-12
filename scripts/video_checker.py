#!/usr/bin/env python3
"""
YouTube 影片預覽與品質檢查機制
使用 moviepy + PIL 進行檢查
"""

import os
import sys
from pathlib import Path
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np

# 顏色輸出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_video_exists(video_path):
    """檢查影片是否存在"""
    print(f"\n{BLUE}📁 檢查影片檔案...{RESET}")
    if not os.path.exists(video_path):
        print(f"{RED}❌ 影片檔案不存在: {video_path}{RESET}")
        return False
    
    size = os.path.getsize(video_path)
    size_mb = size / (1024 * 1024)
    print(f"{GREEN}✅ 影片存在: {video_path}{RESET}")
    print(f"   大小: {size_mb:.2f} MB")
    return True

def get_video_info(video_path):
    """取得影片資訊"""
    print(f"\n{BLUE}🎬 取得影片資訊...{RESET}")
    
    try:
        clip = VideoFileClip(video_path)
        info = {
            'width': clip.w,
            'height': clip.h,
            'duration': clip.duration,
            'fps': clip.fps,
            'has_audio': clip.audio is not None if hasattr(clip, 'audio') else False,
        }
        
        if clip.audio:
            info['audio_codec'] = 'aac'
            info['audio_fps'] = clip.audio.fps
        
        clip.close()
        return info
    except Exception as e:
        print(f"{RED}❌ 讀取影片失敗: {e}{RESET}")
        return None

def check_video_quality(info, video_path):
    """檢查影片品質"""
    print(f"\n{BLUE}🔍 品質檢查...{RESET}")
    
    issues = []
    warnings = []
    
    # 1. 解析度檢查
    width = info.get('width', 0)
    height = info.get('height', 0)
    if height < 720:
        issues.append(f"解析度過低: {width}x{height} (建議至少 720p)")
    elif height >= 1080:
        print(f"{GREEN}✅ 解析度: {width}x{height} (1080p+){RESET}")
    else:
        warnings.append(f"解析度: {width}x{height} (720p)")
        print(f"{YELLOW}⚠️ 解析度: {width}x{height}{RESET}")
    
    # 2. 時長檢查
    duration = info.get('duration', 0)
    if duration < 5:
        issues.append(f"影片過短: {duration:.1f}秒 (建議至少 10 秒)")
    elif duration > 60:
        warnings.append(f"影片過長: {duration:.1f}秒 (Shorts 建議 60 秒內)")
        print(f"{YELLOW}⚠️ 時長: {duration:.1f}秒 (可能太長){RESET}")
    else:
        print(f"{GREEN}✅ 時長: {duration:.1f}秒{RESET}")
    
    # 3. 影格率檢查
    fps = info.get('fps', 0)
    if fps < 24:
        warnings.append(f"影格率過低: {fps}")
        print(f"{YELLOW}⚠️ 影格率: {fps} fps{RESET}")
    else:
        print(f"{GREEN}✅ 影格率: {fps} fps{RESET}")
    
    # 4. 音頻檢查
    has_audio = info.get('has_audio', False)
    if not has_audio:
        issues.append("沒有音頻軌道")
        print(f"{RED}❌ 沒有音頻{RESET}")
    else:
        print(f"{GREEN}✅ 有音頻軌道{RESET}")
    
    # 5. 檔案大小檢查
    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    if size_mb < 0.5:
        warnings.append(f"檔案過小: {size_mb:.2f}MB (可能內容不足)")
        print(f"{YELLOW}⚠️ 檔案大小: {size_mb:.2f} MB{RESET}")
    else:
        print(f"{GREEN}✅ 檔案大小: {size_mb:.2f} MB{RESET}")
    
    # 6. 影片內容變化檢查
    print(f"\n{BLUE}🎥 檢測影片內容變化（靜態 vs 動態）...{RESET}")
    is_static, frame_count = check_if_static(video_path, info.get('duration', 10))
    if is_static:
        issues.append("影片可能是靜態的（無明顯內容變化）")
        print(f"{RED}❌ 警告: 影片只是靜態圖片輪播！{RESET}")
    else:
        print(f"{GREEN}✅ 影片有內容變化 (檢測 {frame_count} 幀){RESET}")
    
    return issues, warnings

def check_if_static(video_path, duration, sample_count=8):
    """檢測影片是否為靜態（只是圖片輪播）"""
    try:
        clip = VideoFileClip(video_path)
        
        # 採樣多個時間點
        timestamps = np.linspace(0.05, duration * 0.95, min(sample_count, 8))
        
        frames = []
        for ts in timestamps:
            frame = clip.get_frame(ts)
            frames.append(frame)
        
        clip.close()
        
        if len(frames) < 2:
            return True, 0
        
        # 計算幀之間的差異
        total_diff = 0
        diff_count = 0
        
        for i in range(1, len(frames)):
            # 轉為灰階比對
            f1 = np.mean(frames[i-1], axis=2)
            f2 = np.mean(frames[i], axis=2)
            
            # 計算差異
            diff = np.abs(f1.astype(float) - f2.astype(float)).mean()
            total_diff += diff
            diff_count += 1
        
        avg_diff = total_diff / diff_count if diff_count > 0 else 0
        
        # 如果平均差異小於 5，認為是靜態
        is_static = avg_diff < 5
        
        return is_static, len(frames)
        
    except Exception as e:
        print(f"{YELLOW}⚠️ 內容變化檢測失敗: {e}{RESET}")
        return False, 0

def generate_preview(video_path, output_dir):
    """生成預覽截圖"""
    print(f"\n{BLUE}🖼️ 生成預覽截圖...{RESET}")
    
    preview_dir = Path(output_dir) / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        
        # 擷取 4 個時間點
        timestamps = [0.1, duration * 0.33, duration * 0.66, duration * 0.9]
        
        for i, ts in enumerate(timestamps):
            frame = clip.get_frame(ts)
            
            # 轉為 PIL Image
            if frame.dtype != np.uint8:
                frame = (frame * 255).astype(np.uint8)
            
            img = Image.fromarray(frame)
            output = preview_dir / f"preview_{i+1}.jpg"
            img.save(output, quality=90)
            print(f"   ✅ {ts:.1f}s → {output.name}")
        
        clip.close()
        print(f"\n{GREEN}📂 預覽截圖已存至: {preview_dir}{RESET}")
        
    except Exception as e:
        print(f"{RED}❌ 生成預覽失敗: {e}{RESET}")

def print_summary(issues, warnings):
    """印出檢查結果摘要"""
    print(f"\n{'='*50}")
    print(f"{BLUE}📋 檢查結果摘要{RESET}")
    print('='*50)
    
    if not issues and not warnings:
        print(f"{GREEN}✅ 影片通過所有檢查！{RESET}")
        return True
    
    if issues:
        print(f"\n{RED}❌ 問題 ({len(issues)}):{RESET}")
        for issue in issues:
            print(f"   • {issue}")
    
    if warnings:
        print(f"\n{YELLOW}⚠️ 警告 ({len(warnings)}):{RESET}")
        for warn in warnings:
            print(f"   • {warn}")
    
    return len(issues) == 0

def main():
    if len(sys.argv) < 2:
        print("用法: python video_checker.py <影片路徑> [--skip-preview]")
        print("範例: python video_checker.py ./youtube/final_video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    skip_preview = '--skip-preview' in sys.argv
    
    print(f"{BLUE}{'='*50}")
    print(f"🎬 YouTube 影片品質檢查")
    print(f"{'='*50}{RESET}")
    
    # 1. 檢查檔案
    if not check_video_exists(video_path):
        sys.exit(1)
    
    # 2. 取得資訊
    info = get_video_info(video_path)
    if not info:
        sys.exit(1)
    
    # 3. 品質檢查
    issues, warnings = check_video_quality(info, video_path)
    
    # 4. 生成預覽
    if not skip_preview:
        preview_dir = os.path.dirname(video_path) or '.'
        generate_preview(video_path, preview_dir)
    
    # 5. 摘要
    passed = print_summary(issues, warnings)
    
    print(f"\n{'='*50}")
    if passed:
        print(f"{GREEN}🎉 影片準備好可以上傳！{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}❌ 請修正上述問題後再上傳{RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()
