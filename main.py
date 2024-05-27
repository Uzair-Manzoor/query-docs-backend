# backend/main.py
from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF

app = FastAPI()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    # Save PDF and extract text (implement later)
    return {"filename": file.filename}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
