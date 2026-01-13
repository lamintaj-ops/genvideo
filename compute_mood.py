import cv2
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import requests

INPUT = "canto_clip_tags_with_urls.csv"
OUT = "canto_clip_mood.csv"
TEMP = "temp_mood.mp4"

def download(url):
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(TEMP, "wb") as f:
        for c in resp.iter_content(1024*1024):
            f.write(c)

def analyze(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for i in np.linspace(0, total-1, 10).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, frame = cap.read()
        if not ok: continue
        frames.append(frame)
    cap.release()

    if not frames: return None

    frames = np.array(frames)

    brightness = frames.mean()
    contrast = frames.std()

    b = frames[...,0].mean()
    r = frames[...,2].mean()
    temp = (r - b)

    motion = 0
    for i in range(len(frames)-1):
        diff = np.abs(frames[i].astype(int) - frames[i+1].astype(int)).mean()
        motion += diff
    motion /= max(len(frames)-1,1)

    return {
        "mood_brightness": float(brightness),
        "mood_contrast": float(contrast),
        "mood_temp": float(temp),
        "mood_motion": float(motion)
    }

df = pd.read_csv(INPUT)
rows=[]
for _, r in tqdm(df.iterrows(), total=len(df)):
    url = r["download_url"]
    download(url)
    mood = analyze(TEMP)
    if not mood:
        mood={"mood_brightness":None,"mood_contrast":None,"mood_temp":None,"mood_motion":None}
    rows.append({**r, **mood})

pd.DataFrame(rows).to_csv(OUT, index=False, encoding="utf-8-sig")
Path(TEMP).unlink(missing_ok=True)
print("DONE:", OUT)
