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
from utils.config_loader import load_config
from utils.model_loader import ModelLoader
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

class DBManager:
    pass
class DocHandler:
    pass
class DocumentComparator:
    pass
class ChatIngestor:
    pass