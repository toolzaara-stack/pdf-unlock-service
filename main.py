import os
import shutil
import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="ToolZaara PDF Unlock Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp/pdf_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/unlock-pdf")
async def unlock_pdf(file: UploadFile = File(...), password: str = Form(None)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(UPLOAD_DIR, "unlocked_" + file.filename)

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # فتح الملف باستخدام PyMuPDF
        doc = fitz.open(input_path)

        # إذا كان الملف مشفراً ويحتاج لكلمة مرور
        if doc.needs_pass:
            success = False
            # 1. إذا أدخل المستخدم كلمة مرور يدوياً
            if password and doc.authenticate(password):
                success = True
            else:
                # 2. محاولة فتح الملف بدون كلمة مرور (إذا كان قفل صلاحيات فقط)
                if doc.authenticate(""):
                    success = True
                else:
                    # 3. قائمة كلمات مرور شائعة تجربها الأداة تلقائياً (مثل المواقع العالمية)
                    common_passwords = ["", "123456", "1234", "0000", "password", "123456789", "admin", file.filename.split('.')[0]]
                    for pwd in common_passwords:
                        if doc.authenticate(pwd):
                            success = True
                            break
            
            if not success:
                doc.close()
                raise HTTPException(
                    status_code=401, 
                    detail="الملف محمي بكلمة مرور قوية تعذّر تخمينها. يرجى إدخال كلمة المرور الصحيحة."
                )

        # حفظ الملف بدون أي قيود أو كلمات مرور
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()

        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename="unlocked_" + file.filename
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # تنظيف الملفات المؤقتة
        if os.path.exists(input_path):
            os.remove(input_path)
