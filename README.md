# Document Portal Pipeline — README

## 🚀 Project Objective
A streamlined **Retrieval-Augmented Generation (RAG) pipeline** designed to automate:
- Document ingestion across multiple formats (PDF, DOCX, TXT, HTML, etc.)
- Semantic analysis and structured extraction
- Smart querying using LLM-augmented retrieval
- Business-driven document comparison based on content, metrics, or semantic differences

This pipeline converts unstructured documents into searchable vector embeddings, enabling fast, accurate, and contextual responses to business queries.

---

## 🛠️ Tech Stack
- **LangChain** — LLM workflow orchestration
- **AstraDB** — Vector + metadata database
- **Python** — Core logic and processing
- **UV** — Modern Python environment & dependency management
- **Docker & Docker Compose** — Deployment and environment consistency
- **GROQ** — High-speed LLM inference
- **FastAPI / Uvicorn** — API layer
- **pytest** — Testing

---

## 📦 Project Flow
1. Upload or ingest documents
2. Extract, clean, and chunk text
3. Generate embeddings (GROQ-compatible models)
4. Store embeddings and metadata in AstraDB
5. Query pipeline retrieves relevant chunks → LLM → final answer
6. Comparison pipeline analyzes differences between two documents
7. Expose all functionality through FastAPI

---

## 🧰 Environment Setup Using UV
UV is a fast Python environment manager that replaces the usual pip + venv workflow.

### 1. Install UV
```bash
pip install uv
```

### **2. Create and Activate Virtual Environment**
```bash
uv init
```
```bash
uv venv --python 3.11  ##use any version >3.10
``` 
```bash
source .venv/bin/activate
```
### 3. Install Dependencies
```bash
uv pip install -r requirements.txt
```
