# Codebase Q&A Agent 🔍

An intelligent developer tool that lets you ask natural language questions about any public GitHub repository. Paste a repo URL and instantly get an AI-powered assistant that understands the entire codebase — architecture, functions, flows, and more.

> Built as an open-source alternative to Cursor's codebase chat feature.

---

## 🚀 Live Demo

- Frontend: _coming soon_
- Backend API: _coming soon_

---

## ✨ Features

- **AST-Aware Chunking** — Code is split by functions and classes using Tree-sitter, not arbitrary character limits. This is how production tools like Cursor work.
- **Hybrid Retrieval** — Combines semantic search (FAISS) and keyword search (BM25) for best-of-both-worlds retrieval.
- **Reciprocal Rank Fusion (RRF)** — Merges results from both retrievers using RRF scoring for optimal ranking.
- **Gemini-Powered Answers** — Answers cite exact file paths and line numbers from the codebase.
- **Source Panel** — Every answer shows which code chunks were used, with file name, line numbers, and RRF confidence score.
- **Multi-language Support** — Supports Python, JavaScript, TypeScript, and Java repositories.

---

## 🏗️ Architecture
GitHub URL

↓

[Cloner] → Clone repo via GitPython

↓

[Parser] → AST chunking via Tree-sitter (functions, classes)

↓

[Indexer] → FAISS vector index + BM25 keyword index

↓

[Query]

↓

[Semantic Search] + [BM25 Search]

↓

[Reciprocal Rank Fusion]

↓

[Gemini 2.5 Flash] → Answer with source citations

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS |
| Keyword Search | BM25 (rank-bm25) |
| AST Parsing | Tree-sitter |
| Repo Cloning | GitPython |
| Frontend | React + Vite + Tailwind CSS |

---

## 📁 Project Structure

codebase-qa-agent/

├── backend/

│   ├── main.py                  # FastAPI endpoints

│   ├── ingestion/

│   │   ├── cloner.py            # GitHub repo cloning

│   │   ├── parser.py            # AST-based chunking

│   │   └── indexer.py           # FAISS + BM25 index builder

│   ├── retrieval/

│   │   ├── semantic.py          # FAISS semantic search

│   │   ├── keyword.py           # BM25 keyword search

│   │   └── fusion.py            # Reciprocal Rank Fusion

│   ├── generation/

│   │   └── answer.py            # Gemini answer generation

│   └── requirements.txt

└── frontend/

└── src/

└── App.jsx              # React chat interface

---

## ⚙️ Local Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` folder:
GOOGLE_API_KEY=your_gemini_api_key_here

Run the backend:

```bash
uvicorn main:app
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/ingest` | Clone and index a GitHub repo |
| POST | `/query` | Ask a question about the codebase |
| GET | `/status` | Check current index status |

### Example

```bash
# Index a repo
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/user/repo"}'

# Ask a question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How does authentication work?", "top_k": 5}'
```

---

## 🧠 How It Works

1. **Ingest** — GitPython clones the repo locally
2. **Parse** — Tree-sitter parses each file into AST nodes (functions, classes)
3. **Index** — sentence-transformers embeds each chunk into FAISS; BM25 indexes tokens
4. **Retrieve** — Both indexes are queried; results are fused with RRF
5. **Generate** — Top chunks are passed to Gemini with a system prompt; answer is returned with source citations

---

## 👩‍💻 Author

**Nikitha Dinesh Kumar**
B.E. Computer Science Engineering, St. Joseph's Institute of Technology
[GitHub](https://github.com/NikithaDineshKumar) • [LinkedIn](https://linkedin.com/in/your-linkedin)

---

## 📄 License

MIT License
