from __future__ import annotations
import os
import json
import uuid
from pathlib import Path 
import shutil
import hashlib
from typing import Iterable , List , Optional , Dict , Any
from datetime import datetime , timezone
import fitz
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader , TextLoader,PyPDFLoader
from astrapy import DataAPIClient
from langchain_astradb.vectorstores import AstraDBVectorStore
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException
from utils.config_loader import load_config
from utils.document_ops import read_pdf ,load_documents, clean_old_sessions, concat_for_comparison
from utils.file_io import generate_session_id, save_uploaded_files
from utils.model_loader import ModelLoader
from dotenv import load_dotenv
import warnings
load_dotenv()
warnings.filterwarnings("ignore")
SUPPORTED_EXTENSIONS = {".pdf", ".txt",".docx",".doc",".md"}
class DBManager:
    def __init__(self, data_dir ,model_loader:Optional[ModelLoader] = None):
        try:
            self.config = load_config()
            self.data_dir = data_dir
            self.collection_name = self.config["astra_db"]["collection_name"]
            self.api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT") 
            self.db_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
            self.collection_name = self.config["astra_db"]["collection_name"]
            self.db_keyspace = self.config["astra_db"]["key_space"]
            self.embedding = ModelLoader().load_embeddings() 
            self.meta_path = self.data_dir / "ingested_meta.json"
            self._meta: Dict[str, Any] = {"rows": {}} ## this is dict of rows
            if self.meta_path.exists():
                try:
                    self._meta = json.loads(self.meta_path.read_text(encoding="utf-8")) or {"rows": {}} # load it if alrady there
                except Exception:
                    self._meta = {"rows": {}} # init the empty one if dones not exists
            self.model_loader = model_loader or ModelLoader()
            self.emb = self.model_loader.load_embeddings()
            self.vs: Optional[AstraDBVectorStore] = None
        except Exception as e:
            log.error("Error While DB Manager in Data Ingestion",error = str(e))
            raise DocumentException("Error While DB Manager in Data Ingestion")
    def _exists(self):
        try:
            db = DataAPIClient(self.db_token).get_database(self.api_endpoint)
            collections = db.list_collections()
            return any(col.name == self.collection_name for col in collections)
        except Exception as e:
            log.error("Error in existing method" , error = str(e))
            raise DocumentException("Error While DB Mangining in Data Ingestion")
    @staticmethod
    def _fingerprint(text: str, md: Dict[str, Any]):
        try:
            src = md.get("source") or md.get("file_path")
            rid = md.get("row_id")
            if src is not None:
                return f"{src}::{'' if rid is None else rid}"
            return hashlib.sha256(text.encode("utf-8")).hexdigest()
        except Exception as e:
            log.error("Error in Checking Duplicates in Fingerprint" , error = str(e))
            raise DocumentException("Error in Checking Duplicates in Fingerprint")
    def db_connection(self):
        try:
            
            self.vs = AstraDBVectorStore(
            embedding= self.embedding,
            collection_name=self.collection_name,
            api_endpoint=self.api_endpoint,
            token=self.db_token,
            namespace=self.db_keyspace,)
        except Exception as e:
            log.error("Error in Connecting Astra DB" , error = str(e))
            raise DocumentException("Error in Connecting Astra DB")
    def _save_meta(self):
        try:
            self.meta_path.write_text(json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            log.error("Error in Saving MetaData" , error = str(e))
            raise DocumentException("Error in Error in Saving MetaData")
    def add_documents(self,docs: List[Document]):
        try:
            if self.vs is None:
                raise RuntimeError("Call load_or_create() before add_documents_idempotent().")
            new_docs: List[Document] = []
        
            for d in docs:
                key = self._fingerprint(d.page_content, d.metadata or {})
                if key in self._meta["rows"]:
                    continue
                self._meta["rows"][key] = True
                new_docs.append(d)
                
            if new_docs:
                self.vs.add_documents(new_docs)
                self._save_meta()
            return len(new_docs)
        except Exception as e:
            log.error("Error in Adding Documents" , error = str(e))
            raise DocumentException("Error in Adding Documents")    
    def load_or_create(self,texts:Optional[List[str]]=None, metadatas: Optional[List[dict]] = None):
        try:
            if self._exists():
                self.db_connection()
            if not texts:
                raise DocumentException("No existing Collection name  and no data to create one")
            self.vs.from_texts(texts , embedding=self.embedding ,metadatas=metadatas or [])
            return self.vs
        except Exception as e:
            log.error("Error in Create or Load AstraDB" , error = str(e))
            raise DocumentException("Error in Create or Load AstraDB")
        
class DocHandler:
    """
        PDF save + read (page-wise) for analysis.
    """
    def __init__(self,data_dir: Optional[str] = None, session_id: Optional[str] = None):
        try:
            self.data_dir = data_dir or os.getenv("DATA_STORAGE_PATH", os.path.join(os.getcwd(), "data", "document_analysis"))
            self.session_id = session_id or generate_session_id("session")
            self.session_path = os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok=True)
            log.info("DocHandler initialized", session_id=self.session_id, session_path=self.session_path)
        except Exception as e:
            log.error("Error While Document Handler in Data Ingestion",error = str(e))
            raise DocumentException("Error While Document Handler in Data Ingestion")
    def save_pdf(self,uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)
            if not filename.lower().endswith(".pdf"):
                raise ValueError("Invalid file type. Only PDFs are allowed.")
            save_path = os.path.join(self.session_path, filename)
            clean_old_sessions(log,Path(self.data_dir))
            with open(save_path, "wb") as f:
                if hasattr(uploaded_file, "read"):
                    f.write(uploaded_file.read())
                else:
                    f.write(uploaded_file.getbuffer())
            log.info("PDF saved successfully", file=filename, save_path=save_path, session_id=self.session_id)
            return save_path
        except Exception as e:
            log.error("Error While Save PDF in Document Handler",error = str(e))
            raise DocumentException("Error While Save PDF in Document Handler")
        
class DocumentComparator:
    """
        Save, read & combine PDFs for comparison with session-based versioning.
    """
    def __init__(self,base_dir: str = "data/document_compare", session_id: Optional[str] = None):
        try:
            self.base_dir = Path(base_dir)
            self.session_id = session_id or generate_session_id()
            self.session_path = self.base_dir / self.session_id
            self.session_path.mkdir(parents=True, exist_ok=True)
            log.info("DocumentComparator initialized", session_path=str(self.session_path))
        except Exception as e:
            log.error("Error While Document Comparator in Data Ingestion",error = str(e))
            raise DocumentException("Error While Document Comparator in Data Ingestion")
    def save_uploaded_files(self,reference_file, actual_file):
        try:
            ref_path = self.session_path / reference_file.name
            act_path = self.session_path / actual_file.name
            for fobj, out in ((reference_file, ref_path), (actual_file, act_path)):
                if not fobj.name.lower().endswith(".pdf"):
                    raise ValueError("Only PDF files are allowed.")
                with open(out, "wb") as f:
                    if hasattr(fobj, "read"):
                        f.write(fobj.read())
                    else:
                        f.write(fobj.getbuffer())
            log.info("Files saved", reference=str(ref_path), actual=str(act_path), session=self.session_id)
            clean_old_sessions(log,self.base_dir)
            return ref_path, act_path
        except Exception as e:
            log.error("Error While Saving Uploaded Documents in Data Ingestion",error = str(e))
            raise DocumentException("Error While Saving Uploaded Documents in Data Ingestion")
    def combine_documents(self):
        try:
            doc_parts = []
            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower() == ".pdf":
                    content = read_pdf(file,self.session_id)
                    doc_parts.append(f"Document: {file.name}\n{content}")
            combined_text = "\n\n".join(doc_parts)
            log.info("Documents combined", count=len(doc_parts), session=self.session_id)
            return combined_text
        except Exception as e:
            log.error("Error While Combining Docs in Document Comparator",error = str(e))
            raise DocumentException("Error While Combining Docs in Document Comparator")
class ChatIngestor:
    def __init__(self, temp_base: str = "data",
        collection_name: str = None,
        use_session_dirs: bool = True,
        session_id: Optional[str] = None,):
        try:
            self.model_loader = ModelLoader()
            self.use_session = use_session_dirs
            self.collection_name = collection_name
            self.session_id = session_id or generate_session_id()
            self.temp_base = Path(temp_base); self.temp_base.mkdir(parents=True, exist_ok=True)
            self.temp_dir = self._resolve_dir(self.temp_base)
            log.info("ChatIngestor initialized",
                      session_id=self.session_id,
                      temp_dir=str(self.temp_dir),
                      collection_name=self.collection_name,
                      sessionized=self.use_session)
        except Exception as e:
            log.error("Error While Initalizing ChatIngestor",error = str(e))
            raise DocumentException("Error While Clearning Old Sessions in Document Comparator")
    def _resolve_dir(self,base: Path):
        try:
            if self.use_session:
                d = base / self.session_id # e.g. "data/abc123"
                d.mkdir(parents=True, exist_ok=True) # creates dir if not exists
                return d
            return base
        except Exception as e:
            log.error("Error While Resolve dir in ChatIngestor",error = str(e))
            raise DocumentException("Error While Resolve dir in Document Comparator")
    def _split(self, docs: List[Document], chunk_size=1000, chunk_overlap=200) -> List[Document]:
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            chunks = splitter.split_documents(docs)
            log.info("Documents split", chunks=len(chunks), chunk_size=chunk_size, overlap=chunk_overlap)
            return chunks
        except Exception as e:
            log.error("Error While Splitting the Document in ChatIngestor",error = str(e))
            raise DocumentException("Error While Splitting the Document in Document Comparator")
    def build_retriever(self,uploaded_files: Iterable,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        k: int = 5,):
        try:
            paths = save_uploaded_files(uploaded_files, self.temp_dir)
            docs = load_documents(paths)
            if not docs:
                raise ValueError("No valid documents loaded")
            chunks = self._split(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            fm = DBManager(self.temp_dir, self.model_loader)
            texts = [c.page_content for c in chunks]
            metas = [c.metadata for c in chunks]
            try:
                vs = fm.load_or_create(texts=texts, metadatas=metas)
            except Exception:
                vs = fm.load_or_create(texts=texts, metadatas=metas)
            added = fm.add_documents(chunks)
            log.info("Vector DB index updated", added=added, collection=str(self.collection_name))
            return vs.as_retriever(search_type="similarity", search_kwargs={"k": k})
            
        except Exception as e:
            log.error("Error While Build Retriever in ChatIngestor",error = str(e))
            raise DocumentException("Error While Build Retriever in Document Comparator")
    
