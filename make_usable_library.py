import pandas as pd
import numpy as np

INPUT = "canto_clip_scores.csv"
OUT_USABLE = "usable_clips.csv"

df = pd.read_csv(INPUT)

# เอาเฉพาะที่วิเคราะห์สำเร็จ
df = df[df["status"] == "ok"].copy()

# normalize ฟีเจอร์ให้กลายเป็น 0–1
def norm(x, lo, hi):
    return np.clip((x - lo) / (hi - lo), 0, 1)

df["sharp_n"] = norm(df["sharp_median"], 50, 250)
df["bright_n"] = 1 - norm(abs(df["brightness_mean"] - 140), 0, 80)  # ค่ากลางสวย ~140
df["motion_n"] = norm(df["motion_mean"], 1, 8)

# รวมคะแนนเป็น 0–100
df["quality_score"] = (
    df["sharp_n"] * 45 +
    df["bright_n"] * 25 +
    df["motion_n"] * 30
)

df["quality_score"] = df["quality_score"].round(1)

# usable แบบ stricter (ตัวอย่าง)
usable = df[df["quality_score"] >= 70].copy()

usable.to_csv(OUT_USABLE, index=False, encoding="utf-8-sig")
print("Done! usable clips:", len(usable))
print("Output:", OUT_USABLE)
