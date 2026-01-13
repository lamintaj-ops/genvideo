# ขั้นตอนการ Push ขึ้น GitHub

## 1. สร้าง Repository บน GitHub
- ไปที่ https://github.com/new
- ตั้งชื่อ repository เช่น `aquaverse-video-generator`
- เลือก Public หรือ Private
- **อย่าสร้าง** README, .gitignore, license (เรามีแล้ว)
- คลิก "Create repository"

## 2. รัน Commands เหล่านี้ใน Terminal

```powershell
# 1. Initialize git repository
git init

# 2. Add all files
git add .

# 3. Create first commit
git commit -m "Initial commit: Aquaverse Video Generator"

# 4. Rename branch to main
git branch -M main

# 5. Add GitHub remote (แทน YOUR_USERNAME และ YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 6. Push to GitHub
git push -u origin main
```

## 3. ตัวอย่างคำสั่งจริง
```powershell
# สมมติ username = johndoe และ repo = aquaverse-video-gen
git remote add origin https://github.com/johndoe/aquaverse-video-gen.git
git push -u origin main
```

## 4. Enter GitHub Credentials
- กรอก username
- สำหรับ password: ใช้ **Personal Access Token** แทน (ไม่ใช่รหัสผ่านปกติ)
  - ไปที่ https://github.com/settings/tokens
  - Generate new token (classic)
  - เลือก scope: `repo`
  - Copy token มาใช้แทนรหัสผ่าน

## 5. ตรวจสอบผลลัพธ์
- ไปที่ `https://github.com/YOUR_USERNAME/YOUR_REPO`
- จะเห็นไฟล์ทั้งหมดอยู่บน GitHub แล้ว

## 6. Deploy (เลือกวิธีใดวิธีหนึ่ง)

### วิธี A: Railway (แนะนำ)
1. ไปที่ https://railway.app
2. Sign in with GitHub
3. New Project → Deploy from GitHub repo
4. เลือก repository ที่สร้างไว้
5. Deploy!
6. จะได้ URL เช่น `https://your-app.railway.app`

### วิธี B: Render
1. ไปที่ https://render.com
2. New + → Web Service
3. Connect repository
4. ตั้งค่า:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python web_app.py`
5. Create Web Service
6. จะได้ URL เช่น `https://your-app.onrender.com`

## 7. แก้ไขโค้ดในอนาคต
```powershell
# 1. แก้ไขไฟล์
# 2. Add changes
git add .

# 3. Commit
git commit -m "Update: อธิบายสิ่งที่แก้ไข"

# 4. Push
git push

# Railway/Render จะ auto-deploy ให้อัตโนมัติ!
```

## ⚠️ หมายเหตุ
- ไฟล์วิดีโอขนาดใหญ่ใน `output/` และ `temp/` จะไม่ถูก push (อยู่ใน .gitignore)
- CSV ไฟล์ถ้าใหญ่เกิน 100MB ให้ใช้ Git LFS
- สำหรับ production ให้ตั้ง `DEBUG=false` ใน environment variables
