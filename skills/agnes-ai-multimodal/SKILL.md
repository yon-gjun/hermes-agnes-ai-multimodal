---
name: agnes-ai-multimodal
description: "Configure and use Agnes AI multimodal models (text, image, video) via Python scripts. 通过 Python 脚本配置和使用 Agnes AI 多模态模型（文本、图片、视频）."
tags: [agnes, multimodal, text-to-image, text-to-video, image-to-video, api, hermes]
---

<!-- Language Switch: 使用 #lang-switch 进行中文/英文切换 -->

<div id="lang-switch" style="display:flex; gap:10px; margin:10px 0; padding:8px; background:#f5f5f5; border-radius:8px;">
  <button onclick="document.getElementById('zh-content').style.display='none';document.getElementById('en-content').style.display='block';this.style.background='#2196F3';this.style.color='white';document.querySelectorAll('#lang-switch button')[1].style.background='transparent';document.querySelectorAll('#lang-switch button')[1].style.color='black';" style="padding:8px 16px; border:1px solid #ccc; border-radius:4px; cursor:pointer; background:#2196F3; color:white; font-weight:bold;">中文</button>
  <button onclick="document.getElementById('en-content').style.display='none';document.getElementById('zh-content').style.display='block';this.style.background='#2196F3';this.style.color='white';document.querySelectorAll('#lang-switch button')[0].style.background='transparent';document.querySelectorAll('#lang-switch button')[0].style.color='black';" style="padding:8px 16px; border:1px solid #ccc; border-radius:4px; cursor:pointer; background:transparent; color:black;">English</button>
</div>

<!-- ===================== ENGLISH SECTION ===================== -->
<div id="en-content">

# Agnes AI Multimodal Suite

## Trigger
When the user wants to use any Agnes AI model (text, image, or video) beyond the default text model, or when configuring/extending Agnes AI integrations.

## Overview
Agnes AI (by Sapiens AI) provides three distinct models under one API key at `https://apihub.agnes-ai.com/v1`. Each model uses a DIFFERENT endpoint — they are NOT interchangeable.

### Models at a Glance

| Model | Type | Endpoint | Script |
|-------|------|----------|--------|
| `agnes-2.0-flash` | Text/Chat | `/v1/chat/completions` | Hermes built-in (default model) |
| `agnes-image-2.1-flash` | Image Gen | `/v1/images/generations` | `~/.hermes/skills/devops/agnes-ai-multimodal/scripts/agnes_image_gen.py` |
| `agnes-video-v2.0` | Video Gen | `/v1/videos` (async) | `~/.hermes/skills/devops/agnes-ai-multimodal/scripts/agnes_video_gen.py` |

## CRITICAL PITFALLS

### 1. Never use image/video models as chat models
You CANNOT send `agnes-image-2.1-flash` or `agnes-video-v2.0` to `/v1/chat/completions`. They use entirely different endpoints. Trying to switch the Hermes default model to `agnes-video-v2.0` will produce:
```
HTTP 404: Not Found — the endpoint doesn't recognize video model names at /chat/completions
```
**Correct approach:** Use the dedicated script for each model type.

### 2. Video response field is NOT "video_url"
The Agnes Video V2.0 API returns the download URL in the `remixed_from_video_id` field (not `video_url`, `url`, or `video`). Always check `remixed_from_video_id` first in the URL extraction fallback list, in this order:
1. `remixed_from_video_id`
2. `video_url`
3. `url`
4. `video`
5. `output_url`
6. `result_url`
7. `download_url`

### 3. Video frame count must follow 8n+1 rule
When setting `num_frames` for video generation, the value must follow `8n+1` (e.g., 121 = 8×15+1). Invalid values will be rejected.

### 4. Quick reference: frame count for duration
```python
# Round to 8n+1:
frames = int(round(duration * 24))
frames = frames + (1 - frames % 8) if frames % 8 != 1 else frames
```
Common durations at 24fps: 5s→121, 10s→241, 15s→361, 20s→481.

### 5. Image-to-video request timeout — use 60s+
Text-to-video creates a task in ~1 second. Image-to-video involves server-side image processing and can take 30+ seconds to return the task creation response. Use `timeout=60` minimum on `requests.post()`.


## Image Generation (agnes-image-2.1-flash)

### API
- **Endpoint:** `POST https://apihub.agnes-ai.com/v1/images/generations`
- **Model name:** `agnes-image-2.1-flash`
- **Auth:** `Bearer <API_KEY>`

### Request
```json
{
    "model": "agnes-image-2.1-flash",
    "prompt": "A detailed description of the image to generate",
    "size": "1024x768",
    "extra_body": {"response_format": "url"}
}
```

### Response
```json
{
    "data": [{"url": "https://...", "b64_json": "..."}]
}
```

### Usage
```bash
# Text to image
python ~/agnes_image_gen.py text "prompt" [--size WxH]
# Image to image
python ~/agnes_image_gen.py img2img <URL> "prompt" [--size WxH]
# Batch
python ~/agnes_image_gen.py batch "prompt1" "prompt2"
```

### Size presets
| Code | Dimension | Use |
|------|-----------|-----|
| `p` / `portrait` | 768x1024 | Vertical/portrait |
| `l` / `landscape` | 1024x768 | Horizontal (default) |
| `s` / `square` | 1024x1024 | Square |
| `w` / `widescreen` | 1920x1080 | Wide (16:9) |

## Video Generation (agnes-video-v2.0)

### API
- **Endpoint:** `POST https://apihub.agnes-ai.com/v1/videos`
- **Model name:** `agnes-video-v2.0`
- **Auth:** `Bearer <API_KEY>`
- **Retrieve:** `GET https://apihub.agnes-ai.com/agnesapi?video_id=...&model_name=agnes-video-v2.0`

### Workflow (Async)
1. **Create task** → POST to `/v1/videos` → returns `task_id` and `video_id`
2. **Poll status** → GET `/agnesapi?video_id=...` → check `state` field
3. **Download** → extract URL from `remixed_from_video_id` field

### Request Parameters
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `model` | string | Yes | Must be `agnes-video-v2.0` |
| `prompt` | string | Yes | Text description |
| `image` | string | Optional | Single image URL for img2vid |
| `extra_body.image` | array | Optional | Multiple images |
| `extra_body.mode` | string | Optional | `"keyframes"` for keyframe mode |
| `width` | int | No | Default: 1152 |
| `height` | int | No | Default: 768 |
| `num_frames` | int | No | Max 441. MUST follow `8n+1` rule |
| `frame_rate` | number | No | Range: 1-60 |

### Response (Retrieve)
```json
{
    "state": "completed",
    "remixed_from_video_id": "https://storage.googleapis.com/.../video.mp4",
    "seconds": "5.0",
    "size": "1152x768"
}
```

### Usage
```bash
# Text to video
python ~/agnes_video_gen.py text "prompt"
# Image to video
python ~/agnes_video_gen.py image <URL> "prompt"
# Multi-image
python ~/agnes_video_gen.py multi <URL1> <URL2> "prompt"
# Keyframe animation
python ~/agnes_video_gen.py keyframe <URL1> <URL2> "prompt"
# Query status
python ~/agnes_video_gen.py status <VIDEO_ID>
```