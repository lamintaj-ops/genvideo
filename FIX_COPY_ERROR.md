## ❌ แก้ไขปัญหา Copy-Item Error

ปัญหาที่คุณเจอ: `Cannot overwrite the item with itself`

### สาเหตุ:
คุณพยายาม copy ไฟล์ในโฟลเดอร์เดียวกัน (C:\spai\videoscore) ทำให้เกิด error

### วิธีแก้ไข:
**อย่าทำ:** 
```powershell
# ❌ ผิด - copy ในโฟลเดอร์เดียวกัน
Copy-Item -Path "C:\spai\videoscore\*" -Destination "." -Recurse
```

**ทำแบบนี้แทน:**
```powershell
# ✅ ถูก - สร้างโฟลเดอร์ใหม่สำหรับ Hugging Face Space
cd C:\
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# แล้ว copy จาก source ไปยัง destination ที่แตกต่างกัน
Copy-Item -Path "C:\spai\videoscore\*.py" -Destination "."
Copy-Item -Path "C:\spai\videoscore\templates" -Destination "." -Recurse
```

### ใช้ Script ที่เตรียมไว้:
```cmd
copy_to_space.bat "C:\path\to\your\huggingface\space"
```

### ไฟล์ที่ไม่ต้อง Copy:
- `.venv/` - Virtual environment (จะสร้างใหม่บน HF)
- `__pycache__/` - Python cache
- `temp/`, `output/` - Temporary files
- `.git/` - Git history (จะมีของ HF Space แล้ว)

### ขั้นตอนที่ถูกต้อง:
1. สร้าง HF Space ที่ huggingface.co
2. Clone Space มาในโฟลเดอร์ใหม่
3. Copy ไฟล์จาก project ไปยัง Space directory
4. Push ขึ้น HF

ปัญหาจะหมดไปครับ! 🎉