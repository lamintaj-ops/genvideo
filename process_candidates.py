# process_candidates.py

import requests
import pandas as pd
from tqdm import tqdm
from pathlib import Path

from video_quality import analyze_video_file, decide_usable
from smart_analyze import motion_score, brightness_score, face_score


OUTPUT_RESULTS_CSV = "canto_clip_scores.csv"
INPUT_CANDIDATES_CSV = "canto_candidates.csv"
TEMP_VIDEO_PATH = "temp_video.mp4"  # ไฟล์ชั่วคราว ใช้ทับไปเรื่อย ๆ


def download_file(url, out_path):
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def main():
    df = pd.read_csv(INPUT_CANDIDATES_CSV)

    # ---------- 1) เช็คว่ามีไฟล์ผลลัพธ์เดิมมั้ย (ไว้ resume) ----------
    output_path = Path(OUTPUT_RESULTS_CSV)
    processed_ids = set()

    if output_path.exists():
        old = pd.read_csv(OUTPUT_RESULTS_CSV)
        if "asset_id" in old.columns:
            processed_ids = set(old["asset_id"].dropna().astype(str))
        print(f"พบผลลัพธ์เก่า {len(processed_ids)} รายการ จะข้าม asset_id ที่ทำไปแล้ว")

    # แปลง asset_id เป็น string เพื่อเทียบ set ได้เป๊ะ
    df["asset_id"] = df["asset_id"].astype(str)

    # เลือกเฉพาะแถวที่ยังไม่เคยทำ
    mask = ~df["asset_id"].isin(processed_ids)
    df_todo = df[mask].copy()

    print(f"มีคลิปที่ต้องประมวลผลรอบนี้ {len(df_todo)} รายการ จากทั้งหมด {len(df)}")

    # ---------- 2) loop ทีละไฟล์ + เขียน CSV ทันที ----------
    first_write = not output_path.exists() or output_path.stat().st_size == 0

    for _, row in tqdm(df_todo.iterrows(), total=len(df_todo), desc="Processing candidates"):
        asset_id = row.get("asset_id")
        filename = row.get("filename")
        download_url = row.get("download_url")

        def write_result(result_row: dict):
            # เขียนเพิ่มทีละ 1 แถวลง CSV (append mode)
            nonlocal first_write
            out_df = pd.DataFrame([result_row])
            out_df.to_csv(
                OUTPUT_RESULTS_CSV,
                mode="a",
                header=first_write,     # เขียน header แค่ครั้งแรก
                index=False,
                encoding="utf-8-sig",
            )
            first_write = False  # ครั้งต่อ ๆ ไปไม่ต้องเขียน header แล้ว

        # ไม่มี download_url → ไม่ต้องทำต่อ
        if not isinstance(download_url, str) or not download_url.startswith("http"):
            write_result({
                "asset_id": asset_id,
                "filename": filename,
                "status": "no_download_url",
                "error": "",
                "sharp_mean": None,
                "sharp_median": None,
                "brightness_mean": None,
                "motion_mean": None,
                "decision": "reject",
            })
            continue

        # 1) ดาวน์โหลดไฟล์
        try:
            download_file(download_url, TEMP_VIDEO_PATH)
        except Exception as e:
            write_result({
                "asset_id": asset_id,
                "filename": filename,
                "status": "error_download",
                "error": str(e),
                "sharp_mean": None,
                "sharp_median": None,
                "brightness_mean": None,
                "motion_mean": None,
                "decision": "reject",
            })
            continue

        # 2) วิเคราะห์วิดีโอ
        metrics = analyze_video_file(TEMP_VIDEO_PATH)
        if metrics is None:
            write_result({
                "asset_id": asset_id,
                "filename": filename,
                "status": "error_analyze",
                "error": "cannot_read_video",
                "sharp_mean": None,
                "sharp_median": None,
                "brightness_mean": None,
                "motion_mean": None,
                "decision": "reject",
            })
        else:
            decision = decide_usable(metrics)
            write_result({
                "asset_id": asset_id,
                "filename": filename,
                "status": "ok",
                "error": "",
                **metrics,
                "decision": decision,
            })

        # 3) ลบไฟล์ชั่วคราว
        try:
            Path(TEMP_VIDEO_PATH).unlink(missing_ok=True)
        except Exception:
            pass

    print(f"เสร็จแล้วนะ ผลลัพธ์อยู่ในไฟล์: {OUTPUT_RESULTS_CSV}")


if __name__ == "__main__":
    main()
