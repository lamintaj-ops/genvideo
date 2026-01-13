# clip_selector.py

import random
import pandas as pd

# ------------------------------
# 1) Score จาก prompt
# ------------------------------
def score_by_prompt(top_tags: str, prompt_info: dict):
    tags = (top_tags or "").lower()
    score = 0

    for t in prompt_info["themes"]:
        if t in tags:
            score += 4

    if prompt_info["vibe"] in tags:
        score += 1

    return score

# ------------------------------
# 2) Mood similarity score
# ------------------------------
def mood_score(r, desired):
    if (
        pd.isna(r["mood_brightness"]) or 
        pd.isna(r["mood_contrast"]) or 
        pd.isna(r["mood_temp"]) or
        pd.isna(desired["brightness"]) or
        pd.isna(desired["contrast"]) or
        pd.isna(desired["temp"])
    ):
        return 0

    score = 0

    if abs(r["mood_brightness"] - desired["brightness"]) < 30:
        score += 2

    if abs(r["mood_contrast"] - desired["contrast"]) < 20:
        score += 1

    if abs(r["mood_temp"] - desired["temp"]) < 15:
        score += 1

    return score

# ------------------------------
# 3) Rank clips by mood + prompt
# ------------------------------
def rank_clips(df: pd.DataFrame, prompt_info: dict):

    df["prompt_score"] = df["top_tags"].apply(
        lambda t: score_by_prompt(t, prompt_info)
    )

    desired_mood = {
        "brightness": df["mood_brightness"].median(),
        "contrast": df["mood_contrast"].median(),
        "temp": df["mood_temp"].median()
    }

    df["mood_match"] = df.apply(lambda r: mood_score(r, desired_mood), axis=1)

    df["overall"] = df["prompt_score"] * 2 + df["mood_match"]

    return df.sort_values("overall", ascending=False)


# ------------------------------
# 4) Signature Story Structure
# ------------------------------
def select_signature_story(df_ranked):

    # Copy Working DataFrame
    df_work = df_ranked.copy()
    final_rows = []

    sections = {
        "hook":      {"motion": "high", "count": 1},
        "action":    {"motion": "mid-high", "count": 2},
        "family":    {"tags": ["family", "smile", "group"], "count": 1},
        "ride":      {"tags": ["slide", "splash", "ride"], "count": 1},
        "ending":    {"motion": "low", "brightness": "high", "count": 1}
    }

    for section, rules in sections.items():
        subset = df_work.copy()

        # Motion rules
        if "motion" in rules:
            if rules["motion"] == "high":
                subset = subset[subset["mood_motion"] > df_ranked["mood_motion"].quantile(0.75)]
            elif rules["motion"] == "mid-high":
                subset = subset[subset["mood_motion"] > df_ranked["mood_motion"].median()]
            elif rules["motion"] == "low":
                subset = subset[subset["mood_motion"] < df_ranked["mood_motion"].median()]

        # Brightness rules
        if "brightness" in rules and rules["brightness"] == "high":
            subset = subset[subset["mood_brightness"] > df_ranked["mood_brightness"].median()]

        # Tags rules (fix None case)
        if "tags" in rules:
            subset = subset[
                subset["top_tags"].fillna("").str.lower().apply(
                    lambda t: any(tag in t for tag in rules["tags"])
                )
            ]

        # Select top clips for this section
        chosen = subset.head(rules["count"])
        final_rows.append(chosen)

        # Remove selected rows to avoid duplicates
        df_work = df_work.drop(chosen.index)

    story = pd.concat(final_rows, ignore_index=True)
    return story


# ------------------------------
# 5) MAIN
# ------------------------------
def select_clips(df: pd.DataFrame, prompt_info: dict, n_shots=6):
    df_ranked = rank_clips(df, prompt_info)
    story = select_signature_story(df_ranked)
    return story
