import pandas as pd

TAGS = "canto_clip_tags.csv"
CAND = "canto_candidates.csv"
OUT  = "canto_clip_tags_with_urls.csv"

tags = pd.read_csv(TAGS)
cand = pd.read_csv(CAND)

tags["asset_id"] = tags["asset_id"].astype(str)
cand["asset_id"] = cand["asset_id"].astype(str)

merged = tags.merge(
    cand[["asset_id", "download_url", "filename"]],
    on="asset_id",
    how="left",
    suffixes=("", "_cand")
)

# ถ้า filename เดิมว่าง ให้ใช้จาก candidates
if "filename_cand" in merged.columns:
    merged["filename"] = merged["filename"].fillna(merged["filename_cand"])
    merged = merged.drop(columns=["filename_cand"])

merged.to_csv(OUT, index=False, encoding="utf-8-sig")

print("✅ Done:", OUT)
print("Rows:", len(merged))
print("Missing download_url:", merged["download_url"].isna().sum())
