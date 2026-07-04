#!/usr/bin/env python3
"""Agnes Image 2.1 Flash 图片生成器
用法: python agnes_image_gen.py text "提示词"
      python agnes_image_gen.py img2img <图片URL> "提示词"
      python agnes_image_gen.py batch "提示词1" "提示词2"
"""
import requests, sys, os
from pathlib import Path

BASE_URL = "https://apihub.agnes-ai.com/v1"
MODEL = "agnes-image-2.1-flash"
size_map = {"p": "768x1024", "portrait": "768x1024", "l": "1024x768", "landscape": "1024x768", "s": "1024x1024", "square": "1024x1024", "w": "1920x1080", "widescreen": "1920x1080"}
AK = "AGNES_API_KEY"
ST = chr(42) * 3  # three asterisks

def get_key():
    """Read API key from env or .env"""
    k = os.getenv(AK, "")
    if k: return k
    for p in [os.path.expanduser("~/.env"), os.path.join(os.getcwd(), ".env"), os.path.expanduser("~/.hermes/.env")]:
        if os.path.exists(p):
            try:
                with open(p) as f:
                    for ln in f:
                        ln = ln.strip()
                        pre = AK + "="
                        if ln.startswith(pre):
                            k = ln[len(pre):].strip().strip('"').strip("'")
                            if k: return k
            except: pass
    print("[Error] No API key. Use --key or set AGNES_API_KEY")
    sys.exit(1)

def api_post(path, data, key):
    url = BASE_URL + path
    h = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}
    r = requests.post(url, headers=h, json=data, timeout=60)
    if r.status_code != 200:
        print(f"[Error] HTTP {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    return r.json()

def gen_text(prompt, size="1024x768"):
    print(f"[Agnes] Text->Img: {prompt} ({size})")
    d = {"model": MODEL, "prompt": prompt, "size": size, "extra_body": {"response_format": "url"}}
    r = api_post("/images/generations", d, get_key())
    return r["data"][0] if r.get("data") else None

def gen_img2img(img_url, prompt, size="1024x768"):
    print(f"[Agnes] Img2Img: {img_url} ({size})")
    d = {"model": MODEL, "prompt": prompt, "size": size, "image": [img_url], "extra_body": {"response_format": "url"}}
    r = api_post("/images/generations", d, get_key())
    return r["data"][0] if r.get("data") else None

def save_image(url, prefix="gen"):
    print(f"[Agnes] Downloading...")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    out = f"{prefix}.png"
    c = 1
    while Path(out).exists(): out = f"{prefix}_{c}.png"; c += 1
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f: f.write(r.content)
    print(f"[Agnes] Saved: {out} ({len(r.content)/1024:.0f} KB)")
    return out

def main():
    if len(sys.argv) < 2:
        print("Agnes Image 2.1 Flash")
        print("  text <prompt>        文生图")
        print("  img2img <url> <pmt>  图生图")
        print("  batch <pmt1> <pmt2>  批量")
        return

    # --key handling
    key_index = -1
    args = list(sys.argv[1:])
    for i, a in enumerate(args):
        if a == "--key" and i+1 < len(args):
            key_index = i
            break
    if key_index < 0:
        key = get_key()
    else:
        key = args[key_index + 1]
        args = [a for i, a in enumerate(args) if i != key_index and i != key_index + 1]

    if not args: return
    mode = args[0].lower()

    if mode == "text":
        size = "landscape"
        prompts = []
        rest = args[1:]
        for i, a in enumerate(rest):
            if a == "--size" and i+1 < len(rest): size = rest[i+1]
            elif not a.startswith("--"): prompts.append(a)
        prompt = " ".join(prompts)
        if not prompt: print("[Error] Need prompt"); sys.exit(1)
        s = size_map.get(size, "1024x768")
        r = gen_text(prompt, s)
        if r and r.get("url"): save_image(r["url"])

    elif mode == "img2img":
        if len(args) < 3: print("[Error] Need URL and prompt"); return
        s = size_map.get("landscape", "1024x768")
        r = gen_img2img(args[1], " ".join(args[2:]), s)
        if r and r.get("url"): save_image(r["url"], "img2img")

    elif mode == "batch":
        s = size_map.get("landscape", "1024x768")
        for i, p in enumerate(args[1:]):
            r = gen_text(p, s)
            if r and r.get("url"): save_image(r["url"], f"batch_{i+1}")

    else:
        print(f"[Error] Unknown: {mode}")

if __name__ == "__main__":
    main()
