# Video API Connectivity Troubleshooting

## Symptom
- Initial video API calls work (e.g., test_t2v.mp4 generated successfully)
- Subsequent calls timeout consistently
- DNS resolves (ping works) but HTTPS connections fail
- Error: `HTTPSConnectionPool(host='apihub.agnes-ai.com', port=443): Read timed out`

## Diagnosis Steps
1. **Check DNS**: `ping apihub.agnes-ai.com` — should resolve to 104.18.x.x (Cloudflare)
2. **Check connectivity**: `curl -v --connect-timeout 10 https://apihub.agnes-ai.com/v1/videos` — may hang
3. **Check via Python**: `requests.get("https://apihub.agnes-ai.com", timeout=10)` — may work when curl fails (different TLS stack)

## Root Cause
Cloudflare CDN between Hermes and Agnes AI servers. Intermittent connectivity issues are common with this setup.

## Solutions
1. **Wait and retry**: The issue often resolves itself in 2-3 minutes
2. **Increase timeout**: Use `timeout=120` or `timeout=300` for video API requests
3. **Use Python requests instead of curl**: Python's requests library may succeed where curl fails due to different TLS implementation
4. **Check if service is down**: If all retries fail for >10 minutes, the service may be temporarily unavailable

## Working Pattern (from June 27, 2026 test)
```python
# Step 1: Create task with long timeout
r = requests.post(BASE_URL + "/videos", headers=headers, json=payload, timeout=300)

# Step 2: Poll status
r = requests.get(RETRIEVE_URL, params={"video_id": VIDEO_ID, "model_name": MODEL},
                 headers=headers, timeout=30)

# Step 3: Download
dr = requests.get(video_url, timeout=120)
```

## Notes
- Image API (`/v1/images/generations`) tends to be more reliable than video API
- If video API is down, text-to-image and image-to-image usually still work
- The `remixed_from_video_id` field contains the download URL (not `video_url`)