# OpenMontage + Agnes AI 图片生成视频工作流

> **Session:** 2026-06-30  
> **Lesson:** 当网络不稳定无法下载外部视频素材时，使用 Agnes AI 图片生成 + FFmpeg 合成是可靠的替代方案。

## Problem

Pexels 等视频素材网站返回 403 Forbidden（防盗链）。Internet Archive 下载超时。直接 git clone GitHub 也失败（getaddrinfo thread failed）。

## Solution: Agnes AI Images + FFmpeg

### Step 1: 用 Agnes AI 生成场景图片

```python
# 从 skills 目录导入
skills_dir = Path.home() / "AppData" / "Local" / "hermes" / "skills" / "agnes-ai-multimodal" / "scripts"
sys.path.insert(0, str(skills_dir))
from agnes_image_gen import gen_text, save_image

# 生成 1920x1080 图片
result = gen_text("detailed prompt here", "1920x1080")
save_image(result['url'], "output_filename")
```

### Step 2: FFmpeg 合成

```bash
# 预处理每张图片（缩放+调色+淡入淡出）
ffmpeg -loop 1 -i image.png -t 5 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p,eq=brightness=-0.05:contrast=0.9:saturation=0.7,colorbalance=rs=0:gs=0:bs=-0.05,fade=t=in:st=0:d=1.5,fade=t=out:st=3.5:d=1.5" \
  -c:v libx264 -preset medium -crf 22 output.mp4

# 拼接多段
# 1. 创建 concat_list.txt: file 'seg1.mp4' ...
# 2. 拼接
ffmpeg -f concat -safe 0 -i concat_list.txt -c:v libx264 -crf 20 output.mp4

# 3. 添加字幕
ffmpeg -i output.mp4 -vf "drawtext=text='Subtitle':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-text_h-50:fontfile=C:/Windows/Fonts/arial.ttf,format=yuv420p" final.mp4
```

## Pitfalls

- **Pexels 防盗链**: 直接下载 Pexels 视频 URL 返回 403。用 Internet Archive 或 Agnes AI 图片替代。
- **FFmpeg 滤镜过长**: 复杂滤镜链会导致 `No such filter` 错误。分段处理（每段单独滤镜）+ concat 拼接更可靠。
- **Windows 字体路径**: `drawtext` 的 fontfile 必须用 Windows 原生路径 `C:/Windows/Fonts/arial.ttf`，不能用系统路径。
- **Agnes AI 模块导入**: `agnes_image_gen.py` 在 skills 目录下，不在项目根目录。需要动态添加到 sys.path。
- **Agnes AI 500 错误**: 偶尔返回 `upstream error: do request failed`。重试即可。
