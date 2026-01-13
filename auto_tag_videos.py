# auto_tag_videos.py

import json
import pandas as pd
import requests
from pathlib import Path
from tqdm import tqdm
import cv2
from PIL import Image

import torch
import open_clip

from tag_config import TAG_CATEGORIES

INPUT_SCORES = "canto_scores_with_urls.csv"
OUTPUT_TAGS = "canto_clip_tags.csv"
TEMP_VIDEO = "temp_tag.mp4"


def download_file(url, out_path):
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)


def extract_frames(video_path, num_frames=5):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        cap.release()
        return []

    idxs = [int(x) for x in torch.linspace(0, frame_count - 1, steps=min(num_frames, frame_count)).tolist()]

    frames = []
    for idx in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        frames.append(pil_img)

    cap.release()
    return frames


def build_tag_list():
    tags = []
    for cat, phrases in TAG_CATEGORIES.items():
        for p in phrases:
            tags.append((cat, p))
    return tags


def main():
    df = pd.read_csv(INPUT_SCORES)

    # ใช้เฉพาะที่ status ok และ decision usable (แนะนำ)
    df = df[(df["status"] == "ok") & (df["decision"] == "usable")].copy()
    df["asset_id"] = df["asset_id"].astype(str)

    # resume
    out_path = Path(OUTPUT_TAGS)
    done_ids = set()
    if out_path.exists():
        old = pd.read_csv(out_path)
        if "asset_id" in old.columns:
            done_ids = set(old["asset_id"].astype(str))
        print(f"มีผล tag เดิมแล้ว {len(done_ids)} รายการ → จะข้ามที่ทำไปแล้ว")

    df_todo = df[~df["asset_id"].isin(done_ids)].copy()
    print("จะทำ tagging รอบนี้:", len(df_todo))

    # Load CLIP
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="openai")
    model = model.to(device)
    tokenizer = open_clip.get_tokenizer("ViT-B-32")

    tag_pairs = build_tag_list()
    tag_texts = [p for _, p in tag_pairs]

    # precompute text embeddings
    with torch.no_grad():
        text_tokens = tokenizer(tag_texts).to(device)
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    first_write = not out_path.exists()

    def append_row(row_dict):
        nonlocal first_write
        pd.DataFrame([row_dict]).to_csv(
            OUTPUT_TAGS,
            mode="a",
            header=first_write,
            index=False,
            encoding="utf-8-sig",
        )
        first_write = False

    for _, row in tqdm(df_todo.iterrows(), total=len(df_todo), desc="Auto tagging"):
        asset_id = row["asset_id"]
        filename = row.get("filename")
        download_url = row.get("download_url")

        if not isinstance(download_url, str) or not download_url.startswith("http"):
            append_row({
                "asset_id": asset_id,
                "filename": filename,
                "status": "no_download_url",
                "top_tags": "",
                "tag_scores_json": "{}",
            })
            continue

        # download
        try:
            download_file(download_url, TEMP_VIDEO)
        except Exception as e:
            append_row({
                "asset_id": asset_id,
                "filename": filename,
                "status": "error_download",
                "top_tags": "",
                "tag_scores_json": json.dumps({"error": str(e)}, ensure_ascii=False),
            })
            continue

        # extract frames
        frames = extract_frames(TEMP_VIDEO, num_frames=5)
        if not frames:
            append_row({
                "asset_id": asset_id,
                "filename": filename,
                "status": "error_frames",
                "top_tags": "",
                "tag_scores_json": json.dumps({"error": "no_frames"}, ensure_ascii=False),
            })
            Path(TEMP_VIDEO).unlink(missing_ok=True)
            continue

        # encode frames
        with torch.no_grad():
            image_inputs = torch.stack([preprocess(img) for img in frames]).to(device)
            image_features = model.encode_image(image_inputs)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            # average similarity across frames
            sims = (image_features @ text_features.T).mean(dim=0).cpu().numpy()

        # map scores back to phrases
        scored = []
        for (cat, phrase), score in zip(tag_pairs, sims):
            scored.append({"category": cat, "tag": phrase, "score": float(score)})

        scored_sorted = sorted(scored, key=lambda x: x["score"], reverse=True)

        top = scored_sorted[:8]  # top 8 tags
        top_tags = ", ".join([t["tag"] for t in top])

        append_row({
            "asset_id": asset_id,
            "filename": filename,
            "status": "ok",
            "top_tags": top_tags,
            "tag_scores_json": json.dumps(scored_sorted[:50], ensure_ascii=False),  # เก็บ top 50 ไว้พอ
        })

        # cleanup
        Path(TEMP_VIDEO).unlink(missing_ok=True)

    print("Done! Output:", OUTPUT_TAGS)


if __name__ == "__main__":
    main()
