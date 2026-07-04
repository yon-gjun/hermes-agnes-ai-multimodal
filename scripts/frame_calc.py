#!/usr/bin/env python3
"""Calculate 8n+1 frame count for Agnes Video V2.0 from target duration."""
import sys

def frames_for_duration(duration_s, fps=24):
    """Return nearest 8n+1 frame count for given duration."""
    raw = int(round(duration_s * fps))
    if raw % 8 != 1:
        raw = raw + (1 - raw % 8)
    return raw

if __name__ == "__main__":
    durations = [float(d) for d in sys.argv[1:]] if len(sys.argv) > 1 else [5, 10, 15, 20, 30]
    fps = 24
    print(f"{'Duration (s)':>12} | {'Raw Frames':>10} | {'8n+1 Frames':>11} | {'8n+1 Duration':>14}")
    print("-" * 60)
    for d in durations:
        raw = int(round(d * fps))
        n8p1 = raw + (1 - raw % 8) if raw % 8 != 1 else raw
        dur_n8p1 = n8p1 / fps
        print(f"{d:>12.1f} | {raw:>10d} | {n8p1:>11d} | {dur_n8p1:>14.2f}s")
