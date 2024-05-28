# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz  # PyMuPDF

app = FastAPI()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    with open(f"uploaded_files/{file.filename}", "wb") as f:
        f.write(content)

    pdf_document = fitz.open(f"uploaded_files/{file.filename}")
    text = ""
    for page_num in range(len(pdf_document)):
        text += pdf_document.load_page(page_num).get_text()

    # Save document details and extracted text to the database
    return {"filename": file.filename, "text": text}

@app.post("/ask")
async def ask_question(filename: str, question: str):
    # Retrieve the document text from the database
    session = SessionLocal()
    document = session.query(Document).filter(Document.filename == filename).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Process the question using LangChain/LLamaIndex
    # For now, return a dummy response
    return {"answer": "This is a placeholder answer."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
