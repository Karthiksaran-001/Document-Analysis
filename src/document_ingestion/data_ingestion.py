from __future__ import annotations
import os
import sys
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
from langchain_astradb.vectorstores import AstraDBVectorStore
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException
from utils.config_loader import load_config
from utils.model_loader import ModelLoader
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")

class DBManager:
    def __init__(self):
        try:
            pass
        except Exception as e:
            log.error("Error While DB Manager in Data Ingestion",error = str(e))
            raise DocumentException("Error While DB Manager in Data Ingestion")
    def _exists(self):
        try:
            pass
        except Exception as e:
            log.error("Error in existing method" , error = str(e))
            raise DocumentException("Error While DB Mangining in Data Ingestion")
    @staticmethod
    def fingerprint():
        try:
            pass
        except Exception as e:
            log.error("Error in Checking Duplicates in Fingerprint" , error = str(e))
            raise DocumentException("Error in Checking Duplicates in Fingerprint")
    def db_connection(self):
        try:
            pass
        except Exception as e:
            log.error("Error in Connecting Astra DB" , error = str(e))
            raise DocumentException("Error in Connecting Astra DB")
    def save_meta(self):
        try:
            pass
        except Exception as e:
            log.error("Error in Saving MetaData" , error = str(e))
            raise DocumentException("Error in Error in Saving MetaData")
    def add_documents(self):
        try:
            pass
        except Exception as e:
            log.error("Error in Adding Documents" , error = str(e))
            raise DocumentException("Error in Adding Documents")    
    def load_or_create(self):
        try:
            pass
        except Exception as e:
            log.error("Error in Create or Load AstraDB" , error = str(e))
            raise DocumentException("Error in Create or Load AstraDB")
        
class DocHandler:
    def __init__(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Document Handler in Data Ingestion",error = str(e))
            raise DocumentException("Error While Document Handler in Data Ingestion")
    def read_pdf(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Reading PDF in Document Handler",error = str(e))
            raise DocumentException("Error While Reading PDF in Document Handler")
    def save_pdf(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Save PDF in Document Handler",error = str(e))
            raise DocumentException("Error While Save PDF in Document Handler")
        
class DocumentComparator:
    def __init__(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Document Comparator in Data Ingestion",error = str(e))
            raise DocumentException("Error While Document Comparator in Data Ingestion")
    def save_uploaded_files(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Saving Uploaded Documents in Data Ingestion",error = str(e))
            raise DocumentException("Error While Saving Uploaded Documents in Data Ingestion")
    def read_pdf(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Reading PDF in Document Comparator",error = str(e))
            raise DocumentException("Error While Reading PDF in Document Comparator")
    def combine_documents(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Combining Docs in Document Comparator",error = str(e))
            raise DocumentException("Error While Combining Docs in Document Comparator")
    def clean_old_sessions(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Clearning Old Sessions in Document Comparator",error = str(e))
            raise DocumentException("Error While Clearning Old Sessions in Document Comparator")
class ChatIngestor:
    def __init__(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Initalizing ChatIngestor",error = str(e))
            raise DocumentException("Error While Clearning Old Sessions in Document Comparator")
    def _resolve_dir(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Resolve dir in ChatIngestor",error = str(e))
            raise DocumentException("Error While Resolve dir in Document Comparator")
    def _split(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Splitting the Document in ChatIngestor",error = str(e))
            raise DocumentException("Error While Splitting the Document in Document Comparator")
    def build_retriever(self):
        try:
            pass
        except Exception as e:
            log.error("Error While Build Retriever in ChatIngestor",error = str(e))
            raise DocumentException("Error While Build Retriever in Document Comparator")
    
