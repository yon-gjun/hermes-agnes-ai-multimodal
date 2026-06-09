#!/usr/bin/env python3
import requests, time, os, json

VIDEO_ID = "video_bGl0ZWxsbTpjdXN0b21fbGxtX3Byb3ZpZGVyOm9wZW5haTttb2RlbF9pZDphZ25lcy12aWRlby12Mi4wO3ZpZGVvX2lkOnZpZGVvX2EwMzU2Y2UzZTI5OTE3MjdkNTVlYTU2MDhkOWQ5YTc0MWRkOGIxMWQ4ZWNkOTFiMA=="
AK = "AGNES_API_KEY"
prefix = AK + "="

def read_key():
    k = os.getenv(AK, "")
    if k: return k
    for p in [os.path.expanduser("~/.hermes/.env"), os.path.expanduser("~/.env")]:
        if os.path.exists(p):
            for ln in open(p):
                ln = ln.strip()
                if ln.startswith(prefix):
                    k = ln[len(prefix):].strip().strip(chr(34)).strip(chr(39))
                    if k: break
            if k: break
    return k
API_KEY=API_KEY=read_key()

RETRIEVE_URL = "https://apihub.agnes-ai.com/agnesapi"

print("[Watcher] 监控中秋节10秒视频...")

for i in range(200):
    try:
        params = {"video_id": VIDEO_ID, "model_name": "agnes-video-v2.0"}
        headers = {"Authorization": "Bearer " + API_KEY}
        resp = requests.get(RETRIEVE_URL, params=params, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            state = data.get("state", data.get("status", "unknown"))
            print(f"\r[Watcher] 状态: {state} (尝试 {i+1}/200)", end="", flush=True)
            if state in ["completed", "success", "done"]:
                print(f"\n[Watcher] OK 视频完成！")
                video_url = None
                for key in ["remixed_from_video_id", "video_url", "url", "video", "output_url", "result_url", "download_url"]:
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
                    with open("midautumn_video.mp4", "wb") as f:
                        f.write(vr.content)
                    print(f"[Watcher] OK 已保存: midautumn_video.mp4 ({len(vr.content)/1024/1024:.1f} MB)")
                else:
                    print(f"[Watcher] 未找到URL，字段: {list(data.keys())}")
                break
            elif state in ["failed", "error", "fail"]:
                print(f"\n[Watcher] 失败: {data}")
                break
            time.sleep(15)
        else:
            print(f"\r[Watcher] HTTP {resp.status_code}, 重试...", end="", flush=True)
            time.sleep(15)
    except Exception as e:
        print(f"\r[Watcher] 错误: {e}, 重试...", end="", flush=True)
        time.sleep(10)
