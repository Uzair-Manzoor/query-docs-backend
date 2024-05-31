import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import fitz  # PyMuPDF
import openai

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://ask-openai-theta.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

openai.api_key = "openai-key"

class AskRequest(BaseModel):
    filename: str
    question: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info("Received file upload request")
        with open("temp.pdf", "wb") as f:
            f.write(file.file.read())
        logger.info("File saved as temp.pdf")
        return {"filename": "temp.pdf"}
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

@app.post("/ask")
async def ask_question(request: AskRequest):
    try:
        logger.info(f"Received question for file: {request.filename}")
        pdf_document = fitz.open(request.filename)
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        logger.info("Extracted text from PDF")

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=request.question + "\n\n" + text,
            max_tokens=100
        )
        answer = response.choices[0].text.strip()
        logger.info(f"Received answer from OpenAI: {answer}")
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    yield
    logger.info("Shutting down the application...")

app.router.lifespan = lifespan

@app.get("/")
async def read_root():
    logger.info("Received request to root endpoint")
    return {"message": "Welcome to QueryDocs Backend!"}
