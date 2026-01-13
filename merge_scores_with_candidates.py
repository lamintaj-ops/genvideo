import pandas as pd

SCORES = "canto_clip_scores.csv"
CANDIDATES = "canto_candidates.csv"
OUT = "canto_scores_with_urls.csv"

scores = pd.read_csv(SCORES)
cand = pd.read_csv(CANDIDATES)

scores["asset_id"] = scores["asset_id"].astype(str)
cand["asset_id"] = cand["asset_id"].astype(str)

merged = scores.merge(
    cand[["asset_id", "download_url", "filename"]],
    on="asset_id",
    how="left"
)

merged.to_csv(OUT, index=False, encoding="utf-8-sig")

print("✅ Output:", OUT)
print("rows:", len(merged))
print("missing download_url:", merged["download_url"].isna().sum())
