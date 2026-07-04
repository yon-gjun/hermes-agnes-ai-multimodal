# MiniMax TTS Child Voice IDs for Chinese Narration

When OpenAI TTS cannot produce child/young voices, MiniMax is the best domestic (China-accessible) alternative.

## Registration
- URL: https://platform.minimaxi.com
- Free credits: 300 for new users
- No VPN required

## Child Voice IDs (Chinese Mandarin)

| Voice ID | Display Name |
|----------|-------------|
| `Chinese (Mandarin)_Cute_Spirit` | 可爱精灵童声 |
| `Chinese (Mandarin)_Straightforward_Boy` | 直率男孩 |
| `Chinese (Mandarin)_Pure-hearted_Boy` | 纯真男孩 |
| `Chinese (Mandarin)_Soft_Girl` | 温柔少女 |
| `Chinese (Mandarin)_Crisp_Girl` | 清脆少女 |
| `Chinese (Mandarin)_Warm_Girl` | 温暖少女 |
| `Chinese (Mandarin)_IntellectualGirl` | 知性少女 |
| `Chinese (Mandarin)_Warm_HeartedGirl` | 热心少女 |
| `Chinese (Mandarin)_Laid_BackGirl` | 慵懒少女 |
| `Chinese (Mandarin)_ExplorativeGirl` | 探索少女 |
| `Chinese (Mandarin)_BashfulGirl` | 害羞少女 |

## API Usage

```bash
curl -X POST https://api.minimaxi.com/v1/t2a \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-TTS-01","text":"这是最美好的时光","voice_settings":{"voice_id":"Chinese (Mandarin)_Cute_Spirit"}}'
```

## Notes
- MiniMax TTS supports emotion control via voice parameters
- Output formats: MP3, WAV
- Streaming and non-streaming modes available
- Full docs: https://platform.minimaxi.com/docs