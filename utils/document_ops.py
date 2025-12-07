from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
from fastapi import UploadFile
import fitz
import shutil
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader,UnstructuredWordDocumentLoader
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt" , ".md"}


def load_documents(paths: Iterable[Path]) -> List[Document]:
    """Load docs using appropriate loader based on extension."""
    docs: List[Document] = []
    try:
        for p in paths:
            ext = p.suffix.lower()
            if ext == ".pdf":
                loader = PyPDFLoader(str(p))
            elif ext in [".doc" , ".docx"]:
                    if ext == ".docx":
                        loader = Docx2txtLoader(str(p))
                    else:
                        loader = UnstructuredWordDocumentLoader(str(p))
            elif ext in [".txt" , ".md"]:
                loader = TextLoader(str(p), encoding="utf-8")
            else:
                log.warning("Unsupported extension skipped", path=str(p))
                continue
            docs.extend(loader.load())
        log.info("Documents loaded", count=len(docs))
        return docs
    except Exception as e:
        log.error("Failed loading documents", error=str(e))
        raise DocumentException("Error loading documents", e) from e

def concat_for_analysis(docs: List[Document]) -> str:
    parts = []
    for d in docs:
        src = d.metadata.get("source") or d.metadata.get("file_path") or "unknown"
        parts.append(f"\n--- SOURCE: {src} ---\n{d.page_content}")
    return "\n".join(parts)

def concat_for_comparison(ref_docs: List[Document], act_docs: List[Document]) -> str:
    left = concat_for_analysis(ref_docs)
    right = concat_for_analysis(act_docs)
    return f"<<REFERENCE_DOCUMENTS>>\n{left}\n\n<<ACTUAL_DOCUMENTS>>\n{right}"

def read_pdf(pdf_path:Path,session_id):
    try:
        text_chunks = []
        with fitz.open(pdf_path) as doc:
            if doc.is_encrypted:
                raise ValueError(f"PDF is encrypted: {pdf_path.name}")
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text_chunks.append(f"\n--- Page {page_num + 1} ---\n{page.get_text()}")  # type: ignore
        text = "\n".join(text_chunks)
        log.info("PDF read successfully", pdf_path=pdf_path, session_id=session_id, pages=len(text_chunks))
        return text
    except Exception as e:
            log.error("Error While Reading PDF in Document Handler",error = str(e))
            raise DocumentException("Error While Reading PDF in Document Handler")

def clean_old_sessions(log,base_dir,keep_latest:int = 3):
    try:
        sessions = sorted([f for f in base_dir.iterdir() if f.is_dir()], reverse=True)
        for folder in sessions[keep_latest:]:
            shutil.rmtree(folder, ignore_errors=True)
        log.info("Old session folder deleted", path=str(folder))
    except Exception as e:
            log.error("Error While Clearning Old Sessions in Document Comparator",error = str(e))
            raise DocumentException("Error While Clearning Old Sessions in Document Comparator")

def get_memory(memory_store , session_id: str, token_limit:int = 1500, llm = None):
    if session_id not in memory_store:
        memory_store[session_id] = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=token_limit,
            memory_key="chat_history",
            return_messages=True
        )
    return memory_store[session_id]


# ---------- Helpers ----------
class FastAPIFileAdapter:
    """Adapt FastAPI UploadFile -> .name + .getbuffer() API"""
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename
    def getbuffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()

# def read_pdf_via_handler(handler, path: str) -> str:
#     if hasattr(handler, "read_pdf"):
#         return handler.read_pdf(path)  # type: ignore
#     if hasattr(handler, "read_"):
#         return handler.read_(path)  # type: ignore
#     raise RuntimeError("DocHandler has neither read_pdf nor read_ method.")