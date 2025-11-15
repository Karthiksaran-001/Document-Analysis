from setuptools import setup  , find_packages

setup(
    name = "document_analysis",
    author= "Karthik Saran",
    version="0.0.1",
    description="RAG Pipeline to build customized Document Comparision",
    packages= find_packages(),
    install_requires =[
    "langchain",
    "langchain-community",
    "langchain-core",
    "langchain-groq",
    "langchain-google-genai",
    "faiss-cpu",
    "ragas",
    "langchain-astradb",
    "fastapi",
    "uvicorn",
    "python-dotenv",
    "python-multipart",
    "PyMuPDF",
    "structlog",
    "docx2txt",
    "ipykernel",
    "streamlit",
    "pytest",
])