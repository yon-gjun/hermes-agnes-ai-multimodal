# Agnes Video V2.0 Chinese Text Rendering Issue

## Symptom

When generating a video with Agnes Video V2.0 and including Chinese text in the prompt (e.g., asking for subtitles like "过年好,给大家拜年了"), the generated video displays garbled characters, squares, or unreadable symbols instead of the intended Chinese text.

## Root Cause

Agnes Video V2.0 has limited support for rendering non-Latin characters in video output. Chinese characters are complex and require specific font support that the model's rendering pipeline does not reliably provide.

## Evidence

- Session: 2026-06-14
- Prompt included: "底部白色中文字幕'过年好,给大家拜年了'"
- Result: Chinese characters rendered as garbled squares/symbols in the video
- The video itself (scene composition, lighting, quality) was generated correctly

## Workaround

### Option 1: Post-generation subtitle addition with FFmpeg

```bash
ffmpeg -i input.mp4 -vf "drawtext=text='过年好,给大家拜年了':fontsize=32:fontcolor=white:x=(w-tw)/2:y=h-th-80" output.mp4
```

**Caveat:** On Windows + MSYS, `fontconfig` may be missing, causing warnings but drawtext usually still works.

### Option 2: Remove Chinese text from prompt

Simply omit any request for Chinese text/subtitles from the prompt. Generate the scene content only, then add subtitles using professional video editing software (Premiere, Final Cut Pro, DaVinci Resolve).

### Option 3: Use ASS subtitle files

Create a `.ass` subtitle file with proper Chinese font specification, then apply with:

```bash
ffmpeg -i input.mp4 -vf "ass=subtitle.ass" output.mp4
```

**Note:** Requires fontconfig to be properly configured on the host system.

## Related

- `references/download-troubleshooting.md` — Other video generation issues
- `references/astrix-corruption-bug.md` — API key masking issue
