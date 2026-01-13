# Deploy to Railway

## Prereqs
- Push this repo to GitHub
- Create a Railway account

## Deploy (GitHub)
1. Railway Dashboard → `New Project` → `Deploy from GitHub repo`
2. Select your repo and deploy
3. Service → `Settings` → `Domains` → open the generated URL

## Config used by this repo
- System deps: `Aptfile` contains `ffmpeg` (Nixpacks installs it)
- Python deps: `requirements.txt`
- Start command: `railway.json` / `Procfile`
  - `gunicorn -w 1 -k gthread -t 0 -b 0.0.0.0:$PORT web_app:app`

## Railway variables (optional)
- `DEBUG=false`
- `VIDEOSCORE_NO_NVENC=1` (disable NVENC if GPU/driver issues)

## Notes
- `output/` is ephemeral on Railway; for persistent storage, upload results to object storage (S3/R2).
