import subprocess
from pathlib import Path

def run(cmd):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

music_path = Path("bgm")
files = list(music_path.glob("*.mp3"))
print("Found bgm:", files)

if not files:
    print("NO MP3 FOUND IN /bgm FOLDER")
    exit()

music = files[0]
out = Path("test_trim.mp3")

cmd = [
    "ffmpeg", "-y",
    "-i", str(music),
    "-t", "5",
    "-af", "afade=t=in:ss=0:d=0.5,afade=t=out:st=4.5:d=0.5",
    str(out)
]

run(cmd)
print("Done. Check test_trim.mp3")
