# Agnes Video Download Troubleshooting

## 2026-06-14: Download failures

### Problem
Video generation succeeded (state=completed) but download failed with:
- `NoSuchKey` on direct URL access (URL was truncated by URL encoding)
- `404` on constructed URL
- `FileNotFoundError` on Windows path

### Root Causes
1. **URL truncation**: `web_extract` and other tools may truncate long base64-encoded video IDs
2. **Path resolution**: On Windows with MSYS/bash, `~/Desktop` may not resolve correctly. Use absolute `/c/Users/yon-g/Desktop/` paths.
3. **DNS issues**: `curl` may fail with `getaddrinfo() thread failed to start`. Use Python `requests` instead.

### Working Pattern
1. Generate video, poll until `completed`
2. Print all response fields: `print("Fields:", list(data.keys()))`
3. Extract URL from `remixed_from_video_id` (NOT `video_url`)
4. Download with Python `requests.get()`, save to simple path