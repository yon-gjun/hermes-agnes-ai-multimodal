#!/usr/bin/env python3
"""持续监控 Agnes 视频生成任务"""
import requests, time, os, json

VIDEO_ID = "video_bGl0ZWxsbMpjdXN0b21fbGxtX3Byb3ZpZGVyOm9wZW5haTttb2RlbF9pZDphZ25lcy12aWRlby12Mi4wO3ZpZGVvX2lkOnZpZGVvXzY1OTUxOTg4ZDA1NGI5OGE3OGI1MzlkNDhjMjg3ZTg4ZDY3ZTExMWQzM2JkMWFiYw=="
AK = "AGNES_API_KEY"
API_KEY=os.getenv(AK, "")

# 从 .env 读取
if not API_KEY:
    for p in [os.path.expanduser("~/.hermes/.env"), os.path.expanduser("~/.env")]:
        if os.path.exists(p):
            try:
                for ln in open(p):
                    ln = ln.strip()
                    if ln.startswith(AK + "="):
                        API_KEY = ln[len(AK)+1:].strip().strip('"').strip("'")
                        if API_KEY: break
            except: pass
        if API_KEY: break

if not API_KEY:
    print("[Error] No API key found")
    exit(1)

RETRIEVE_URL = "https://apihub.agnes-ai.com/agnesapi"

print(f"[Watcher] 监控视频任务...")
print(f"[Watcher] Video ID: {VIDEO_ID[:50]}...")

for i in range(120):
    try:
        params = {"video_id": VIDEO_ID, "model_name": "agnes-video-v2.0"}
        headers = {"Authorization": "Bearer " + API_KEY}
        resp = requests.get(RETRIEVE_URL, params=params, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            state = data.get("state", data.get("status", "unknown"))
            print(f"\r[Watcher] 状态: {state} (尝试 {i+1}/120)", end="", flush=True)
            if state in ["completed", "success", "done"]:
                print(f"\n[Watcher] OK 视频生成完成！")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                video_url = None
                for key in ["video_url", "url", "video", "output_url", "result_url", "remixed_from_video_id"]:
                    if key in data:
                        val = data[key]
                        if isinstance(val, str) and ("http" in val or val.endswith(".mp4")):
                            video_url = val
                            break
                        elif isinstance(val, dict):
                            for sk in ["url", "video", "download_url"]:
                                if sk in val:
                                    video_url = val[sk]
                                    break
                if video_url:
                    print(f"[Watcher] 正在下载...")
                    vr = requests.get(video_url, timeout=120)
                    with open("agnes_output_video.mp4", "wb") as f:
                        f.write(vr.content)
                    print(f"[Watcher] OK 已保存到: agnes_output_video.mp4")
                    print(f"[Watcher] 大小: {len(vr.content)/1024/1024:.2f} MB")
                else:
                    print(f"[Watcher] 未找到视频URL，字段:")
                    for k, v in data.items():
                        print(f"  {k}: {str(v)[:200]}")
                break
            elif state in ["failed", "error", "fail"]:
                print(f"\n[Watcher] 生成失败: {data}")
                break
            time.sleep(15)
        else:
            print(f"\r[Watcher] HTTP {resp.status_code}, 重试中...", end="", flush=True)
            time.sleep(15)
    except Exception as e:
        print(f"\r[Watcher] 错误: {e}, 重试中...", end="", flush=True)
        time.sleep(10)
