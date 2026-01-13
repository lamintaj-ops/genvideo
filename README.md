# 🎬 Aquaverse Video Generator

AI-powered automatic video editing system for waterpark content. Generate professional video edits from simple text prompts.

![Python](https://img.shields.io/badge/python-3.11-blue)
![Flask](https://img.shields.io/badge/flask-3.1.2-green)
![FFmpeg](https://img.shields.io/badge/ffmpeg-8.0-red)

## ✨ Features

- **AI Prompt-Based Editing**: Generate videos from natural language descriptions
- **Theme Presets**: Jumanji Adventure, Family Day, Surf & Party, Chill Lifestyle, Ghostbusters, Zombieland
- **Smart Clip Selection**: Zone-aware selection from Canto DAM library
- **Multi-Format Export**: 16:9 (YouTube/Feed) and 9:16 (Stories/TikTok)
- **Video Preview**: Preview before download
- **Automatic Color Grading**: LUT-based color correction
- **Background Music**: Auto-mixed BGM
- **Modern Hard Cuts**: No old-fashioned fades

## 🚀 Quick Start

### Local Development

1. **Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/videoscore.git
   cd videoscore
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

5. **Run Server**
   ```bash
   python web_app.py
   ```

6. **Open Browser**
   ```
   http://localhost:5000
   ```

## 📦 Deployment

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

### Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

1. Click button above
2. Connect your GitHub account
3. Deploy automatically
4. Get your live URL!

## 🎯 How It Works

1. **Prompt Input**: User enters description (e.g., "Jumanji adventure 15s, high energy")
2. **Keyword Analysis**: Extract themes, vibes, zones from prompt
3. **Smart Selection**: AI selects best clips from library based on:
   - Prompt keywords match
   - Zone/folder match (bonus points)
   - Motion score
   - Diversity (avoid repetition)
4. **Video Processing**:
   - Download clips from Canto DAM
   - Cut random segments (2-3s each)
   - Concatenate with hard cuts
   - Apply color grading (LUT)
   - Mix background music
   - Add branded outro
5. **Export**: Generate both 16:9 and 9:16 versions

## 📁 Project Structure

```
videoscore/
├── web_app.py              # Flask web server
├── generate_edit.py        # Main video generation pipeline
├── clip_selector.py        # Smart clip selection algorithm
├── ffmpeg_utils.py         # FFmpeg wrapper functions
├── prompt_rules.py         # Keyword parsing and mapping
├── downloader.py           # Canto DAM downloader
├── templates/
│   └── index.html          # Web UI
├── assets/
│   └── brand_logo.png      # Outro logo
├── bgm/                    # Background music library
├── lut/                    # Color grading LUTs
└── output/                 # Generated videos

```

## ⚙️ Configuration

### Environment Variables

```bash
PORT=5000                   # Server port (auto-detected on Railway/Render)
DEBUG=false                 # Debug mode (true/false)
```

### Customization

- **BGM**: Add MP3 files to `bgm/` folder
- **LUT**: Replace `lut/aquaverse_fun.cube`
- **Logo**: Replace `assets/brand_logo.png`
- **Themes**: Edit `prompt_rules.py` KEYWORDS
- **Clip Library**: Update `canto_clip_tags_with_urls.csv`

## 🎨 Example Prompts

```
Action video 15s in Jumanji zone, wide shot of slide tower, fast sliding, big splash, excited reactions

Family vlog 15s, Hotel Transylvania kids zone, parents with child, wholesome moments

Cool Flowrider surfing 15s, pro tricks, crowd cheering, slow motion water spray

Zombieland horror zone 15s, dark entrance, thrilling slides, intense landing, scary fun
```

## 📊 Technology Stack

- **Backend**: Python 3.11, Flask 3.1
- **Video Processing**: FFmpeg 8.0
- **Data Processing**: Pandas 2.1
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **DAM Integration**: Canto API

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Credits

- Video Library: Canto DAM
- Color Grading: Custom LUTs
- Music: Royalty-free BGM library

---

Made with ❤️ for Aquaverse Waterpark
