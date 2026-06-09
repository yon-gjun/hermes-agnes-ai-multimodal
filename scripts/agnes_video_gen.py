#!/usr/bin/env python3
"""
Agnes Video V2.0 Video Generator
用法: python agnes_video_gen.py <MODE> <ARGS...>

模式:
  1. 文生视频:    text "提示词"
  2. 图生视频:    image "图片URL" "提示词"
  3. 多图视频:    multi "图片URL1" "图片URL2" "提示词"
  4. 关键帧动画:  keyframe "图片URL1" "图片URL2" "提示词"
  5. 查询状态:    status <video_id>

示例:
  python agnes_video_gen.py text "一家人在草原上放风筝奔跑，阳光温暖"
  python agnes_video_gen.py image "https://example.com/photo.jpg" "人物转身微笑，慢动作"
  python agnes_video_gen.py multi "https://img1.jpg" "https://img2.jpg" "平滑过渡"
  python agnes_video_gen.py keyframe "https://kf1.jpg" "https://kf2.jpg" "关键帧动画"
  python agnes_video_gen.py status abc123def456
"""

import requests
import time
import sys
import os
from pathlib import Path

# ============================================================
# 配置
# ============================================================
BASE_URL = "https://apihub.agnes-ai.com/v1"
RETRIEVE_URL = "https://apihub.agnes-ai.com/agnesapi"
MODEL = "agnes-video-v2.0"
API_KEY = os.getenv("AGNES_VIDEO_API_KEY", "")

# 默认参数
DEFAULT_WIDTH = 1152
DEFAULT_HEIGHT = 768
DEFAULT_NUM_FRAMES = 121    # 符合 8n+1 规则 (8*15+1=121)
DEFAULT_FRAME_RATE = 24
DEFAULT_INFERENCE_STEPS = 30

# ============================================================
# 获取 API Key（支持命令行参数或环境变量）
# ============================================================

def get_api_key():
    """获取 API Key: 命令行参数 > 环境变量 > 提示输入"""
    if len(sys.argv) > 0 and sys.argv[0] == "--key":
        return sys.argv[1]
    
    key = os.getenv("AGNES_VIDEO_API_KEY", "")
    if key:
        return key
    
    # 尝试从 .env 文件读取
    env_paths = [
        os.path.expanduser("~/.env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.expanduser("~/.hermes/.env"),
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("AGNES_API_KEY=") or line.startswith("AGNES_VIDEO_API_KEY="):
                            key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if key:
                                print(f"[Agnes] 从 {env_path} 读取 API Key")
                                return key
            except Exception as e:
                pass
    
    print("[错误] 未找到 API Key")
    print("请通过以下方式提供:")
    print("  1. 命令行: python agnes_video_gen.py --key <YOUR_KEY> ...")
    print("  2. 环境变量: export AGNES_VIDEO_API_KEY=<YOUR_KEY>")
    print("  3. 编辑 .env 文件添加 AGNES_API_KEY=xxx")
    sys.exit(1)


# ============================================================
# 核心函数
# ============================================================

def create_task(api_key: str, mode: str, prompt: str, 
                images: list = None, extra_body: dict = None,
                width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT,
                num_frames: int = DEFAULT_NUM_FRAMES,
                frame_rate: int = DEFAULT_FRAME_RATE,
                inference_steps: int = DEFAULT_INFERENCE_STEPS,
                seed: int = None,
                negative_prompt: str = "") -> dict:
    """创建视频生成任务"""
    
    url = f"{BASE_URL}/videos"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
        "num_inference_steps": inference_steps,
    }
    
    if seed is not None:
        payload["seed"] = seed
    
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    
    # 根据模式添加图片参数
    if images:
        if mode == "multi":
            # 多图视频
            payload["extra_body"] = {
                "image": images,
            }
        elif mode == "keyframe":
            # 关键帧动画
            payload["extra_body"] = {
                "image": images,
                "mode": "keyframes",
            }
        else:
            # 图生视频（单图）
            payload["image"] = images[0]
    
    print(f"[Agnes] 正在创建视频任务...")
    print(f"[Agnes] 模式: {mode}")
    print(f"[Agnes] 提示词: {prompt}")
    print(f"[Agnes] 尺寸: {width}x{height}")
    print(f"[Agnes] 帧数: {num_frames} ({num_frames/24:.1f}秒)")
    if images:
        print(f"[Agnes] 图片: {len(images)} 张")
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"[错误] 创建任务失败: HTTP {response.status_code}")
        print(f"[错误] 响应: {response.text}")
        sys.exit(1)
    
    result = response.json()
    
    task_id = result.get("task_id", "")
    video_id = result.get("video_id", "")
    
    print(f"\n[Agnes] ✅ 任务创建成功！")
    print(f"[Agnes] Task ID: {task_id}")
    print(f"[Agnes] Video ID: {video_id}")
    
    return result, video_id


def retrieve_video(api_key: str, video_id: str, model_name: str = MODEL) -> dict:
    """查询视频生成结果"""
    
    params = {
        "video_id": video_id,
        "model_name": model_name,
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    response = requests.get(RETRIEVE_URL, headers=headers, params=params, timeout=30)
    
    if response.status_code != 200:
        print(f"[错误] 查询失败: HTTP {response.status_code}")
        print(f"[错误] 响应: {response.text}")
        return None
    
    return response.json()


def download_video(video_url: str, output_path: str) -> str:
    """下载视频文件"""
    
    print(f"[Agnes] 正在下载视频...")
    
    response = requests.get(video_url, timeout=120)
    response.raise_for_status()
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    file_size_mb = len(response.content) / (1024 * 1024)
    print(f"[Agnes] ✅ 视频已保存到: {output_path}")
    print(f"[Agnes] 文件大小: {file_size_mb:.2f} MB")
    
    return output_path


def wait_and_download(api_key: str, video_id: str, output_path: str, 
                      model_name: str = MODEL) -> str:
    """等待视频生成完成并下载"""
    
    print(f"\n[Agnes] 等待视频生成中...")
    print(f"[Agnes] 每 15 秒检查一次状态...")
    
    max_attempts = 200  # 最多等待 50 分钟
    for attempt in range(max_attempts):
        try:
            data = retrieve_video(api_key, video_id, model_name)
            
            if data is None:
                print(f"\r[Agnes] 查询失败，重试中... (尝试 {attempt + 1})", end="", flush=True)
                time.sleep(15)
                continue
            
            state = data.get("state", data.get("status", "unknown"))
            
            # 可能的状态字段
            if state in ["completed", "success", "done"]:
                print(f"\n[Agnes] ✅ 视频生成完成！")
                
                # 尝试获取视频 URL
                video_url = None
                for key in ["video_url", "url", "video", "output_url", "result_url", "data", "remixed_from_video_id"]:
                    if key in data:
                        val = data[key]
                        if isinstance(val, str) and ("http" in val or val.endswith(".mp4")):
                            video_url = val
                            break
                        elif isinstance(val, dict):
                            for sub_key in ["url", "video", "download_url"]:
                                if sub_key in val:
                                    video_url = val[sub_key]
                                    break
                        elif isinstance(val, list) and len(val) > 0:
                            video_url = val[0] if isinstance(val[0], str) else None
                            if video_url:
                                break
                
                # 如果上面没找到，检查 common 字段
                if not video_url and "common" in data:
                    common = data["common"]
                    if isinstance(common, dict):
                        for key in ["video_url", "url", "video", "download_url"]:
                            if key in common:
                                video_url = common[key]
                                break
                
                if video_url:
                    return download_video(video_url, output_path)
                else:
                    print(f"[错误] 未找到视频 URL，完整响应: {data}")
                    # 尝试打印所有字段
                    print(f"[Agnes] 可用字段: {list(data.keys())}")
                    sys.exit(1)
                    
            elif state in ["failed", "error", "fail"]:
                print(f"\n\n[Agnes] ❌ 生成失败: {data.get('error', data.get('message', '未知原因'))}")
                sys.exit(1)
            
            else:
                print(f"\r[Agnes] 状态: {state} (尝试 {attempt + 1}/{max_attempts})", end="", flush=True)
                time.sleep(15)
                
        except requests.exceptions.Timeout:
            print(f"\r[Agnes] 超时，重试中... (尝试 {attempt + 1})", end="", flush=True)
            time.sleep(10)
        except Exception as e:
            print(f"\r[Agnes] 错误: {e}，重试中... (尝试 {attempt + 1})", end="", flush=True)
            time.sleep(10)
    
    raise Exception("等待超时 (50分钟)")


# ============================================================
# 便捷函数：一键生成并下载
# ============================================================

def generate_text_to_video(api_key: str, prompt: str,
                           output_path: str = "output_video.mp4",
                           width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT,
                           num_frames: int = DEFAULT_NUM_FRAMES,
                           frame_rate: int = DEFAULT_FRAME_RATE,
                           seed: int = None,
                           negative_prompt: str = "") -> str:
    """一键: 文生视频 -> 等待 -> 下载"""
    
    result, video_id = create_task(
        api_key, "text", prompt,
        width=width, height=height,
        num_frames=num_frames, frame_rate=frame_rate,
        seed=seed, negative_prompt=negative_prompt
    )
    return wait_and_download(api_key, video_id, output_path)


def generate_image_to_video(api_key: str, image_url: str, prompt: str = "",
                            output_path: str = "output_video.mp4",
                            width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT,
                            num_frames: int = DEFAULT_NUM_FRAMES,
                            frame_rate: int = DEFAULT_FRAME_RATE,
                            seed: int = None,
                            negative_prompt: str = "") -> str:
    """一键: 图生视频 -> 等待 -> 下载"""
    
    result, video_id = create_task(
        api_key, "image", prompt or prompt,
        images=[image_url],
        width=width, height=height,
        num_frames=num_frames, frame_rate=frame_rate,
        seed=seed, negative_prompt=negative_prompt
    )
    return wait_and_download(api_key, video_id, output_path)


def generate_multi_image_video(api_key: str, image_urls: list, prompt: str = "",
                               output_path: str = "output_video.mp4",
                               width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT,
                               num_frames: int = DEFAULT_NUM_FRAMES,
                               frame_rate: int = DEFAULT_FRAME_RATE,
                               seed: int = None,
                               negative_prompt: str = "") -> str:
    """一键: 多图视频 -> 等待 -> 下载"""
    
    result, video_id = create_task(
        api_key, "multi", prompt or "Create a smooth transformation scene",
        images=image_urls,
        width=width, height=height,
        num_frames=num_frames, frame_rate=frame_rate,
        seed=seed, negative_prompt=negative_prompt
    )
    return wait_and_download(api_key, video_id, output_path)


def generate_keyframe_video(api_key: str, image_urls: list, prompt: str = "",
                            output_path: str = "output_video.mp4",
                            width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT,
                            num_frames: int = DEFAULT_NUM_FRAMES,
                            frame_rate: int = DEFAULT_FRAME_RATE,
                            seed: int = None,
                            negative_prompt: str = "") -> str:
    """一键: 关键帧动画 -> 等待 -> 下载"""
    
    result, video_id = create_task(
        api_key, "keyframe", prompt or "Generate smooth cinematic transition",
        images=image_urls,
        width=width, height=height,
        num_frames=num_frames, frame_rate=frame_rate,
        seed=seed, negative_prompt=negative_prompt
    )
    return wait_and_download(api_key, video_id, output_path)


# ============================================================
# 主程序
# ============================================================

def main():
    api_key = get_api_key()
    
    # 解析命令行参数
    args = list(sys.argv[1:])
    
    # 查找 --key 参数
    key_index = -1
    for i, arg in enumerate(args):
        if arg == "--key" and i + 1 < len(args):
            api_key = args[i + 1]
            key_index = i
            break
    
    # 去掉 --key 和 API_KEY 参数
    if key_index >= 0:
        args = [a for i, a in enumerate(args) if i != key_index and i != key_index + 1]
    
    if len(args) == 0:
        print("=" * 60)
        print("🎬 Agnes Video V2.0 视频生成器")
        print("=" * 60)
        print()
        print("用法:")
        print()
        print("  1️⃣  文生视频:")
        print(f'     python {sys.argv[0]} --key <API_KEY> text "提示词"')
        print()
        print("  2️⃣  图生视频:")
        print(f'     python {sys.argv[0]} --key <API_KEY> image <图片URL> "提示词"')
        print()
        print("  3️⃣  多图视频:")
        print(f'     python {sys.argv[0]} --key <API_KEY> multi <URL1> <URL2> "提示词"')
        print()
        print("  4️⃣  关键帧动画:")
        print(f'     python {sys.argv[0]} --key <API_KEY> keyframe <URL1> <URL2> "提示词"')
        print()
        print("  5️⃣  查询状态:")
        print(f'     python {sys.argv[0]} --key <API_KEY> status <VIDEO_ID>')
        print()
        print("=" * 60)
        print("参数说明:")
        print(f'     模型:  {MODEL}')
        print(f'     帧数:  必须符合 8n+1 规则 (如 121 = 8×15+1)')
        print(f'     帧率:  1-60 FPS')
        print("=" * 60)
        return
    
    if len(args) < 1:
        print("[错误] 参数不足")
        sys.exit(1)
    
    mode = args[0]
    args_rest = args[1:]
    
    try:
        if mode == "status":
            video_id = args_rest[0] if args_rest else ""
            print(f"[Agnes] 查询视频状态: {video_id}")
            data = retrieve_video(api_key, video_id)
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        elif mode == "text":
            prompt = " ".join(args_rest) if args_rest else ""
            if not prompt:
                print("[错误] 文生视频需要提示词")
                return
            output = generate_text_to_video(api_key, prompt)
            print(f"\n🎉 完成！视频文件: {output}")
            
        elif mode == "image":
            image_url = args_rest[0] if len(args_rest) > 0 else ""
            prompt = " ".join(args_rest[1:]) if len(args_rest) > 1 else ""
            if not image_url:
                print("[错误] 图生视频需要提供图片URL")
                return
            output = generate_image_to_video(api_key, image_url, prompt)
            print(f"\n🎉 完成！视频文件: {output}")
            
        elif mode == "multi":
            image_urls = args_rest[:2]
            prompt = " ".join(args_rest[2:]) if len(args_rest) > 2 else ""
            if len(image_urls) < 2:
                print("[错误] 多图视频需要至少2张图片URL")
                return
            output = generate_multi_image_video(api_key, image_urls, prompt)
            print(f"\n🎉 完成！视频文件: {output}")
            
        elif mode == "keyframe":
            image_urls = args_rest[:2]
            prompt = " ".join(args_rest[2:]) if len(args_rest) > 2 else ""
            if len(image_urls) < 2:
                print("[错误] 关键帧动画需要至少2张图片URL")
                return
            output = generate_keyframe_video(api_key, image_urls, prompt)
            print(f"\n🎉 完成！视频文件: {output}")
            
        else:
            print(f"[错误] 未知模式: {mode}")
            print("可用模式: text, image, multi, keyframe, status")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[错误] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
