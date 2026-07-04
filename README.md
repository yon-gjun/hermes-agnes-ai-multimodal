# hermes-agnes-ai-multimodal

Configure and use Agnes AI multimodal models (text, image, video) via Python scripts.  
通过 Python 脚本配置和使用 Agnes AI 多模态模型（文本、图片、视频）。

---

## Overview / 概述

Agnes AI (by Sapiens AI) provides three distinct models under one API key.  
Agnes AI（由 Sapiens AI 提供）在同一个 API Key 下提供三个独立模型。

| Model / 模型 | Type / 类型 | Endpoint / 端点 | How to Use / 调用方式 |
|---|---|---|---|
| `agnes-2.0-flash` | Text/Chat 文本对话 | `/v1/chat/completions` | Hermes built-in default model |
| `agnes-image-2.1-flash` | Image Gen 图片生成 | `/v1/images/generations` | `~/agnes_image_gen.py` |
| `agnes-video-v2.0` | Video Gen 视频生成 | `/v1/videos` (async) | `~/agnes_video_gen.py` |

**Each model uses a DIFFERENT endpoint — they are NOT interchangeable.**  
**每个模型使用完全不同的 API 端点，不能混用。**

---

## Quick Start / 快速开始

### 1. Set API Key / 配置 API Key

Add to `~/.hermes/.env`:  
在 `~/.hermes/.env` 中添加：

```
AGNES_API_KEY=sk-xxxx
AGNES_VIDEO_API_KEY=sk-xxxx   # same key, separate env var for video script
```

### 2. Install the helper scripts / 安装辅助脚本

```bash
cp agnes_image_gen.py ~/
cp agnes_video_gen.py ~/
```

### 3. Install Skill / 安装技能（Hermes 用户）

```bash
hermes skill install agnes-ai-multimodal
```

### 4. Usage Examples / 使用示例

```bash
# Text to image / 文生图
python ~/agnes_image_gen.py text "一家人在草原上野餐"

# Image to image / 图生图
python ~/agnes_image_gen.py img2img <URL> "风格转换描述"

# Text to video / 文生视频（5s = 121 frames）
python ~/agnes_video_gen.py text "一家人在草原上放风筝" output.mp4 --frames 121

# Image to video / 图生视频
python ~/agnes_video_gen.py image <URL> "提示词" output.mp4

# Query status / 查询视频生成状态
python ~/agnes_video_gen.py status <VIDEO_ID>
```

---

## Full Video Production Pipeline / 完整视频制作管线

The skill supports an end-to-end workflow for multi-scene videos:  
该技能支持完整的多场景视频制作流程：

```
Scene Generation  →  TTS Narration  →  Pad & Concat  →  Audio Mix  →  Subtitles
   场景生成              TTS 配音         补齐/拼接         混音          字幕
```

Key tools used / 关键工具：

| Step | Tool | Description |
|------|------|-------------|
| Scene gen | `agnes_video_gen.py` | ~130s per 5s segment |
| TTS | Hermes `text_to_speech` | OpenAI TTS, each clip ~2-5s |
| Padding | `ffmpeg apad+atrim` | Pad to exactly N seconds |
| Concat | `ffmpeg concat` | Merge all segments |
| Audio mix | `ffmpeg amix` | Narration 0.75 + BGM 0.4 |
| Subtitles | `ffmpeg ass=` | ASS format + Microsoft YaHei |

Use `delegate_task` to generate multiple scenes in parallel (~2-3 min per segment).

---

## CRITICAL PITFALLS / 关键踩坑记录

### 1. Never mix endpoint types / 切勿混用端点
Image/video models CANNOT be sent to `/v1/chat/completions` (HTTP 404).  
图片/视频模型不能发到对话端点。

### 2. Video URL: `remixed_from_video_id` FIRST
API returns download URL in `remixed_from_video_id`, NOT `video_url`. Check order:
1. `remixed_from_video_id` ⬅️ always first
2. `video_url` → `url` → `video` → `output_url` → `result_url` → `download_url`

### 3. API Key: never hardcode / 永远不硬编码 API Key
- **Via `terminal`**: use `read_key()` from `.env` at runtime
- **Via `write_file`**: hex-encode to survive `***` corruption
  ```python
  KEY_HEX = "736b2d..."  # python -c "print(key.encode().hex())"
  API_KEY = bytes.fromhex(KEY_HEX).decode()
  ```

### 4. Frame count: 8n+1 rule / 帧数规则
| Duration / 时长 | Frames / 帧数 | Formula / 公式 |
|---|---|---|
| 5s | 121 | 8×15+1 |
| 10s | 241 | 8×30+1 |
| 15s | 361 | 8×45+1 |
| 20s | 481 | 8×60+1 |
| Max | 441 | 8×55+1 |

### 5. Request timeout: always 120s+
Cloudflare CDN latency can cause 30-40s delays on POST. Use `timeout=120`.

### 6. Image-to-video needs public URLs / 图生视频需要公开 URL
Local paths and base64 data URLs are rejected. Generate an image URL first via text-to-image.

### 7. Windows: use `python`, not `python3`
`python3` symlinks to WindowsApps (MSYS-incompatible). Always use `python`.

### 8. `write_file` fails in mounted directories
The `video_cache` directory rejects `write_file` (mv denied). Use `terminal cat >` instead.

### 9. TTS clips shorter than scene duration
OpenAI TTS clips (2-5s) must be padded to full segment length:
```bash
ffmpeg -i tts_segN.mp3 -af "apad=pad_dur=5,atrim=0:5" -y tts_segN_pad.mp3
```

### 10. Multi-scene visual inconsistency / 多场景视觉不统一
Each text-to-video call generates independently → different lighting/style. Fixes:
- Include shared style descriptors in every prompt
- Be extremely specific about required elements
- Use image-to-video from a shared reference image

### 11. Video API intermittent connectivity
`apihub.agnes-ai.com` may become unreachable (Cloudflare CDN). Wait 2-3 min and retry.

### 12. Chinese text in video prompts does NOT render
Agnes Video cannot render Chinese characters. Generate scenes text-free, add subtitles via FFmpeg ASS.

### 13. OpenAI TTS has no child voices / 无童声音色
All OpenAI voices (`alloy` through `shimmer`) are adult. For child voices:
- **Fish Audio** (free): `101a88bb..` = 稚嫩女童, `1ba245cf..` = 小男孩
- **MiniMax TTS**: `Cute_Spirit`, `Pure-hearted_Boy`

---

## Frame Count Reference / 帧数参考表

| Duration / 时长 | Frames / 帧数 | Format / 公式 |
|---|---|---|
| 1s | 25 | 8×3+1 |
| 2s | 49 | 8×6+1 |
| 3s | 73 | 8×9+1 |
| 5s | 121 | 8×15+1 |
| 10s | 241 | 8×30+1 |
| 15s | 361 | 8×45+1 |
| 20s | 481 | 8×60+1 |

---

## File Structure / 文件结构

```
agnes-ai-multimodal/
├── SKILL.md                          # Main skill document (bilingual)
├── README.md                         # This file
├── README.html                       # HTML formatted README
├── references/
│   ├── astrix-corruption-bug.md      # API Key `***` corruption fix
│   ├── audio-generation-patterns.md  # BGM generation with numpy
│   ├── chinese-text-rendering-limitation.md  # Chinese text in videos
│   ├── download-troubleshooting.md   # Download failure patterns
│   ├── end-to-end-video-pipeline.md  # Full video production workflow
│   ├── fish-audio-child-voice.md     # Fish Audio child TTS voices
│   ├── image-to-video-standalone.md  # Standalone image-to-video script
│   ├── minimax-tts-child-voices.md   # MiniMax child TTS voices
│   ├── openmontage-agnes-workflow.md # Agnes AI + FFmpeg video alternative
│   ├── test-procedure.md             # Full test procedure (4 modes)
│   ├── test-report-june27.md         # Test report (Jun 27, 2026)
│   ├── update-report-2026-06-16.md   # Skill update report (Jun 16)
│   ├── update-report-2026-07-02.md   # Skill update report (Jul 02)
│   └── video-api-connectivity.md     # API connectivity guide
├── scripts/
│   ├── agnes_image_gen.py            # Image generation script
│   ├── agnes_video_gen.py            # Video generation script
│   ├── agnes_watch.py                # Watch/monitor script
│   ├── agnes_watch2.py               # Watch v2
│   ├── agnes_watch3.py               # Watch v3
│   ├── agnes_watch_midautumn.py      # Mid-autumn themed watch
│   └── frame_calc.py                 # Frame count calculator
├── templates/
│   └── agnes_img2img.py              # Image-to-image template (hex-encoded key)
└── assets/
    └── icon.svg                      # Skill icon
```

---

## Verification / 验证

After running a video task, verify the output:

```bash
ffprobe -v quiet -print_format json -show_format final_output.mp4
```
