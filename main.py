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
    "https://ask-openai-d469je5xi-uzairmanzoors-projects.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

openai.api_key = "OPENAI_SECRET_KEY"
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

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Extracted text: {text}\n\nQuestion: {request.question}"}
            ]
        )
        answer = response.choices[0].message["content"].strip()
        logger.info(f"Received answer from OpenAI: {answer}")
        return JSONResponse(content={"answer": answer})
    except openai.error.OpenAIError as e:
        logger.error(f"Error processing question: {str(e)}")
        if isinstance(e, openai.error.RateLimitError):
            return JSONResponse(status_code=429, content={"error": "Rate limit exceeded. Please try again later."})
        elif isinstance(e, openai.error.AuthenticationError):
            return JSONResponse(status_code=401, content={"error": "Authentication error. Please check your API key."})
        elif isinstance(e, openai.error.InsufficientQuotaError):
            return JSONResponse(status_code=402, content={"error": "Insufficient quota. Please check your plan and billing details."})
        else:
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
