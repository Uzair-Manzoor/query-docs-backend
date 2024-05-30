from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import fitz  # PyMuPDF
import openai
import os
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class AskRequest(BaseModel):
    filename: str
    question: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.debug("Received file upload request")
    with open("temp.pdf", "wb") as f:
        f.write(file.file.read())
    logger.debug("File saved as temp.pdf")
    return {"filename": "temp.pdf"}

@app.post("/ask")
async def ask_question(request: AskRequest):
    logger.debug(f"Received question for file: {request.filename}")
    pdf_document = fitz.open(request.filename)
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    logger.debug("Extracted text from PDF")

    response = openai.Completion.create(
        engine="davinci",
        prompt=request.question + "\n\n" + text,
        max_tokens=100
    )
    answer = response.choices[0].text.strip()
    logger.debug(f"Received answer from OpenAI: {answer}")
    return JSONResponse(content={"answer": answer})

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logger.debug("Starting up the application...")
    yield
    # Shutdown code
    logger.debug("Shutting down the application...")

app.router.lifespan = lifespan

@app.get("/")
async def read_root():
    logger.debug("Received request to root endpoint")
    return {"message": "Welcome to QueryDocs Backend!"}
