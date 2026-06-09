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

Agnes AI (by Sapiens AI) provides three distinct models under one API key at `https://apihub.agnes-ai.com/v1`. Each model uses a DIFFERENT endpoint -- they are NOT interchangeable.

### Models at a Glance

| Model | Type | Endpoint | Script |
|-------|------|----------|--------|
| `agnes-2.0-flash` | Text/Chat | `/v1/chat/completions` | Hermes built-in (default model) |
| `agnes-image-2.1-flash` | Image Gen | `/v1/images/generations` | `~/agnes_image_gen.py` |
| `agnes-video-v2.0` | Video Gen | `/v1/videos` (async) | `~/agnes_video_gen.py` |

## CRITICAL PITFALLS

### 1. Never use image/video models as chat models

You CANNOT send `agnes-image-2.1-flash` or `agnes-video-v2.0` to `/v1/chat/completions`. They use entirely different endpoints. Trying to switch the Hermes default model to `agnes-video-v2.0` will produce:

```
HTTP 404: Not Found -- the endpoint does not recognize video model names at /chat/completions
```

**Correct approach:** Use the dedicated script for each model type.

### 2. Video response field is NOT "video_url"

The Agnes Video V2.0 API returns the download URL in the `remixed_from_video_id` field (not `video_url`, `url`, or `video`). Always check in this order:

1. `remixed_from_video_id`
2. `video_url`
3. `url`
4. `video`
5. `output_url`
6. `result_url`
7. `download_url`

### 3. API Key reading pattern -- avoid `***` corruption

The `***` pattern gets corrupted when used inline in Python source code -- the Hermes tool call system replaces the literal API key string at the transmission level, breaking Python syntax.

**ALWAYS** use a `read_key()` function that reads the key from `.env` files at runtime. Never hardcode or inline the key value.

**Correct pattern:**

```python
def read_key():
    k = os.getenv("AGNES_API_KEY", "")
    if k: return k
    for p in [os.path.expanduser("~/.hermes/.env"), os.path.expanduser("~/.env")]:
        if os.path.exists(p):
            for ln in open(p):
                ln = ln.strip()
                if ln.startswith("AGNES_API_KEY="):
                    k = ln[len("AGNES_API_KEY="):].strip().strip('"').strip("'")
                    if k: return k
    return ""

API_KEY = read_key()
```

### 4. Video frame count must follow 8n+1 rule

When setting `num_frames` for video generation, the value must follow `8n+1` (e.g., 121 = 8*15+1). Invalid values will be rejected.

### 5. Quick reference: frame count for duration

| Duration | Frames |
|----------|--------|
| 5s | 121 |
| 10s | 241 |
| 15s | 361 |
| 20s | 481 |

### 6. Image-to-video request timeout -- use 60s+

Text-to-video creates a task in ~1 second. Image-to-video involves server-side image processing and can take 30+ seconds. Use `timeout=60` minimum.

## Image Generation (agnes-image-2.1-flash)

### API

- **Endpoint:** `POST https://apihub.agnes-ai.com/v1/images/generations`
- **Model name:** `agnes-image-2.1-flash`
- **Auth:** `Bearer <API_KEY>`

### Request

```json
{
    "model": "agnes-image-2.1-flash",
    "prompt": "your description",
    "size": "1152x768",
    "extra_body": {"response_format": "url"}
}
```

### Response

```json
{"data": [{"url": "https://...", "b64_json": "..."}]}
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
| `p` / `portrait` | 768x1024 | Vertical |
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

1. **Create task** -- POST to `/v1/videos` -- returns `task_id` and `video_id`
2. **Poll status** -- GET `/agnesapi?video_id=...` -- check `state` field
3. **Download** -- extract URL from `remixed_from_video_id` field

### Request Parameters

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `model` | string | Yes | Must be `agnes-video-v2.0` |
| `prompt` | string | Yes | Text description |
| `image` | string | Optional | Single image URL |
| `extra_body.image` | array | Optional | Multiple images |
| `extra_body.mode` | string | Optional | `"keyframes"` for keyframe mode |
| `width` | int | No | Default: 1152 |
| `height` | int | No | Default: 768 |
| `num_frames` | int | No | Max 441. MUST follow `8n+1` |
| `frame_rate` | number | No | Range: 1-60 |

### Response

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

## Support Files

- `references/astrix-corruption-bug.md` -- Fix for the `***` API key corruption bug
- `scripts/frame_calc.py` -- Frame count calculator (`python frame_calc.py 5 10 15`)

</div>

<!-- ===================== CHINESE SECTION ===================== -->
<div id="zh-content" style="display:none;">

# Agnes AI 多模态模型套件

## 触发条件

当用户想要使用 Agnes AI 模型（文本、图片、视频）来配置或扩展 Agnes AI 集成时使用此技能。

## 概述

Agnes AI（由 Sapiens AI 提供）在 `https://apihub.agnes-ai.com/v1` 下提供三个独立的模型，共用同一个 API Key。每个模型使用**完全不同的 API 端点**，不能混用。

### 模型概览

| 模型 | 类型 | 端点 | 调用方式 |
|------|------|------|---------|
| `agnes-2.0-flash` | 文本对话 | `/v1/chat/completions` | Hermes 内置默认模型 |
| `agnes-image-2.1-flash` | 图片生成 | `/v1/images/generations` | `~/agnes_image_gen.py` |
| `agnes-video-v2.0` | 视频生成 | `/v1/videos` (异步) | `~/agnes_video_gen.py` |

## 关键注意事项

### 1. 切勿将图片/视频模型当作对话模型

**不能**将 `agnes-image-2.1-flash` 或 `agnes-video-v2.0` 发送到 `/v1/chat/completions`。它们使用完全不同的端点。

**错误后果：** `HTTP 404: Not Found`

**正确做法：** 每种模型类型使用专用脚本。

### 2. 视频响应字段名不是 "video_url"

Agnes Video V2.0 API 将下载 URL 放在 **`remixed_from_video_id`** 字段中，而不是 `video_url`、`url` 或 `video`。

检查顺序：
1. `remixed_from_video_id`（优先）
2. `video_url`
3. `url`
4. `video`
5. `output_url`
6. `result_url`
7. `download_url`

### 3. API Key 读取方式 -- 避免 `***` 被截断

Hermes 系统在传输工具调用参数时，会**将 API Key 字符串替换为 `***`**（3 个星号），导致 Python 语法错误。

**正确做法：** 使用 `read_key()` 函数在运行时从 `.env` 文件读取 API Key，永远不要硬编码。

**正确代码示例：**

```python
def read_key():
    k = os.getenv("AGNES_API_KEY", "")
    if k: return k
    for p in [os.path.expanduser("~/.hermes/.env"), os.path.expanduser("~/.env")]:
        if os.path.exists(p):
            for ln in open(p):
                ln = ln.strip()
                if ln.startswith("AGNES_API_KEY="):
                    k = ln[len("AGNES_API_KEY="):].strip().strip('"').strip("'")
                    if k: return k
    return ""

API_KEY = read_key()
```

### 4. 视频帧数必须符合 8n+1 规则

`num_frames` 必须满足 `8n+1`（例如 121 = 8*15+1）。不合法的值会被 API 拒绝。

### 5. 帧数与时长对照表

| 时长 | 帧数 |
|------|------|
| 5 秒 | 121 |
| 10 秒 | 241 |
| 15 秒 | 361 |
| 20 秒 | 481 |

### 6. 图生视频请求超时 -- 至少 60 秒

文生视频约 1 秒返回任务 ID，但**图生视频需要服务器处理图片**，可能 30+ 秒才返回。必须设置 `timeout=60` 以上。

## 图片生成 (agnes-image-2.1-flash)

### API

- **端点：** `POST https://apihub.agnes-ai.com/v1/images/generations`
- **模型名：** `agnes-image-2.1-flash`
- **认证：** `Bearer <API_KEY>`

### 请求示例

```json
{
    "model": "agnes-image-2.1-flash",
    "prompt": "描述内容",
    "size": "1152x768",
    "extra_body": {"response_format": "url"}
}
```

### 响应

```json
{"data": [{"url": "https://...", "b64_json": "..."}]}
```

### 使用方式

```bash
# 文生图
python ~/agnes_image_gen.py text "提示词" [--size WxH]
# 图生图
python ~/agnes_image_gen.py img2img <URL> "提示词" [--size WxH]
# 批量
python ~/agnes_image_gen.py batch "提示词1" "提示词2"
```

### 尺寸预设

| 代码 | 尺寸 | 用途 |
|------|------|------|
| `p` / `portrait` | 768x1024 | 竖屏 |
| `l` / `landscape` | 1024x768 | 横屏（默认） |
| `s` / `square` | 1024x1024 | 正方形 |
| `w` / `widescreen` | 1920x1080 | 宽屏 (16:9) |

## 视频生成 (agnes-video-v2.0)

### API

- **端点：** `POST https://apihub.agnes-ai.com/v1/videos`
- **模型名：** `agnes-video-v2.0`
- **认证：** `Bearer <API_KEY>`
- **查询：** `GET https://apihub.agnes-ai.com/agnesapi?video_id=...&model_name=agnes-video-v2.0`

### 工作流程（异步）

1. **创建任务** -- POST `/v1/videos` -- 返回 `task_id` 和 `video_id`
2. **轮询状态** -- GET `/agnesapi?video_id=...` -- 检查 `state` 字段
3. **下载视频** -- 从 `remixed_from_video_id` 字段提取 URL

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 必须为 `agnes-video-v2.0` |
| `prompt` | string | 是 | 文字描述 |
| `image` | string | 否 | 单张图片 URL |
| `extra_body.image` | array | 否 | 多张图片 |
| `extra_body.mode` | string | 否 | `"keyframes"` 为关键帧模式 |
| `width` | int | 否 | 默认: 1152 |
| `height` | int | 否 | 默认: 768 |
| `num_frames` | int | 否 | 最大 441，必须符合 8n+1 |
| `frame_rate` | number | 否 | 范围: 1-60 |

### 响应示例

```json
{
    "state": "completed",
    "remixed_from_video_id": "https://storage.googleapis.com/.../video.mp4",
    "seconds": "5.0",
    "size": "1152x768"
}
```

### 使用方式

```bash
# 文生视频
python ~/agnes_video_gen.py text "提示词"
# 图生视频
python ~/agnes_video_gen.py image <URL> "提示词"
# 多图生成
python ~/agnes_video_gen.py multi <URL1> <URL2> "提示词"
# 关键帧动画
python ~/agnes_video_gen.py keyframe <URL1> <URL2> "提示词"
# 查询状态
python ~/agnes_video_gen.py status <VIDEO_ID>
```

## 支持文件

- `references/astrix-corruption-bug.md` -- `***` API Key 被截断 bug 的修复方法
- `scripts/frame_calc.py` -- 帧数计算器 (`python frame_calc.py 5 10 15`)

</div>
