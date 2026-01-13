# video_quality.py

import cv2
import numpy as np

NUM_FRAMES_SAMPLE = 10  # จะสุ่มดูประมาณ 10 เฟรมต่อคลิป

def calc_sharpness(frame_gray):
    lap = cv2.Laplacian(frame_gray, cv2.CV_64F)
    return lap.var()

def calc_brightness(frame_gray):
    return float(frame_gray.mean())

def analyze_video_file(path, num_samples=NUM_FRAMES_SAMPLE):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count == 0:
        cap.release()
        return None

    idxs = np.linspace(0, frame_count - 1, num=min(num_samples, frame_count), dtype=int)

    sharpness_list = []
    brightness_list = []
    motion_list = []

    prev_gray = None

    for idx in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        s = calc_sharpness(gray)
        b = calc_brightness(gray)
        sharpness_list.append(s)
        brightness_list.append(b)

        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            m = float(diff.mean())
            motion_list.append(m)

        prev_gray = gray

    cap.release()

    if not sharpness_list:
        return None

    sharp_mean = float(np.mean(sharpness_list))
    sharp_median = float(np.median(sharpness_list))
    bright_mean = float(np.mean(brightness_list))
    motion_mean = float(np.mean(motion_list)) if motion_list else 0.0

    return {
        "sharp_mean": sharp_mean,
        "sharp_median": sharp_median,
        "brightness_mean": bright_mean,
        "motion_mean": motion_mean,
    }


# เกณฑ์ตัดสินเบื้องต้น (ปรับได้)
MIN_SHARPNESS   = 80
MIN_BRIGHTNESS  = 40
MAX_BRIGHTNESS  = 220
MIN_MOTION      = 2.0

def decide_usable(metrics: dict) -> str:
    s = metrics["sharp_median"]
    b = metrics["brightness_mean"]
    m = metrics["motion_mean"]

    if (
        s >= MIN_SHARPNESS
        and MIN_BRIGHTNESS <= b <= MAX_BRIGHTNESS
        and m >= MIN_MOTION
    ):
        return "usable"
    else:
        return "reject"
