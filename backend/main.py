from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import shutil
import os

from models import QuestionRequest, AnswerResponse

from rag import (
    extract_text_from_pdf,
    chunk_text,
    build_faiss_index,
    retrieve_relevant_chunks,
    ask_groq
)

# Load environment variables
load_dotenv()

app = FastAPI(title="PDF RAG API")


# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def health_check():
    return {"message": "PDF RAG Backend Running"}


# -----------------------------
# Upload PDF Endpoint
# -----------------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    try:

        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save uploaded PDF
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_path)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF"
            )

        # Chunk text
        chunks = chunk_text(extracted_text)

        if len(chunks) == 0:
            raise HTTPException(
                status_code=400,
                detail="Failed to create chunks from PDF"
            )

        # Build FAISS index
        build_faiss_index(chunks)

        return {
            "message": "PDF processed successfully",
            "filename": file.filename,
            "chunks": len(chunks)
        }

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload processing failed: {str(e)}"
        )


# -----------------------------
# Ask Question Endpoint
# -----------------------------
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):

    try:

        question = request.question.strip()

        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        # Retrieve relevant chunks from FAISS
        relevant_chunks, similarity = retrieve_relevant_chunks(question)

        # HARD HALLUCINATION BLOCK
        # If no sufficiently relevant chunks exist,
        # NEVER call the LLM.
        if len(relevant_chunks) == 0:
            return AnswerResponse(
                answer="I don't know based on the provided document."
            )

        # Ask Groq using retrieved context
        answer = ask_groq(relevant_chunks, question)

        return AnswerResponse(answer=answer)

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(e)}"
        )


# -----------------------------
# Run:
# uvicorn main:app --reload
# -----------------------------