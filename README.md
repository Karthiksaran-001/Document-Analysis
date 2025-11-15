# Document Portal Pipeline — README

**Project Objective :**
A lightweight Retrieval-Augmented Generation (RAG) pipeline to automate document ingestion, analysis, querying, and comparison across multiple file formats (PDF, DOCX, TXT, HTML, etc.). The pipeline extracts structured text, builds a searchable vector store, answers business queries over documents, and compares two documents according to business rules (differences in content, sentiment, or metrics).

**Tech Stack :**
    - LangChain — orchestration of LLM + retrieval flows
    - AstraDB (Scylla/Cassandra-compatible or Astra DB) — metadata & vector storage (or other vector DBs)
    - Python — orchestration, ETL, and API
    - UV — Python virtual environment for dependency isolation
    - Docker & Docker Compose — containerization and easy deployment
    - GROQ — for generation and semantic understanding
    - FastAPI / Uvicorn — lightweight API server (Uvicorn = ASGI server)
    - pytest — tests

**Step-by-step: Create Python virtual environment (venv) & sync**
    1. Install UV 
    ```pip install uv```
    2. Create Venv and Activate
    ```uv init```
    ```uv venv --python 3.11``` (Desired Version >3.10)
    ```.venv\Scripts\activate```
    3. Add Required Packages
    ```uv pip install -r requirements.txt```