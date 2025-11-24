import os
from pathlib import Path
import warnings
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException


class DocumentIngestion:
    def __init__(self):
        try:
            pass 
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