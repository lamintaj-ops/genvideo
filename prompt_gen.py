import random
import argparse

# ----------------------------------------------
# PRESETS
# ----------------------------------------------

MOODS = {
    "fun": "สนุกสดใส",
    "bright": "bright fun",
    "warm": "โทนอบอุ่น",
    "cinematic": "cinematic adventure",
    "upbeat": "upbeat"
}

SUBJECTS = {
    "family": ["family fun", "smile moment", "group fun"],
    "teens": ["teen excitement", "ride action", "fast splash"],
    "kids": ["kids fun", "cute moment", "water playground"],
    "mixed": ["fun adventure", "splash", "water blast"]
}

ZONES = {
    "jumanji": "โซน Jumanji",
    "aquaverse": "Aquaverse",
    "slides": "โซนสไลเดอร์",
    "playground": "โซน water playground"
}

STYLES = {
    "tvc": "แบบโฆษณา TVC",
    "reel": "เหมือน IG Reel จังหวะเร็ว",
    "promo": "แบบโปรโมทสวนสนุก"
}

INTENSITIES = [
    "เน้น splash", "motion สูง", "สดใสสุดๆ", "สนุกตลอดคลิป", "เน้น slide"
]

STRUCTURES = [
    "มี HOOK ช่วงเปิด", 
    "ตัดต่อเร็วตอนต้นและจบด้วย wide shot",
    "บรรยากาศสนุกตั้งแต่ต้นจนจบ"
]

# ----------------------------------------------
# GENERATION LOGIC
# ----------------------------------------------

def generate_prompt(duration=None, mood=None, subject=None, zone=None, style=None):
    
    # Auto-random fallback
    if duration is None:
        duration = random.choice([12, 15, 18])

    if mood is None:
        mood = random.choice(list(MOODS.values()))
    else:
        mood = MOODS.get(mood.lower(), random.choice(list(MOODS.values())))

    if subject is None:
        theme = random.choice(sum(SUBJECTS.values(), []))
    else:
        theme = random.choice(SUBJECTS.get(subject.lower(), SUBJECTS["mixed"]))

    if zone is None:
        zone = random.choice(list(ZONES.values()))
    else:
        zone = ZONES.get(zone.lower(), random.choice(list(ZONES.values())))

    if style is None:
        style_text = random.choice(list(STYLES.values()))
    else:
        style_text = STYLES.get(style.lower(), random.choice(list(STYLES.values())))

    intense = random.choice(INTENSITIES)
    struct = random.choice(STRUCTURES)

    # Final prompt
    prompt = (
        f"ทำคลิป {duration} วินาที โทน{mood} {theme} "
        f"ใน {zone} {intense} {struct} {style_text}"
    )
    return prompt


# ----------------------------------------------
# CLI
# ----------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aquaverse Prompt Generator")

    parser.add_argument("--duration", type=int, help="ระยะเวลา เช่น 15")
    parser.add_argument("--mood", type=str, help="fun | bright | warm | cinematic | upbeat")
    parser.add_argument("--subject", type=str, help="family | teens | kids | mixed")
    parser.add_argument("--zone", type=str, help="jumanji | aquaverse | slides | playground")
    parser.add_argument("--style", type=str, help="tvc | reel | promo")

    args = parser.parse_args()

    result = generate_prompt(
        duration=args.duration,
        mood=args.mood,
        subject=args.subject,
        zone=args.zone,
        style=args.style
    )

    print("\n🎬 Prompt ที่สร้างขึ้น:")
    print(result)
    print()
