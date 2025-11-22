import uuid
from pathlib import Path 
import sys
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_astradb.vectorstores import AstraDBVectorStore
from logger import GLOBAL_LOGGER as log 
from exception.custom_exception import DocumentException
from utils.model_loader import ModelLoader

class SingleDocIngestor:
    def __init__(self):
        try:
            pass 
        except Exception as e:
            log.error("Error in SingleDocIngestor Initalizer" , error=str(e))
            raise DocumentException("Error in SingleDocIngestor Initalizer")
    def ingest_files(self):
        try:
            pass 
        except Exception as e:
            log.error("Error in Ingest File" , error=str(e))
            raise DocumentException("Error in Ingest File")
    def _create_retriever(self):
        try:
            pass 
        except Exception as e:
            log.error("Error in Retriever Creation" , error=str(e))
            raise DocumentException("Error in Retriever Creation")
    
