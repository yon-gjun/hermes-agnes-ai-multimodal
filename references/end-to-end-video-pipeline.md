# End-to-End Video Pipeline

## Overview

Consolidated reference for the full video production workflow: scene generation (text-to-video or image-to-video with shared reference frame) → TTS narration → frame alignment → FFmpeg concatenation → transitions → audio mixing → Chinese subtitle embedding.

Supersedes `tts-narration-pipeline.md` and `video-production-pipeline.md`.

## Pipeline Steps

### Step 0: Generate a Reference Image (for character/background consistency)

When multiple scenes share the same characters and setting (e.g. "4 students in a classroom"), generate one
reference image via `image_generate` (FAL), then use image-to-video for **all** scenes. This preserves
facial features, clothing/uniforms, hairstyles, classroom setup, and lighting across every clip.

```
image_generate(prompt="All 4 characters described in detail...", aspect_ratio="landscape")
```

### Step 1: Generate TTS First, Then Set Frame Count

Always generate narration before deciding video duration. "旁白完成后镜头才能结束" means video length
must match actual speech, not the other way around.

```python
text_to_speech(text="旁白内容", output_path="...voiceN.mp3")
```

Measure TTS duration with ffprobe:

```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 voice1.mp3
# → 6.12 → ceil(6.12*24)=147 → nearest 8n+1 = 145 or 153
```

### Step 1b: Generate Video Scenes

Two modes depending on consistency needs:

**A. Text-to-video** (fast, but characters may vary between scenes):
```bash
cd ~/AppData/Local/hermes
python ~/agnes_video_gen.py text "scene prompt" segN.mp4 --frames 121
```

**B. Image-to-video** (shared reference URL = consistent characters):
```bash
python ~/agnes_video_gen_full.py --key <KEY> image <REF_URL> "prompt" segN.mp4 --frames 121
```

Each call takes ~120-150s. Run sequentially to avoid API rate limits (429 errors).
Use `delegate_task` for parallel generation, but be aware of rate limits.

### Step 2: Concatenate Video Segments

```bash
printf "file 'seg1.mp4'\nfile 'seg2.mp4'\n..." > concat_list.txt
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy -y merged.mp4
```

### Step 3: Apply Crossfade Transitions

Replace hard cuts with dissolve transitions using FFmpeg's `xfade` filter:

```bash
# For 2-clip dissolve: trim each clip separately, then xfade
ffmpeg -i merged.mp4 -filter_complex \
  "split[a][b];[a]trim=0:6,setpts=PTS-STARTPTS[c1];\
   [b]trim=6:11,setpts=PTS-STARTPTS[c2];\
   [c1][c2]xfade=transition=fade:duration=0.5:offset=5.5,setpts=PTS-STARTPTS[outv]" \
  -map "[outv]" -c:v libx264 -y dissolved.mp4
```

Adjust `trim` and `offset` values to actual clip boundary timestamps.

### Step 4: Mix Narration + Background Music

```bash
ffmpeg -i merged.mp4 -i bgm.mp3 \
  -i tts_seg1_pad.mp3 -i tts_seg2_pad.mp3 ... \
  -filter_complex "[2:a][3:a][4:a][5:a][6:a][7:a]concat=n=6:v=0:a=1[narr];\
[narr]volume=0.75[a1];[1:a]volume=0.4[a2];[a1][a2]amix=inputs=2:duration=first[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac -b:a 192k -movflags +faststart \
  -y final_audio.mp4
```

Volume levels: narration 0.75 (dominant), background music 0.4 (subtle).

### Step 6: Embed Chinese Subtitles (ASS)

Convert SRT to ASS (better Chinese rendering with Microsoft YaHei font):

```bash
ffmpeg -i final_audio.mp4 -vf "ass=subtitles.ass" \
  -c:v libx264 -preset medium -crf 23 -c:a copy -y final_output.mp4
```

ASS file must have `PlayResX/Y` matching video resolution, and `Fontname: Microsoft YaHei`.

### Step 7: Verify

```bash
ffprobe -v quiet -print_format json -show_format final_output.mp4
```

## Key Decision: Pad TTS vs Extend Video

| Strategy | When to use | How |
|----------|------------|-----|
| Pad TTS with silence | Video length is fixed (e.g. 5s per scene) | `ffmpeg -i v.mp3 -af "apad=pad_dur=5,atrim=0:5"` |
| Extend video to TTS length | "旁白完成后镜头才能结束" | Generate TTS first, calc 8n+1 frames, then gen video |

## Common Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Duration too short | Video generated before TTS alignment | Generate TTS first, calc frames |
| Characters look different across scenes | Text-to-video per scene | Use image-to-video with shared ref URL |
| Hard cuts between scenes | No transition effect | Apply `xfade` with 0.5s dissolve |
| Rate limit (429) | Too many API calls | Wait 60-75s between requests |
| Subtitles garbled | drawtext for Chinese | Use `ass=` with Microsoft YaHei |
| `write_file` fails | Mounted directory | Use `terminal cat >` |

## Volume Reference (Tested Working)

- Narration (TTS): 0.75 (75%) — dominant voice
- Background music: 0.4 (40%) — subtle support
- Original video audio: 0.25 (25%) — ambient context

## FFmpeg Filter Details

- `apad=pad_dur=N` — pad with silence until at least N seconds
- `atrim=0:N` — trim to exactly N seconds after padding
- `concat=n=N:v=0:a=1` — concatenate N audio clips, no video
- `amix=inputs=N:duration=first` — mix N audio sources, match longest duration
