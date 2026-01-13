import requests
import pandas as pd
from tqdm import tqdm

CANTO_BASE_URL = "https://columbiapicturesaquaverse.canto.global/api/v1"  # แก้เป็นของจริง
API_TOKEN = "4f0534d28a7347c7bd18120a9fd5cddd"  # แทนที่ด้วย token จริง

# ตัวอย่าง: โฟลเดอร์/อัลบัมที่อยากดึง (ขึ้นอยู่กับโครง Canto ของคุณ)
TARGET_ALBUM_ID = "ALBUM_ID_HERE"  # ให้ IT บอก หรือดูจาก Canto UI

OUTPUT_METADATA_CSV = "canto_metadata.csv"


def get_headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

def fetch_assets_in_library(limit=1000):
    """
    ดึงรายการวิดีโอทั้งหมดจาก Canto:
    - ใช้ endpoint: /api/v1/video
    - ใช้ start+limit ตามเอกสาร
    - limit สูงสุด 1000 ตาม docs
    """

    all_assets = []
    seen_keys = set()

    start = 0
    page = 1

    while True:
        params = {
            "start": start,   # <-- ใช้ start ตาม docs
            "limit": limit,   # max 1000
            # ถ้าอยาก filter เฉพาะ video ช่วงใดช่วงหนึ่ง เช่น duration/created/owner ฯลฯ
            # ก็ใส่เพิ่มตรงนี้ตาม docs ได้ เช่น:
            # "duration": "1..1200",
            # "approval": "approved",
        }
        url = f"{CANTO_BASE_URL}/video"
        resp = requests.get(url, headers=get_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        found = data.get("found", 0)
        limit_resp = data.get("limit", limit)

        print(f"page {page}: start={start}, ได้ {len(results)} รายการ, found={found}, limit={limit_resp}")

        if not results:
            print("ไม่มี results แล้ว หยุด loop")
            break

        new_in_this_page = 0

        for asset in results:
            # เนื่องจาก result ไม่มี id แบบชัด เราใช้ download URL มาเป็น key กันซ้ำ
            url_info = asset.get("url") or {}
            uniq_key = (
                url_info.get("directUrlOriginal")
                or url_info.get("download")
                or url_info.get("play")
            )

            if not uniq_key:
                continue

            if uniq_key in seen_keys:
                continue

            seen_keys.add(uniq_key)
            all_assets.append(asset)
            new_in_this_page += 1

        print(f"page {page}: เพิ่มใหม่ {new_in_this_page} รายการ, รวมตอนนี้ {len(all_assets)}")

        # ถ้าไม่มีตัวใหม่เลยในหน้านี้ → น่าจะสุดแล้ว
        if new_in_this_page == 0:
            print("หน้านี้ไม่มี asset ใหม่เลย น่าจะสุดแล้ว หยุด loop")
            break

        # ถ้ามี found และเก็บครบแล้ว → หยุด
        if found and len(all_assets) >= found:
            print(f"เก็บครบตาม found แล้ว ({len(all_assets)}/{found}) หยุด")
            break

        # เลื่อน start ไปหน้าถัดไป
        start += limit
        page += 1

    print(f"รวมได้ assets ไม่ซ้ำทั้งหมด {len(all_assets)} รายการ")
    return all_assets






def extract_metadata(asset: dict) -> dict:
    asset_id = asset.get("id")  # ตอนนี้ยังไม่เห็น แต่เผื่อไว้
    filename = asset.get("name") or asset.get("filename")

    # meta อื่น ๆ อาจยังไม่มีใน result นี้ → ปล่อยเป็น None ไปก่อน
    size = None
    duration = None
    width = None
    height = None

    tags_value = asset.get("tags") or asset.get("tag") or []
    if isinstance(tags_value, list):
        tags = ",".join(tags_value)
    else:
        tags = str(tags_value) if tags_value is not None else ""

    folder_path = asset.get("folderPath") or asset.get("folder") or asset.get("albumName")

    url_info = asset.get("url") or {}
    # ใช้ directUrlOriginal ก่อน ถ้าไม่มีค่อย fallback เป็น download
    download_url = url_info.get("directUrlOriginal") or url_info.get("download")
    preview_url = url_info.get("preview")
    play_url = url_info.get("play")

    return {
        "asset_id": asset_id,
        "filename": filename,
        "size_bytes": size,
        "duration_sec": duration,
        "width": width,
        "height": height,
        "tags": tags,
        "folder": folder_path,
        "download_url": download_url,
        "preview_url": preview_url,
        "play_url": play_url,
    }



import json

def main():
    print("ดึง asset metadata จาก Canto ...")
    assets = fetch_assets_in_library()
    print(f"พบ asset ทั้งหมด {len(assets)} รายการ")

    # 🔍 ดูตัวอย่าง asset ตัวแรก
    if assets:
        print("===== SAMPLE ASSET (pretty JSON) =====")
        print(json.dumps(assets[0], ensure_ascii=False, indent=2)[:2000])
        print("======================================")

    rows = []
    for a in tqdm(assets, desc="Processing assets"):
        rows.append(extract_metadata(a))

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_METADATA_CSV, index=False, encoding="utf-8-sig")
    print(f"บันทึก metadata ลงไฟล์: {OUTPUT_METADATA_CSV}")



if __name__ == "__main__":
    main()
