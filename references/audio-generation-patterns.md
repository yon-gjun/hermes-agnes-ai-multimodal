# Audio Generation Patterns

## Generating Chinese-style music with Python + numpy

When a WAV file is needed for video background music, generate it programmatically using numpy arrays rather than relying on external tools.

### Chinese pentatonic scale
- 宫=Do=C4=262Hz, 商=Re=D4=294Hz, 角=Mi=E4=330Hz, 徵=Sol=G4=392Hz, 羽=La=A4=440Hz
- Higher octave: C5=523, D5=587, E5=659, G5=784

### Plucked string timbre (琵琶/古筝)
Use sharp attack + fast exponential decay:
```python
note_t = t[mask] - current_time
attack = np.exp(-note_t * 30)
melody[mask] = freq_component * np.sin(2*pi*freq*note_t) * attack
# Add harmonics for richness
melody[mask] += 0.15 * np.sin(2*pi*freq*2*note_t) * np.exp(-note_t * 15)
```

### Chinese drum pattern (鼓)
Deep rhythmic hits with 160 BPM galloping feel:
- Strong beat (even): 60Hz sine, sharp attack, quick decay
- Light slap (odd): 100Hz sine, faster decay
- Gallop fill every 8 beats: double-hit at beat+6

### Cymbal shimmer (钹)
High-frequency metallic sound at 4000-6000Hz with fast decay.

### Bass drone
Sustained low note at ~131Hz (C3) throughout.

### WAV file format
```python
import struct
with open("output.wav", "wb") as f:
    f.write(b"RIFF")
    f.write(struct.pack("<I", 36 + len(data)))
    f.write(b"WAVE")
    f.write(b"fmt ")
    f.write(struct.pack("<HHIIHH", 1, 1, sr, sr*2, 2, 16))
    f.write(b"data")
    f.write(struct.pack("<I", len(data)))
    f.write(data)
```

## Crowd/stadium noise generation
Use filtered random noise with periodic bursts:
- Base murmur: low-pass filtered white noise
- Cheering waves: noise bursts at rally intervals
- Clapping: sharp noise hits at 4Hz rhythm
- Peak cheering: high-intensity bursts at match climax moments
