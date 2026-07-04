# Fish Audio Child Voice Reference

## Why OpenAI TTS Cannot Produce Child Voices

OpenAI TTS voices: `alloy, ash, ballad, coral, echo, fable, iris, nova, sage, shimmer` — all adult-sounding. `shimmer` is most youthful but still adult female.

## Fish Audio Alternative

**API:** `POST https://api.fish.audio/v1/tts`
**Auth:** `Authorization: Bearer <API_KEY>`
**Site:** https://fish.audio (free tier available)

### Pre-made Child Voice Model IDs

| Voice | Model ID | Description |
|-------|----------|-------------|
| 儿童 (稚嫩女童) | `101a88bb00a8440e87505582da936960` | Young Chinese girl |
| 小男孩 | `1ba245cfea5d41abbcd3c3fc4bd71ee0` | Young Chinese boy |
| 小孩声音 | `30ee81db5dfd43e49bd4d59acc956de8` | General child voice |
| Child | `d4708472472c406286f5ba27cc4ac1d7` | English child voice |

### Example API Call

```bash
curl -X POST https://api.fish.audio/v1/tts \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"这是最美好的时光","voice":"101a88bb00a8440e87505582da936960","normalize":true,"format":"mp3"}' \
  -o output.mp3
```

### Python Example

```python
import requests
API_KEY = "your_key"
VOICE_ID = "101a88bb00a8440e87505582da936960"  # child girl

resp = requests.post(
    "https://api.fish.audio/v1/tts",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={"text": "这是最美好的时光", "voice": VOICE_ID, "normalize": True, "format": "mp3"},
)
with open("child_narration.mp3", "wb") as f:
    f.write(resp.content)
```

## Session Reference

- **2026-06-15/16:** Amusement park video project. User needed child voice for narration. OpenAI TTS all sounded adult. Fish Audio has dedicated child voice models with pre-made IDs. User needs to register at fish.audio and provide API key.