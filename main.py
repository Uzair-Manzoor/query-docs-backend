from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

import fitz  # PyMuPDF
import uvicorn

app = FastAPI()

# Initialize the LLM (e.g., OpenAI GPT)
llm = OpenAI(api_key='openai-api-key', model_name="text-davinci-003")

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="Context: {context}\n\nQuestion: {question}\n\nAnswer:",
)

# Set up the chain
qa_chain = LLMChain(llm=llm, prompt=prompt_template)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    with open(f"uploaded_files/{file.filename}", "wb") as f:
        f.write(content)

    pdf_document = fitz.open(f"uploaded_files/{file.filename}")
    text = ""
    for page_num in range(len(pdf_document)):
        text += pdf_document.load_page(page_num).get_text()

    # In a real application, you would save document details and extracted text to a database
    # Here we just return the text for simplicity
    return {"filename": file.filename, "text": text}

@app.post("/ask")
async def ask_question(filename: str = Form(...), question: str = Form(...)):
    # For simplicity, let's assume the file content is stored in memory
    # In a real application, you'd fetch the document's text from a database
    try:
        with open(f"uploaded_files/{filename}", "rb") as f:
            pdf_document = fitz.open(stream=f.read(), filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            text += pdf_document.load_page(page_num).get_text()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

    # Use LangChain to process the question
    answer = qa_chain.run({"context": text, "question": question})
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
