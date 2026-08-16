import io
import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pikepdf
import fitz  # PyMuPDF

app = FastAPI(
    title="ToolZaara PDF Unlock & Repair Microservice",
    description="Production-ready microservice to decrypt, unlock, and repair PDF files using QPDF (pikepdf) and PyMuPDF.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Supports all origins including toolzaara.online and mail.toolzaara.online
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "ToolZaara PDF Unlock & Repair Service",
        "engines": ["pikepdf (QPDF)", "PyMuPDF (fitz)"]
    }

@app.post("/api/unlock-pdf")
async def unlock_pdf(
    file: UploadFile = File(...),
    password: str = Form(default="")
):
    """
    Receives an encrypted or permission-restricted PDF,
    removes restrictions and repairs XRef tables, and returns clean PDF bytes.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")

    output_stream = io.BytesIO()

    # --- Engine 1: pikepdf (QPDF engine - industry standard for decrypting and repairing PDFs) ---
    try:
        pdf_input = io.BytesIO(file_bytes)
        with pikepdf.open(pdf_input, password=password) as pdf:
            # Linearize=False ensures complete recreation of xref tables
            pdf.save(output_stream, linearize=False)
            
        output_stream.seek(0)
        clean_filename = f"unlocked_{file.filename}"
        return StreamingResponse(
            output_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{clean_filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except pikepdf.PasswordError:
        raise HTTPException(
            status_code=401, 
            detail="Password required or incorrect password provided."
        )
    except Exception as e_pikepdf:
        # --- Engine 2: PyMuPDF (fitz) Fallback for non-standard structures ---
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            if doc.is_encrypted:
                if not doc.authenticate(password):
                    raise HTTPException(
                        status_code=401, 
                        detail="Password required or incorrect password provided."
                    )
            
            clean_pdf = fitz.open()
            clean_pdf.insert_pdf(doc)
            clean_bytes = clean_pdf.write(clean=True, deflate=True)
            clean_pdf.close()
            doc.close()

            output_stream = io.BytesIO(clean_bytes)
            output_stream.seek(0)
            clean_filename = f"unlocked_{file.filename}"
            return StreamingResponse(
                output_stream,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{clean_filename}"',
                    "Access-Control-Expose-Headers": "Content-Disposition"
                }
            )
        except HTTPException:
            raise
        except Exception as e_fitz:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse or repair PDF structure: {str(e_pikepdf)} | Fallback: {str(e_fitz)}"
            )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
