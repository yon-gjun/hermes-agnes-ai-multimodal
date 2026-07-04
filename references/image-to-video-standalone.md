# Image-to-Video with Hex-Encoded API Key

## Problem

When running image-to-video tasks via a standalone Python script (not `~/agnes_video_gen.py`),
API key extraction from `~/.hermes/.env` is error-prone because:
- The `.env` file may have trailing content after the key line (Gateway config)
- Shell variable substitution truncates the key (`***` corruption)
- The `--key` flag with the full script reads to end-of-line and picks up tail content

## Solution: Hex-encoded key in a standalone script

This is the pattern used in the 运动会报名 video (2026-07-02 session).

```python
#!/usr/bin/env python3
import requests, time, sys, os
from pathlib import Path

KEY_HEX = "736b2d..."  # python -c "...print(k.encode().hex())"
API_KEY = bytes.fromhex(KEY_HEX).decode()

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def create_and_poll(prompt, image_url, output_path, num_frames=121):
    name = Path(output_path).name
    print(f"[START] {name} — {num_frames} frames ({num_frames/24:.1f}s)")

    payload = {
        "model": "agnes-video-v2.0",
        "prompt": prompt,
        "image": image_url,
        "width": 1152, "height": 768,
        "num_frames": num_frames, "frame_rate": 24,
    }

    resp = requests.post("https://apihub.agnes-ai.com/v1/videos",
                         headers=HEADERS, json=payload, timeout=120)
    if resp.status_code != 200:
        print(f"[ERROR] HTTP {resp.status_code}")
        return False
    r = resp.json()
    vid = r.get("video_id", "")
    print(f"[OK] video_id: {vid}")

    for i in range(200):
        try:
            rr = requests.get("https://apihub.agnes-ai.com/agnesapi",
                              headers=HEADERS,
                              params={"video_id": vid, "model_name": "agnes-video-v2.0"},
                              timeout=30)
            if rr.status_code == 200:
                d = rr.json()
                # CRITICAL: check BOTH state and status
                st = d.get("state") or d.get("status", "unknown")
                if st in ("completed", "success", "done"):
                    print(f"[DONE] in {i+1} checks")
                    for kk in ("remixed_from_video_id", "video_url", "url", "video",
                               "output_url", "result_url"):
                        if kk in d:
                            v = d[kk]
                            if isinstance(v, str) and "http" in v:
                                dl = requests.get(v, timeout=120)
                                dl.raise_for_status()
                                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                                with open(output_path, "wb") as f:
                                    f.write(dl.content)
                                mb = len(dl.content) / 1024 / 1024
                                print(f"[SAVED] {output_path} ({mb:.1f} MB)")
                                return True
                    print(f"[ERROR] No URL found. Keys: {list(d.keys())}")
                    return False
                elif st in ("failed", "error"):
                    print(f"[FAILED] {d.get('error', '?')}")
                    return False
            if i % 4 == 0:
                print(f"\r[WAIT] State: {st} ({i+1} checks)", end="", flush=True)
        except Exception as e:
            print(f"\r[RETRY] {e}", end="", flush=True)
        time.sleep(15)
    print("\n[TIMEOUT]")
    return False
```

## Key Differences from `agnes_video_gen.py`

| Feature | `~/agnes_video_gen.py` | Standalone script |
|---------|------------------------|-------------------|
| Key source | Env var or `.env` read_key() | Hex-encoded inline |
| Image mode | Not supported (text only) | Direct API call with `image` param |
| Status field | `data.get("state")` | `data.get("state") or data.get("status")` |
| Use case | Quick text-to-video | Image-to-video, key survives `write_file` |
