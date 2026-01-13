import cv2
import numpy as np
import mediapipe as mp

mp_face = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)

# --------------------------------------------------
# 1) Motion Score (Optical Flow)
# --------------------------------------------------
def motion_score(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, prev = cap.read()
    if not ret:
        return 0
    prev = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    scores = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        flow = cv2.calcOpticalFlowFarneback(
            prev, gray, None,
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        mag = np.sqrt(flow[...,0]**2 + flow[...,1]**2)
        scores.append(np.mean(mag))

        prev = gray

    cap.release()
    return float(np.mean(scores)) if scores else 0


# --------------------------------------------------
# 2) Brightness Score (mean V channel)
# --------------------------------------------------
def brightness_score(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        return 0

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    val = hsv[...,2]
    return float(np.mean(val))


# --------------------------------------------------
# 3) Face Score (จำนวนหน้าในเฟรมแรก)
# --------------------------------------------------
def face_score(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        return 0
    cap.release()

    res = mp_face.process(frame[:,:,::-1])
    if not res.detections:
        return 0
    return float(len(res.detections))
