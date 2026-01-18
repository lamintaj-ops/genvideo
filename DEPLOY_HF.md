# 🚀 Deploy บน Hugging Face Spaces

คู่มือการ deploy Aquaverse Video Generator บน Hugging Face Spaces

## ⚠️ สำคัญ: อย่า Copy ไฟล์ในโฟลเดอร์เดียวกัน
ปัญหาที่เจอคือการ copy ไฟล์ในโฟลเดอร์เดียวกัน ให้ทำตามขั้นตอนนี้แทน

## เตรียมการก่อน Deploy

### 1. สร้าง Hugging Face Account
- สมัครที่ https://huggingface.co/
- ยืนยัน email address

### 2. ติดตั้ง Dependencies
```bash
pip install huggingface_hub
```

### 3. Login Hugging Face CLI
```bash
huggingface-cli login
```
ใส่ token ของคุณ (สร้างได้ที่ https://huggingface.co/settings/tokens)

## วิธี Deploy (วิธีที่ถูกต้อง)

### ขั้นตอนที่ 1: สร้าง Space ใหม่
1. ไปที่ https://huggingface.co/new-space
2. ใส่ชื่อ Space เช่น `aquaverse-video-generator`
3. เลือก SDK: **Gradio**
4. เลือก Hardware: **CPU basic** (หรือ GPU ถ้าต้องการ)
5. กดสร้าง

### ขั้นตอนที่ 2: Clone และ Setup
```bash
# Clone your space to a NEW directory (NOT in your project folder)
cd C:\
git clone https://huggingface.co/spaces/YOUR_USERNAME/aquaverse-video-generator
cd aquaverse-video-generator

# Copy files from your project (run from the Space directory)
python C:\spai\videoscore\deploy_hf.py
```

**หรือ Copy ด้วยมือ (แนะนำ):**
```powershell
# สร้างโฟลเดอร์ใหม่สำหรับ Space
cd C:\
git clone https://huggingface.co/spaces/YOUR_USERNAME/aquaverse-video-generator
cd aquaverse-video-generator

# Copy เฉพาะไฟล์ที่จำเป็น (ไม่รวม .venv)
Copy-Item -Path "C:\spai\videoscore\*.py" -Destination "." 
Copy-Item -Path "C:\spai\videoscore\requirements.txt" -Destination "."
Copy-Item -Path "C:\spai\videoscore\templates" -Destination "." -Recurse
Copy-Item -Path "C:\spai\videoscore\static" -Destination "." -Recurse
Copy-Item -Path "C:\spai\videoscore\*.csv" -Destination "." 
Copy-Item -Path "C:\spai\videoscore\*.md" -Destination "."
Copy-Item -Path "C:\spai\videoscore\Dockerfile" -Destination "." -ErrorAction SilentlyContinue
```

### ขั้นตอนที่ 3: Deploy
**วิธีที่ 1: ใช้ Script อัตโนมัติ (แนะนำ)**
```cmd
# จากโฟลเดอร์ project ปัจจุบัน (C:\spai\videoscore)
copy_to_space.bat "C:\HF_Spaces\aquaverse-video-generator"

# แล้วไปที่โฟลเดอร์ Space
cd "C:\HF_Spaces\aquaverse-video-generator"
git add .
git commit -m "Deploy Aquaverse Video Generator"
git push origin main
```

**วิธีที่ 2: Manual Copy**
```powershell
# Copy เฉพาะไฟล์ที่จำเป็น
cd "C:\HF_Spaces\aquaverse-video-generator"

# Copy ไฟล์หลัก
Copy-Item -Path "C:\spai\videoscore\*.py" -Destination "."
Copy-Item -Path "C:\spai\videoscore\requirements.txt" -Destination "."
Copy-Item -Path "C:\spai\videoscore\*.md" -Destination "."

# Copy โฟลเดอร์ที่จำเป็น
Copy-Item -Path "C:\spai\videoscore\templates" -Destination "." -Recurse
Copy-Item -Path "C:\spai\videoscore\static" -Destination "." -Recurse
Copy-Item -Path "C:\spai\videoscore\assets" -Destination "." -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "C:\spai\videoscore\bgm" -Destination "." -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "C:\spai\videoscore\sfx" -Destination "." -Recurse -ErrorAction SilentlyContinue

# Deploy
git add .
git commit -m "Deploy Aquaverse Video Generator"  
git push origin main
```

## โครงสร้างไฟล์ที่จำเป็น

### ไฟล์หลักที่สร้างแล้ว:
- ✅ `app.py` - Entry point สำหรับ Hugging Face
- ✅ `requirements.txt` - Dependencies ที่อัปเดตแล้ว
- ✅ `README.md` - อัปเดตด้วย metadata ของ Hugging Face
- ✅ `Dockerfile` - สำหรับ custom deployment
- ✅ `.gitignore` - ไฟล์ที่ไม่ต้อง commit

### ไฟล์ที่มีอยู่แล้ว:
- `web_app.py` - Flask application
- `templates/` - HTML templates
- `static/` - Static files
- `generate_edit.py` - Video generation logic

## การตั้งค่า Environment Variables (ถ้าจำเป็น)

ในหน้า Settings ของ Space:
```
DEBUG=false
FLASK_ENV=production
```

## การตรวจสอบ Log

หลัง deploy สามารถดู log ได้ที่:
- ไปยัง Space URL
- กด "Logs" tab เพื่อดูสถานะการ build

## ปัญหาที่อาจเจอ

### 1. Space ไม่ start
- ตรวจสอบ logs
- ตรวจสอบ requirements.txt
- ตรวจสอบ port 7860

### 2. FFmpeg ไม่ทำงาน
- ใช้ Dockerfile แทน Gradio SDK
- หรือเปลี่ยนไปใช้ alternative video processing

### 3. Memory issues
- อัพเกรด hardware เป็น GPU
- ลดขนาดไฟล์ที่ process

## การอัปเดต Space

เมื่อต้องการอัปเดต:
```bash
git add .
git commit -m "Update: describe your changes"
git push origin main
```

Space จะ rebuild อัตโนมัติ

## URL ของ Space

หลัง deploy เสร็จ Space จะใช้งานได้ที่:
```
https://huggingface.co/spaces/YOUR_USERNAME/aquaverse-video-generator
```

## Troubleshooting

### ถ้า build ล้มเหลว:
1. ตรวจสอบ requirements.txt
2. ตรวจสอบ import ใน app.py
3. ดู logs ใน Space

### ถ้า app ไม่ทำงาน:
1. ตรวจสอบ port 7860
2. ตรวจสอบ file permissions
3. ตรวจสอบ environment variables

สำหรับความช่วยเหลือเพิ่มเติม ดูได้ที่:
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Gradio Documentation](https://gradio.app/docs/)