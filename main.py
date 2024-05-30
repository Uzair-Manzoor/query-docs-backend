from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Starting up the application...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down the application...")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    with open(f"uploads/{file.filename}", "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename}

@app.post("/ask")
async def ask_question(filename: str = Form(...), question: str = Form(...)):
    # Dummy implementation of answer generation
    return {"answer": f"Dummy answer to the question: '{question}' based on file: '{filename}'"}

if __name__ == "__main__":
    import uvicorn
    import asyncio

    try:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        print("Server shutdown successfully")
