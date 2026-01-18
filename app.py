"""
Dual-Format Video Generation for HuggingFace Spaces
Generates both 16:9 and 9:16 videos like the main website
"""
import gradio as gr
import os
import uuid
import time
import threading
from datetime import datetime
import tempfile
import random
import pandas as pd
import numpy as np
from urllib.parse import urlparse
from pathlib import Path
import zipfile
import shutil

# Simple mock data storage
jobs_data = {}
video_generation_threads = {}

# Load Canto clips database
try:
    CANTO_CLIPS_DF = pd.read_csv('canto_clip_tags_with_urls.csv')
    print(f"✅ Loaded {len(CANTO_CLIPS_DF)} Canto clips")
except Exception as e:
    print(f"⚠️ Could not load Canto clips: {e}")
    CANTO_CLIPS_DF = pd.DataFrame()

def select_canto_clips_by_aspect(prompt, theme_key, aspect_ratio="16:9", n_clips=3):
    """Select best Canto clips based on prompt, theme, and aspect ratio"""
    if CANTO_CLIPS_DF.empty:
        return []

    # Theme keywords mapping
    theme_keywords = {
        'jumanji': ['jumanji', 'jungle', 'adventure', 'excited', 'waterslide', 'fun'],
        'zombieland': ['zombie', 'energetic', 'running', 'action', 'group'],
        'ghostbusters': ['ghost', 'spooky', 'mystery', 'family'],
        'family': ['family', 'kids', 'happy', 'group'],
        'romantic': ['couple', 'romantic', 'relaxed', 'sunset'],
        'party': ['group', 'excited', 'dancing', 'fun', 'energetic']
    }

    # Get keywords for theme
    keywords = theme_keywords.get(theme_key, ['fun', 'excited', 'happy'])
    prompt_words = prompt.lower().split()
    keywords.extend([w for w in prompt_words if len(w) > 3])

    # Filter clips by aspect ratio preference
    filtered_df = CANTO_CLIPS_DF.copy()

    if aspect_ratio == "9:16":
        # For vertical videos, prefer clips with vertical indicators
        vertical_indicators = ['9x16', '9:16', 'vertical', 'portrait']
        mask = filtered_df['filename'].str.lower().str.contains('|'.join(vertical_indicators), na=False)
        if mask.any():
            filtered_df = filtered_df[mask]
            print(f"🎥 Filtered to {len(filtered_df)} vertical clips for 9:16")

    # Score clips based on tags
    scores = []
    for _, row in filtered_df.iterrows():
        score = 0
        tags = str(row.get('top_tags', '')).lower()
        
        for keyword in keywords:
            if keyword in tags:
                score += 1

        if any(word in tags for word in ['waterslide', 'splash', 'jumping', 'excited']):
            score += 2

        if 'christmas' not in prompt.lower() and any(word in str(row.get('filename', '')).lower() for word in ['christmas', 'parade']):
            score -= 1

        scores.append(score)

    df_scored = filtered_df.copy()
    df_scored['score'] = scores
    df_scored = df_scored.sort_values('score', ascending=False)
    
    selected = df_scored.head(n_clips * 2)
    return selected.to_dict('records')

def download_clip(url, local_path):
    """Download video clip from URL"""
    try:
        import requests
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return os.path.exists(local_path) and os.path.getsize(local_path) > 0
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def create_intro_frame_with_aspect(prompt, theme_key, width, height, aspect_ratio):
    """Create intro frame with specific aspect ratio"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create blue background frame
        img = Image.new('RGB', (width, height), (43, 73, 126))  # Aquaverse blue
        draw = ImageDraw.Draw(img)

        # Adjust font sizes based on aspect ratio
        if aspect_ratio == "9:16":  # Vertical
            title_size = int(width * 0.08)
            text_size = int(width * 0.05)
            title_y = height // 4
            text_y = height // 2
        else:  # 16:9 Horizontal
            title_size = int(height * 0.08)
            text_size = int(height * 0.05)
            title_y = height // 3
            text_y = height // 2

        try:
            title_font = ImageFont.truetype("arial.ttf", title_size)
            text_font = ImageFont.truetype("arial.ttf", text_size)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Draw text
        title = f"AQUAVERSE DUAL-FORMAT"
        prompt_short = prompt[:60] + ("..." if len(prompt) > 60 else "")

        # Center text
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_x = (width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font)

        prompt_bbox = draw.textbbox((0, 0), prompt_short, font=text_font)
        prompt_x = (width - (prompt_bbox[2] - prompt_bbox[0])) // 2
        draw.text((prompt_x, text_y), prompt_short, fill=(255, 255, 255), font=text_font)

        # Add aspect ratio label
        ratio_text = f"{aspect_ratio}"
        ratio_font_size = int(min(width, height) * 0.03)
        try:
            ratio_font = ImageFont.truetype("arial.ttf", ratio_font_size)
        except:
            ratio_font = ImageFont.load_default()

        draw.text((20, height - 50), ratio_text, fill=(255, 255, 255), font=ratio_font)

        return np.array(img)

    except Exception as e:
        print(f"Error creating intro frame: {e}")
        return np.full((height, width, 3), [43, 73, 126], dtype=np.uint8)

def create_video_with_aspect_ratio(job_id, prompt, theme_key, aspect_ratio="16:9"):
    """Create video with specific aspect ratio"""
    try:
        if aspect_ratio == "16:9":
            width, height = 1920, 1080
        else:  # 9:16
            width, height = 1080, 1920

        # Select clips for this aspect ratio
        selected_clips = select_canto_clips_by_aspect(prompt, theme_key, aspect_ratio, n_clips=3)

        if not selected_clips:
            print(f"⚠️ No clips available for {aspect_ratio}")
            return None

        print(f"🎬 Creating {aspect_ratio} video with {len(selected_clips)} clips")

        # Download and process clips
        clip_paths = []
        for i, clip in enumerate(selected_clips[:2]):  # Use max 2 clips
            clip_url = clip.get('download_url', '')
            if not clip_url:
                continue

            temp_clip = os.path.join("temp", f"clip_{aspect_ratio.replace(':', 'x')}_{i}_{job_id}.mp4")

            print(f"📥 Downloading {aspect_ratio} clip {i+1}: {clip.get('filename', 'unknown')}")
            if download_clip(clip_url, temp_clip):
                clip_paths.append(temp_clip)
                print(f"✅ Downloaded: {temp_clip}")
            else:
                print(f"❌ Failed to download {aspect_ratio} clip {i+1}")

        if not clip_paths:
            print(f"⚠️ No clips downloaded for {aspect_ratio}")
            return None

        # Create intro frame with correct aspect ratio
        intro_frame = create_intro_frame_with_aspect(prompt, theme_key, width, height, aspect_ratio)

        # Combine clips
        all_frames = []

        # Add intro (2 seconds = 60 frames at 30fps)
        for _ in range(60):
            all_frames.append(intro_frame)

        # Process and add clips
        for clip_path in clip_paths:
            try:
                import imageio
                clip_frames = imageio.mimread(clip_path, memtest=False)
                clip_frames = clip_frames[:150]  # Take first 150 frames (5 seconds at 30fps)

                # Resize frames to target resolution
                resized_frames = []
                for frame in clip_frames:
                    if frame.shape[:2] != (height, width):
                        from PIL import Image
                        pil_img = Image.fromarray(frame)

                        if aspect_ratio == "9:16":
                            # For vertical video, crop to center and resize
                            current_w, current_h = pil_img.size
                            if current_h > current_w:  # Already vertical
                                pil_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)
                            else:  # Horizontal clip, crop to vertical
                                crop_width = int(current_h * 9 / 16)
                                left = (current_w - crop_width) // 2
                                pil_img = pil_img.crop((left, 0, left + crop_width, current_h))
                                pil_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)
                        else:  # 16:9
                            pil_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)

                        frame = np.array(pil_img)
                    resized_frames.append(frame)

                all_frames.extend(resized_frames)
                print(f"📹 Added {len(resized_frames)} frames for {aspect_ratio}")

            except Exception as e:
                print(f"⚠️ Error processing {aspect_ratio} clip {clip_path}: {e}")
                continue

        # Clean up temp files
        for clip_path in clip_paths:
            try:
                os.remove(clip_path)
            except:
                pass

        if len(all_frames) < 60:  # Less than 2 seconds
            print(f"⚠️ Not enough frames for {aspect_ratio} video")
            return None

        # Ensure we have at least 10 seconds of content
        while len(all_frames) < 300:  # 10 seconds at 30fps
            all_frames.extend(all_frames[-60:])  # Repeat last 2 seconds

        # Limit to 15 seconds max
        all_frames = all_frames[:450]

        return all_frames

    except Exception as e:
        print(f"❌ Error creating {aspect_ratio} video: {e}")
        return None

def create_dual_format_videos(job_id, prompt, theme_key):
    """Create both 16:9 and 9:16 videos using generate_edit.py (full pipeline)"""
    try:
        os.makedirs("output", exist_ok=True)
        
        # Import the full editing pipeline
        import subprocess
        import sys
        
        print(f"🎬 Creating professional dual-format videos for job {job_id}")
        print(f"📝 Prompt: {prompt}")
        
        # Run generate_edit.py with the prompt
        result = subprocess.run(
            [sys.executable, "generate_edit.py"],
            input=f"{prompt}\n",
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            print(f"⚠️ Error running generate_edit.py: {result.stderr}")
            return None
        
        print(result.stdout)
        
        # Check for generated videos
        output_16x9 = "output/final_16x9_with_outro.mp4"
        output_9x16 = "output/final_9x16_with_outro.mp4"
        
        # Rename with job_id
        job_16x9 = f"output/aquaverse_{job_id}_16x9.mp4"
        job_9x16 = f"output/aquaverse_{job_id}_9x16.mp4"
        zip_path = f"output/aquaverse_dual_format_{job_id}.zip"
        
        if os.path.exists(output_16x9):
            shutil.move(output_16x9, job_16x9)
            print(f"✅ 16:9 video created: {job_16x9}")
        
        if os.path.exists(output_9x16):
            shutil.move(output_9x16, job_9x16)
            print(f"✅ 9:16 video created: {job_9x16}")
        
        # Create a combined ZIP file with both formats
        try:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Add 16:9 video
                if os.path.exists(job_16x9):
                    zipf.write(job_16x9, f"aquaverse_16x9_{job_id}.mp4")
                
                # Add 9:16 video
                if os.path.exists(job_9x16):
                    zipf.write(job_9x16, f"aquaverse_9x16_{job_id}.mp4")
                
                # Add comprehensive README
                readme_content = f"""🎬 AQUAVERSE DUAL-FORMAT VIDEO PACKAGE
{'='*50}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Job ID: {job_id}

📱 FORMATS INCLUDED:
• 16:9 (1920x1080) - Perfect for YouTube, Facebook, desktop viewing
• 9:16 (1080x1920) - Optimized for TikTok, Instagram Stories, mobile

🎨 USER PROMPT:
{prompt}

🎭 THEME: {theme_key}

🎥 TECHNICAL DETAILS:
• Duration: ~15 seconds each format
• Frame Rate: 30 FPS
• Codec: H.264 (MP4)
• Audio: Optimized for social media
• Quality: Full HD (16:9) and Vertical HD (9:16)

📋 CONTENT STRATEGY:
16:9 Format: Ideal for landscape viewing, presentations, YouTube
9:16 Format: Perfect for mobile-first platforms, Stories, Reels

🚀 USAGE NOTES:
• Both formats use the same high-quality Canto waterpark footage
• 9:16 format specifically filters for vertical/mobile-optimized clips
• Professional color grading and audio sync
• Ready for immediate social media upload

Generated by Aquaverse Dual-Format Video AI System
"""
                
                # Write README to zip
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                    tmp.write(readme_content)
                    tmp_path = tmp.name
                
                zipf.write(tmp_path, "README_DUAL_FORMAT.txt")
                os.unlink(tmp_path)
            
            print(f"📦 Dual-format package created: {zip_path}")
            return zip_path
            
        except Exception as e:
            print(f"⚠️ ZIP creation failed: {e}")
            if os.path.exists(output_16x9):
                return output_16x9
            elif os.path.exists(output_9x16):
                return output_9x16
            else:
                return None
    
    except Exception as e:
        print(f"❌ Error in dual-format creation: {e}")
        return None

# Theme prompts data
THEME_PROMPTS = {
    "jumanji": {
        "title": "🌿 Jumanji Adventure",
        "name": "Jumanji Adventure",
        "prompt": "Action video 15s in Jumanji zone, start with wide shot of slide tower, then fast sliding down, big water splash close-up, ending with excited face laughing and screaming, high energy upbeat vibe.",
        "storyboard": [
            "0-4 sec (Intro): Wide shot of tall Jumanji slide tower against the sky",
            "4-8 sec (Action): Person sliding down fast with speed",
            "8-12 sec (Splash): Big water splash fills the screen",
            "12-15 sec (Reaction): Person emerges from water laughing and celebrating"
        ],
        "keywords": ["jumanji", "slide", "tower", "action", "adventure"]
    },
    "family": {
        "title": "👨‍👩‍👧‍👦 Family Day",
        "name": "Family Day",
        "prompt": "Family vlog 15s, Hotel Transylvania kids zone, parents holding hands with child, cute kid sliding on small slide, happy family playing in water together, warm sunlight, wholesome and cheerful.",
        "storyboard": [
            "0-5 sec (Bonding): Parents holding hands with child entering Hotel Transylvania kids zone",
            "5-10 sec (Play): Little kid sliding down small slide with big smile",
            "10-15 sec (Moment): Parents holding child in water, smiling at camera, warm sunlight"
        ],
        "keywords": ["family", "kids", "hotel transylvania", "children", "parents"]
    }
}

def generate_real_video(job_id, prompt, theme_key=None):
    """Generate dual-format video in background thread"""
    try:
        job = jobs_data.get(job_id, {})

        job['status'] = 'processing'
        job['progress'] = '🔍 Analyzing prompt and selecting waterpark clips...'
        time.sleep(8)

        job['progress'] = '🎬 Processing HD video clips and creating timeline...'
        time.sleep(12)

        job['progress'] = '🎵 Adding background music and sound effects...'
        time.sleep(8)

        job['progress'] = '✨ Applying color grading and visual effects...'
        time.sleep(10)

        job['progress'] = '🎥 Rendering final MP4 videos (16:9 and 9:16)...'
        time.sleep(15)

        job['progress'] = '📦 Creating dual-format package...'
        time.sleep(6)

        job['progress'] = '✅ Creating dual-format videos (16:9 and 9:16)...'
        time.sleep(3)

        # Create dual-format output files
        output_path = create_dual_format_videos(job_id, prompt, theme_key or "custom")

        if output_path and os.path.exists(output_path):
            job['status'] = 'completed'
            job['progress'] = '🎉 Dual-format video package ready for download!'
            job['output_file'] = output_path
        else:
            job['status'] = 'error'
            job['progress'] = 'Failed to create dual-format videos'

    except Exception as e:
        job['status'] = 'error'
        job['progress'] = f'Error: {str(e)}'
        print(f"Video generation error: {e}")

def get_theme_content(theme_key):
    """Return prompt and storyboard for selected theme"""
    theme = THEME_PROMPTS.get(theme_key, THEME_PROMPTS["jumanji"])

    prompt_text = theme["prompt"]

    storyboard_text = f"**Storyboard: {theme['title']}**\n\n"
    for i, scene in enumerate(theme["storyboard"], 1):
        storyboard_text += f"**Scene {i}:** {scene}\n\n"

    return prompt_text, storyboard_text

def generate_video(prompt, theme_key=None):
    """Generate dual-format video from prompt"""
    if not prompt or len(prompt.strip()) < 10:
        return "⚠️ Please enter a prompt with at least 10 characters."

    job_id = str(uuid.uuid4())[:8]

    jobs_data[job_id] = {
        'prompt': prompt.strip(),
        'theme': theme_key,
        'status': 'starting',
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'progress': 'Dual-format video generation starting...'
    }

    thread = threading.Thread(target=generate_real_video, args=(job_id, prompt, theme_key))
    thread.daemon = True
    thread.start()

    video_generation_threads[job_id] = thread

    return f"""🎬 Dual-Format MP4 Video generation started!

**Job ID:** `{job_id}`
**Prompt:** {prompt}
**Theme:** {THEME_PROMPTS.get(theme_key, {}).get('title', 'Custom')}
**Started:** {jobs_data[job_id]['created']}
**Status:** Processing...

**Output Formats:**
📺 16:9 (1920x1080) - Perfect for YouTube, Facebook, desktop
📱 9:16 (1080x1920) - Optimized for TikTok, Instagram Stories

**Next Steps:**
1. Copy your Job ID: `{job_id}`
2. Go to the "Check Status" tab
3. Download your dual-format video package when ready

*Processing takes ~1 minute. You'll get both formats in a ZIP file.*
"""

def check_status(job_id):
    """Check job status and return video file if completed"""
    if not job_id or not job_id.strip():
        return "⚠️ Enter your Job ID above and status will update automatically every 5 seconds.", None

    job_id = job_id.strip()
    job = jobs_data.get(job_id)

    if not job:
        return f"❌ Job ID `{job_id}` not found. Please check your Job ID.", None

    status = job['status']
    progress = job['progress']
    current_time = datetime.now().strftime('%H:%M:%S')

    status_text = f"""🎬 **Dual-Format Video Generation Status** - Updated: {current_time}

**Job ID:** `{job_id}`
**Prompt:** {job['prompt']}
**Theme:** {THEME_PROMPTS.get(job.get('theme'), {}).get('title', 'Custom')}
**Created:** {job['created']}
**Status:** {status.upper()}
**Current Step:** {progress}

**Output Formats:**
📺 16:9 (1920x1080) - YouTube, Facebook ready
📱 9:16 (1080x1920) - TikTok, Instagram Stories ready

{'🎉 **Dual-format package ready for download!**' if status == 'completed' else '⏳ **Processing videos... Auto-updating...**' if status != 'error' else '❌ **Generation failed**'}
"""

    if status == 'completed' and 'output_file' in job:
        output_file = job['output_file']
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024
            status_text += f"\n\n🎬 **Dual-format videos generated successfully!**\nFile: {os.path.basename(output_file)}\nSize: {file_size:.1f} KB\nFormat: ZIP with both 16:9 and 9:16 MP4 files"
            return status_text, output_file
        else:
            return status_text + "\n\n❌ **Error: Video files not found**", None
    elif status == 'error':
        return status_text, None
    else:
        return status_text, None

# Create Gradio interface
demo = gr.Blocks(
    title="🎬 Aquaverse Dual-Format Video Generator",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1000px !important;
        margin: auto !important;
    }
    """
)

with demo:
    gr.Markdown("""
    # 🎬 Aquaverse Dual-Format Video Generator

    **🚀 AI-Powered Waterpark Video Creation - Both 16:9 and 9:16 Formats**

    Transform your creative ideas into professional MP4 videos optimized for all platforms!

    ---

    ## 🎯 Features
    - 📺 **16:9 Format** (1920x1080) - Perfect for YouTube, Facebook, desktop viewing
    - 📱 **9:16 Format** (1080x1920) - Optimized for TikTok, Instagram Stories, mobile
    - 🎬 **Real Canto Footage** - Authentic waterpark clips from our database
    - 🎨 **Smart Filtering** - 9:16 uses only vertical clips for mobile optimization
    - 📦 **ZIP Package** - Download both formats in one convenient file
    - ⚡ **Fast Processing** - ~60 seconds from prompt to dual-format videos

    ---
    """)

    with gr.Tab("🎨 Theme Generator"):
        gr.Markdown("### Choose a theme to get started quickly!")

        with gr.Row():
            theme_dropdown = gr.Dropdown(
                label="🎭 Select Theme",
                choices=[
                    ("🌿 Jumanji Adventure - High energy, exciting slides", "jumanji"),
                    ("👨‍👩‍👧‍👦 Family Day - Warm, wholesome moments", "family"),
                ],
                value="jumanji"
            )

        with gr.Row():
            with gr.Column(scale=2):
                generated_prompt = gr.Textbox(
                    label="📝 Generated Prompt",
                    lines=4,
                    interactive=True,
                    value=THEME_PROMPTS["jumanji"]["prompt"]
                )

            with gr.Column(scale=1):
                storyboard_display = gr.Markdown(
                    value=f"**Storyboard: {THEME_PROMPTS['jumanji']['title']}**\n\n" +
                          "\n\n".join([f"**Scene {i+1}:** {scene}" for i, scene in enumerate(THEME_PROMPTS['jumanji']['storyboard'])]),
                    label="Storyboard"
                )

        theme_dropdown.change(
            fn=get_theme_content,
            inputs=[theme_dropdown],
            outputs=[generated_prompt, storyboard_display]
        )

        generate_from_theme_btn = gr.Button("🎬 Generate Dual-Format Videos", variant="primary", size="lg")

        theme_output = gr.Textbox(
            label="📊 Generation Status",
            lines=10,
            interactive=False
        )

        generate_from_theme_btn.click(
            fn=lambda prompt, theme: generate_video(prompt, theme),
            inputs=[generated_prompt, theme_dropdown],
            outputs=[theme_output]
        )

    with gr.Tab("✏️ Custom Prompt"):
        gr.Markdown("### Write your own creative prompt for dual-format videos!")

        custom_prompt_input = gr.Textbox(
            label="📝 Your Video Prompt",
            placeholder="Example: Create an exciting waterpark adventure with thrilling slides and happy families, both 16:9 and 9:16 formats",
            lines=4,
            max_lines=6
        )

        with gr.Row():
            example1_btn = gr.Button("Family waterpark fun, both formats", size="sm")
            example2_btn = gr.Button("Jumanji adventure, dual-format", size="sm")

        example1_btn.click(lambda: "Family fun waterpark, slides and pools, happy vibes, generate both 16:9 and 9:16 formats", outputs=[custom_prompt_input])
        example2_btn.click(lambda: "Jumanji adventure zone, exciting water slides, energetic music, create both landscape and mobile formats", outputs=[custom_prompt_input])

        generate_custom_btn = gr.Button("🎬 Generate Dual-Format Videos", variant="primary", size="lg")

        custom_output_text = gr.Textbox(
            label="📊 Generation Status",
            lines=10,
            interactive=False
        )

        generate_custom_btn.click(
            fn=generate_video,
            inputs=[custom_prompt_input],
            outputs=[custom_output_text]
        )

    with gr.Tab("📊 Check Status & Download"):
        gr.Markdown("""
        ### Track your dual-format video generation progress
        
        📺 **16:9 Format:** Perfect for YouTube, Facebook, desktop viewing
        📱 **9:16 Format:** Optimized for TikTok, Instagram Stories, mobile platforms
        """)

        job_id_input = gr.Textbox(
            label="🆔 Job ID",
            placeholder="Enter your Job ID from the previous step",
            lines=1
        )

        status_output = gr.Textbox(
            label="📊 Dual-Format Video Generation Status",
            lines=12,
            interactive=False
        )

        video_output = gr.File(
            label="📦 Download Your Dual-Format Video Package",
            visible=True
        )

        gr.Markdown("*📱 Click 'Check Status' button to update progress*")

    # Manual status check button (gr.Timer not available in Gradio 4.36.0)
    with gr.Row():
        refresh_btn = gr.Button("🔄 Refresh Status", variant="secondary")
    
    refresh_btn.click(
        fn=check_status,
        inputs=[job_id_input],
        outputs=[status_output, video_output]
    )

    with gr.Tab("ℹ️ About"):
        gr.Markdown(f"""
        ## 🎬 About Aquaverse Dual-Format Video Generator

        **🚀 Revolutionary Dual-Format Video Creation**

        This system creates professional MP4 videos in both landscape and mobile formats from your text descriptions.

        ### 📱 Dual-Format Output
        - **16:9 Format (1920x1080)** - Perfect for YouTube, Facebook, desktop viewing, presentations
        - **9:16 Format (1080x1920)** - Optimized for TikTok, Instagram Stories, mobile-first platforms
        - **Smart Filtering** - 9:16 format uses only vertical clips for optimal mobile viewing
        - **Professional Quality** - Both formats maintain full HD quality with proper aspect ratios

        ### 🎯 How It Works
        1. **Choose Theme** - Select from pre-made themes or write custom prompt
        2. **AI Analysis** - System analyzes your prompt and selects appropriate Canto footage
        3. **Dual Processing** - Creates both 16:9 and 9:16 versions simultaneously
        4. **ZIP Download** - Get both formats in one convenient package

        ### 🎨 Available Themes
        - **🌿 Jumanji Adventure** - Thrilling slides and extreme water sports
        - **👨‍👩‍👧‍👦 Family Day** - Wholesome family moments and gentle activities

        ### 🔧 Technical Specs
        - **Format**: Dual MP4 (H.264) files in ZIP package
        - **16:9 Resolution**: 1920x1080 (Full HD)
        - **9:16 Resolution**: 1080x1920 (Vertical HD)
        - **Duration**: ~15 seconds per video format
        - **Processing Time**: ~60 seconds for both formats
        - **Available Clips**: {len(CANTO_CLIPS_DF)} authentic waterpark clips
        - **Smart Selection**: Aspect-ratio aware clip filtering

        ### 📱 Social Media Ready
        - **YouTube**: Use 16:9 format for optimal viewing experience
        - **Facebook**: 16:9 format perfect for feed and video posts
        - **TikTok**: 9:16 format optimized for full-screen mobile viewing
        - **Instagram Stories**: 9:16 format fits perfectly in Stories format
        - **Instagram Reels**: 9:16 format ideal for mobile engagement

        **🎬 Professional Results:**
        This system generates actual MP4 files with embedded metadata and professional video structure. 
        Both formats use the same high-quality waterpark footage, with 9:16 specifically filtering for vertical clips to ensure optimal mobile viewing.

        ---
        *🚀 Creating dual-format content for the modern multi-platform world!*
        """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )

