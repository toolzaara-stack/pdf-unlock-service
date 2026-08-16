import os
import shutil
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor, as_completed
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

# توليد أو جلب قائمة بأشهر كلمات السر والرموز الشائعة (أكثر من 10,000 احتمال تشمل الأرقام، التواريخ، والكلمات الشائعة)
def generate_common_passwords(filename: str):
    passwords = ["", "123456", "1234", "0000", "password", "123456789", "admin", "12345", "1111", "123123", "12345678", "qwerty", "abc12345"]
    
    # إضافة اسم الملف بدون اللاحقة كاحتمال وارد
    base_name = filename.split('.')[0]
    passwords.append(base_name)
    passwords.append(base_name.lower())
    passwords.append(base_name.upper())

    # إضافة الأرقام المكونة من 4 أرقام (من 0000 إلى 9999)
    for i in range(10000):
        passwords.append(f"{i:04d}")

    # إضافة السنوات الشائعة من 1970 إلى 2030
    for year in range(1970, 2031):
        passwords.append(str(year))
        passwords.append(f"123{year}")
        passwords.append(f"admin{year}")

    return passwords

def try_unlock(doc, pwd):
    try:
        if doc.authenticate(pwd):
            return True
    except Exception:
        pass
    return False

@app.post("/api/unlock-pdf")
async def unlock_pdf(file: UploadFile = File(...), password: str = Form(None)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(UPLOAD_DIR, "unlocked_" + file.filename)

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc = fitz.open(input_path)

        if doc.needs_pass:
            success = False
            
            # 1. التجربة اليدوية أو الخاوية أولاً
            if password and doc.authenticate(password):
                success = True
            elif doc.authenticate(""):
                success = True
            else:
                # 2. جلب القائمة الضخمة وتجربتها بسرعة فائقة عبر الخلفية (Multi-threading)
                passwords_list = generate_common_passwords(file.filename)
                
                # استخدام خيوط متعددة للبحث السريع جداً
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = {executor.submit(try_unlock, doc, pwd): pwd for pwd in passwords_list}
                    for future in as_completed(futures):
                        if future.result():
                            success = True
                            # إلغاء المهام المتبقية بمجرد نجاح فك القفل
                            executor.shutdown(wait=False, cancel_futures=True)
                            break

            if not success:
                doc.close()
                raise HTTPException(
                    status_code=401, 
                    detail="الملف محمي بكلمة مرور معقدة جداً. يرجى إدخال كلمة المرور الصحيحة يدوياً."
                )

        # حفظ الملف بعد تفريغه بالكامل من القيود والكلمات السرية
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
        if os.path.exists(input_path):
            os.remove(input_path)
