import os
from pathlib import Path
import warnings
import uuid
from datetime import datetime , timezone
from langchain_community.document_loaders import PyPDFLoader , Docx2txtLoader , TextLoader
from utils.model_loader import ModelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_astradb.vectorstores import AstraDBVectorStore
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException


class DocumentIngestion:
    SUPPORT_FILE_TYPES = {".pdf" , '.docx' , '.txt' , '.md'}
    def __init__(self, temp_dir:str = r"./data/multi_doc_chat",session_id=None):
        try:
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True , exist_ok=True)
            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_dir = self.temp_dir/self.session_id
            self.session_dir.mkdir(parents=True, exist_ok=True)
            self.model_loader = ModelLoader()
            log.info("DocumentIngestion Initialized",
                     dir_path = str(self.temp_dir),
                     session_id = str(self.session_id),
                     session_dir = str(self.session_dir)) 
        except Exception as e:
            log.error("Error in DocumentIngestion Initalizer" , error = e)
            raise DocumentException("Error in DocumentIngestion Initalizer")
    def ingest_file(self):
        try:
            pass
        except Exception as e:
            log.error("Error in Ingest File" , error = e)
            raise DocumentException("Error in Ingest File")
    def _create_retriever(self):
        try:
            pass 
        except Exception as e:
            log.error("Error in Create Retrieval" , error = e)
            raise DocumentException("Error in Create Retrieval") 