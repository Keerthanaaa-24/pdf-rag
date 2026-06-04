import fitz
import faiss
import numpy as np
import requests
import os

from sentence_transformers import SentenceTransformer
from typing import List, Tuple



embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# =====================================================
# Global Storage
# =====================================================

document_chunks = []
faiss_index = None


# =====================================================
# Configuration
# =====================================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Lower threshold improves retrieval for small PDFs
SIMILARITY_THRESHOLD = 0.20

SYSTEM_PROMPT = """
You are a factual PDF assistant.

Answer ONLY from the provided context.

If the answer is not available in the context, reply exactly:

"I don't know based on the provided document."

Do not hallucinate.
Do not make assumptions.
Do not use outside knowledge.
"""


# =====================================================
# PDF Text Extraction
# =====================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using PyMuPDF.
    """

    try:
        doc = fitz.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text

    except Exception as e:
        raise Exception(f"Failed to extract PDF text: {str(e)}")


# =====================================================
# Chunking
# =====================================================

def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = words[start:end]

        chunks.append(" ".join(chunk))

        start += chunk_size - overlap

    return chunks


# =====================================================
# Build FAISS Index
# =====================================================

def build_faiss_index(chunks: List[str]):

    global document_chunks
    global faiss_index

    document_chunks = chunks

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True
    )

    embeddings = embeddings.astype("float32")

    dimension = embeddings.shape[1]

    faiss_index = faiss.IndexFlatL2(dimension)

    faiss_index.add(embeddings)


# =====================================================
# Retrieve Relevant Chunks
# =====================================================

def retrieve_relevant_chunks(
    query: str,
    top_k: int = 5
) -> Tuple[List[str], float]:

    global faiss_index
    global document_chunks

    if faiss_index is None:
        return [], 0.0

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    query_embedding = query_embedding.astype("float32")

    distances, indices = faiss_index.search(
        query_embedding,
        top_k
    )

    retrieved_chunks = []

    best_similarity = 0.0

    for distance, idx in zip(distances[0], indices[0]):

        if idx == -1:
            continue

        similarity = 1 / (1 + distance)

        best_similarity = max(
            best_similarity,
            similarity
        )

        if similarity >= SIMILARITY_THRESHOLD:

            retrieved_chunks.append(
                document_chunks[idx]
            )

    return retrieved_chunks, best_similarity


# =====================================================
# Ask Groq
# =====================================================

def ask_groq(
    context_chunks: List[str],
    question: str
) -> str:

    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise Exception(
            "Missing GROQ_API_KEY in environment variables"
        )

    # Updated Groq model
    groq_model = "llama-3.1-8b-instant"

    context = "\n\n".join(context_chunks)

    user_prompt = f"""
Context:
{context}

Question:
{question}

Answer ONLY from the provided context.
"""

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": groq_model,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0,
        "max_tokens": 512
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(
            f"Groq API Error: {response.status_code} - {response.text}"
        )

    result = response.json()

    return result["choices"][0]["message"]["content"].strip()
