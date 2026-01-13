# 🚀 Deploy Aquaverse Video Generator

## วิธีที่ 1: Deploy บน Railway (แนะนำ - ฟรี)

### ขั้นตอน:

1. **สร้าง GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy บน Railway**
   - ไปที่ https://railway.app
   - Sign up ด้วย GitHub account
   - คลิก "New Project" → "Deploy from GitHub repo"
   - เลือก repository ที่สร้างไว้
   - Railway จะ auto-detect และ deploy ให้อัตโนมัติ

3. **ตั้งค่า Environment Variables (ถ้าจำเป็น)**
   - ใน Railway dashboard → Settings → Variables
   - เพิ่มตัวแปรที่ต้องการ (เช่น API keys)

4. **เปิดใช้งาน**
   - Railway จะให้ URL เช่น `https://your-app.railway.app`
   - เข้าใช้งานได้ทันที!

---

## วิธีที่ 2: Deploy บน Render (ฟรี)

1. **Push โค้ดขึ้น GitHub** (ตามข้างบน)

2. **Deploy บน Render**
   - ไปที่ https://render.com
   - Sign up ด้วย GitHub
   - คลิก "New +" → "Web Service"
   - เลือก repository
   - ตั้งค่า:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python web_app.py`
     - **Environment**: Python 3

3. **Deploy**
   - คลิก "Create Web Service"
   - รอสักครู่จะได้ URL เช่น `https://your-app.onrender.com`

---

## วิธีที่ 3: Deploy บน Heroku (เสียค่าใช้จ่าย)

1. **Push โค้ดขึ้น GitHub**

2. **ติดตั้ง Heroku CLI**
   ```bash
   # Windows
   winget install Heroku.HerokuCLI
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   heroku open
   ```

---

## ⚠️ สิ่งที่ต้องระวัง

### 1. **ไฟล์ขนาดใหญ่**
- ไฟล์ video/audio ใน `output/`, `temp/` จะถูก ignore (.gitignore)
- ถ้ามี BGM/assets ที่ใหญ่ ใช้ Git LFS:
  ```bash
  git lfs install
  git lfs track "*.mp3"
  git lfs track "*.mp4"
  ```

### 2. **FFmpeg**
Railway/Render/Heroku ต้องติดตั้ง FFmpeg:
- เพิ่มไฟล์ `aptfile` หรือ `Aptfile`:
  ```
  ffmpeg
  ```

### 3. **CSV Data Files**
- ตรวจสอบว่า `canto_clip_tags_with_urls.csv` ไม่ใหญ่เกินไป
- ถ้าใหญ่ ให้ใช้ database แทน (PostgreSQL)

### 4. **Port Configuration**
ตรวจสอบว่า `web_app.py` รับ PORT จาก environment:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

---

## 🔧 Troubleshooting

### ปัญหา: "Application Error"
- ตรวจสอบ logs: `heroku logs --tail` หรือดูใน Railway/Render dashboard
- ตรวจสอบว่าติดตั้ง dependencies ครบ

### ปัญหา: "FFmpeg not found"
- เพิ่ม buildpack หรือ aptfile ตามข้างบน

### ปัญหา: "File not found" (CSV, assets)
- ตรวจสอบว่าไฟล์อยู่ใน repository และไม่อยู่ใน .gitignore

---

## 📊 Free Tier Limits

| Platform | RAM | Storage | Build Time | Sleep |
|----------|-----|---------|------------|-------|
| Railway  | 512MB | 1GB | ไม่จำกัด | ไม่ sleep |
| Render   | 512MB | - | 15 นาที | sleep หลัง 15 นาทีไม่ใช้งาน |
| Heroku   | 512MB | - | - | เสียเงิน (ยกเลิก free tier) |

**คำแนะนำ:** ใช้ Railway สำหรับ production, Render สำหรับ testing
