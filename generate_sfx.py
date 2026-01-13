import os
import wave
import numpy as np
from pathlib import Path

SFX_DIR = Path("sfx")
SFX_DIR.mkdir(exist_ok=True)

def save_wav(filename, samples, samplerate=44100):
    filepath = SFX_DIR / filename
    with wave.open(str(filepath), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)      # 16-bit PCM
        wf.setframerate(samplerate)
        wf.writeframes(samples.astype(np.int16).tobytes())
    print(f"Created: {filepath}")

# -----------------------------
# GENERATORS FOR ARTIFICIAL SFX
# -----------------------------

def generate_splash(duration=0.28, samplerate=44100):
    t = np.linspace(0, duration, int(duration * samplerate))
    noise = np.random.randn(len(t)) * np.exp(-t * 10)
    noise *= 8000
    return noise

def generate_splash_hit(duration=0.20, samplerate=44100):
    t = np.linspace(0, duration, int(duration * samplerate))
    noise = np.random.randn(len(t)) * np.exp(-(t * 14))
    noise *= 10000
    return noise

def generate_whoosh(duration=0.35, samplerate=44100, strong=False):
    t = np.linspace(0, duration, int(duration * samplerate))
    freq = 300 + 1200 * t
    tone = np.sin(2 * np.pi * freq * t)
    env = np.exp(-t * (4 if not strong else 2))
    whoosh = tone * env * (6000 if strong else 3000)
    return whoosh

def generate_sparkle(duration=0.45, samplerate=44100):
    t = np.linspace(0, duration, int(duration * samplerate))
    freqs = [800, 1200, 1600]
    signal = sum(np.sin(2*np.pi*f*t) for f in freqs)
    signal *= np.exp(-t * 3) * 3000
    return signal

# -----------------------------
# SAVE ALL FILES
# -----------------------------

save_wav("splash1.wav",       generate_splash())
save_wav("splash_hit.wav",    generate_splash_hit())
save_wav("whoosh_soft.wav",   generate_whoosh(strong=False))
save_wav("whoosh_strong.wav", generate_whoosh(strong=True))
save_wav("sparkle_outro.wav", generate_sparkle())

print("\nAll SFX generated successfully! 🎉")
