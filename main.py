from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from langchain_openai import OpenAI  # Updated import
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import fitz  # PyMuPDF
import uvicorn

app = FastAPI()

# Initialize the LLM / OpenAI GPT
llm = OpenAI(api_key='openai-api-key', model_name="text-davinci-003")

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="Context: {context}\n\nQuestion: {question}\n\nAnswer:",
)

# Set up the chain
qa_chain = LLMChain(llm=llm, prompt=prompt_template)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Query Docs API"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    with open(f"uploaded_files/{file.filename}", "wb") as f:
        f.write(content)

    pdf_document = fitz.open(f"uploaded_files/{file.filename}")
    text = ""
    for page_num in range(len(pdf_document)):
        text += pdf_document.load_page(page_num).get_text()

    return {"filename": file.filename, "text": text}

@app.post("/ask")
async def ask_question(filename: str = Form(...), question: str = Form(...)):
    try:
        with open(f"uploaded_files/{filename}", "rb") as f:
            pdf_document = fitz.open(stream=f.read(), filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            text += pdf_document.load_page(page_num).get_text()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

    answer = qa_chain.run({"context": text, "question": question})
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
