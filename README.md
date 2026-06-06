# 📄 PDF RAG Assistant
A production-ready Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions grounded strictly in the document content.

The application uses:
- FastAPI (Backend)
- Vanilla HTML/CSS/JavaScript (Frontend)
- Groq API (LLM)
- FAISS (Vector Database)
- Sentence Transformers (Embeddings)
- PyMuPDF (PDF Parsing)

## 🚀 Features

### PDF Processing

- Upload PDF documents
- Extract text using PyMuPDF
- Fixed-size chunking with overlap
- Local embedding generation
- FAISS vector indexing

### Question Answering

- Semantic similarity search
- Retrieval-Augmented Generation (RAG)
- Context-grounded responses
- Similarity threshold filtering
- Hallucination prevention

### User Interface

- Drag-and-drop PDF upload
- Chat-style question answering
- Loading indicators
- Error handling
- Responsive design

### Logging

- Backend logging
- Frontend error logging
- Log file rotation
- Terminal monitoring

---

## 🏗 Architecture

```text
User
 │
 ▼
Frontend (HTML/CSS/JS)
 │
 ▼
FastAPI Backend
 │
 ├── PDF Upload
 │      │
 │      ▼
 │   PyMuPDF
 │      │
 │      ▼
 │   Chunking
 │      │
 │      ▼
 │ Sentence Transformers
 │      │
 │      ▼
 │     FAISS
 │
 └── Question
        │
        ▼
   Similarity Search
        │
        ▼
  Retrieved Context
        │
        ▼
      Groq LLM
        │
        ▼
      Answer
```

---

## 📁 Project Structure

```text
pdf-rag/
├── backend/
│   ├── main.py
│   ├── rag.py
│   ├── models.py
│   ├── logger.py
│   ├── requirements.txt
│   ├── uploads/
│   └── logs/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/pdf-rag.git

cd pdf-rag
```

### 2. Create Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

### 3. Install Dependencies

```bash
cd backend

pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-8b-8192
```

---

## ▶ Running the Backend

From the backend folder:

```bash
uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## ▶ Running the Frontend

Open:

```text
frontend/index.html
```

Or serve using Python:

```bash
cd frontend

python -m http.server 5500
```

Then visit:

```text
http://localhost:5500
```

---

## 🔍 API Endpoints

### Upload PDF

```http
POST /upload
```

Request:

```form-data
file=<pdf-file>
```

Response:

```json
{
  "message": "PDF processed successfully",
  "filename": "sample.pdf",
  "chunks": 42
}
```

---

### Ask Question

```http
POST /ask
```

Request:

```json
{
  "question": "What is the main objective?"
}
```

Response:

```json
{
  "answer": "The document states that..."
}
```

---

## 🛡 Hallucination Prevention

The system enforces strict grounding:

- Retrieved chunks are passed verbatim.
- Similarity threshold filtering is applied.
- If no relevant chunk exists:
  
```text
I don't know based on the provided document.
```

- Temperature is set to 0.
- The LLM is instructed to answer only from context.

---

## 📊 Tech Stack

| Component | Technology |
|------------|------------|
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI |
| LLM | Groq |
| Embeddings | Sentence Transformers |
| Vector Store | FAISS |
| PDF Parsing | PyMuPDF |
| Logging | Python Logging |

---

## 📈 Future Improvements

- Multiple PDF support
- Persistent FAISS storage
- Source citations
- Hybrid search (BM25 + Vector)
- Conversation memory
- User authentication
- Docker deployment
- Cloud deployment

---

## 👨‍💻 Author

Built as a Retrieval-Augmented Generation (RAG) project demonstrating:

- Vector Search
- Semantic Retrieval
- LLM Integration
- FastAPI Development
- AI Application Engineering
