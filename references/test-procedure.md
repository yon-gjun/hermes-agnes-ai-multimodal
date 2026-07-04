# Agnes AI Multimodal Test Procedure

## Test Cases (June 27, 2026)

### 1. Text-to-Image ✅
```bash
python3 'C:\Users\yon-g\AppData\Local\hermes\skills\agnes-ai-multimodal\scripts\agnes_image_gen.py' text "prompt" --size widescreen
```
- Output: `gen.png` (1536 KB)
- Size presets: `p/portrait`=768x1024, `l/landscape`=1024x768, `s/square`=1024x1024, `w/widescreen`=1920x1080

### 2. Image-to-Image ✅
```bash
python3 'C:\Users\yon-g\AppData\Local\hermes\skills\agnes-ai-multimodal\scripts\agnes_image_gen.py' img2img "<URL>" "prompt" --size widescreen
```
- Output: `img2img.png` (1288 KB)
- Input image URL must be accessible (remote URL, not local path)

### 3. Text-to-Video ✅
- Initial POST to `/v1/videos` can take 30-40s (network latency)
- Returns `task_id` and `video_id`
- Poll `/agnesapi?video_id=...&model_name=agnes-video-v2.0` every 10s
- Check `state` field: `queued` → `processing` → `completed`
- Download URL is in `remixed_from_video_id` field (NOT `video_url`)
- Default frames: 121 (5 seconds), must follow 8n+1 rule

### 4. Image-to-Video ⚠️ (partial)
- Requires image URL (not local path)
- Base64 data URLs are too large for practical use
- Workaround: use text-to-video with detailed prompt instead

## Key Patterns

### API Key Reading (avoid *** corruption)
```python
def read_key():
    for p in [os.path.expanduser("~/.hermes/.env"), os.path.expanduser("~/.env")]:
        if os.path.exists(p):
            for ln in open(p):
                if ln.startswith("AGNES_API_KEY=***                    return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return ""
```

### Windows Path Handling
- Shell commands: MSYS paths work (`/d/Hermes/Project/`)
- Python `open()`: must use Windows paths (`D:\Hermes\Project\`)
- Always use `python` not `python3` (python3 → WindowsApps symlink)

### Video Download
```python
r = requests.get(url, timeout=120)
with open("output.mp4", "wb") as f:
    f.write(r.content)
```

## Known Issues
- Video API HTTPS connection can timeout with default 60s — increase to 120s+
- write_file corrupts API keys with `***` — use hex encoding or file-based reading
- Cloudflare CDN: DNS resolves but HTTPS handshake may timeout on first attempt
