import pandas as pd
import sys

DATA = "canto_clip_tags.csv"

def search(prompt: str, top_k=20):
    df = pd.read_csv(DATA)
    df = df[df["status"] == "ok"].copy()
    df["top_tags"] = df["top_tags"].fillna("").astype(str)

    prompt_l = prompt.lower()

    # match แบบ phrase-level (ไม่ split เป็นคำ)
    def score_row(tags):
        tags_l = tags.lower()
        score = 0
        for token in prompt_l.split():
            if token in tags_l:
                score += 1
        return score

    df["match_score"] = df["top_tags"].apply(score_row)
    df = df.sort_values("match_score", ascending=False)

    return df[df["match_score"] > 0].head(top_k)[["asset_id", "filename", "top_tags", "match_score"]]

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "family jumanji waterslide fun"
    print(search(prompt, top_k=20).to_string(index=False))
