# filter_candidates.py

import pandas as pd

INPUT_METADATA_CSV = "canto_metadata.csv"
OUTPUT_CANDIDATES_CSV = "canto_candidates.csv"

def main():
    df = pd.read_csv(INPUT_METADATA_CSV)

    # เอาเฉพาะคลิปที่มี download_url จริง ๆ
    df = df[df["download_url"].notna()]

    # ถ้าอยากทดลองแค่ 200 คลิปก่อน (กันเน็ต/เวลา) ให้ uncomment บรรทัดนี้:
    # df = df.head(200)

    print(f"เอา {len(df)} คลิปจากทั้งหมด {len(df)} ไปวิเคราะห์คุณภาพต่อ")
    df.to_csv(OUTPUT_CANDIDATES_CSV, index=False, encoding="utf-8-sig")
    print(f"บันทึกลงไฟล์: {OUTPUT_CANDIDATES_CSV}")

if __name__ == "__main__":
    main()
