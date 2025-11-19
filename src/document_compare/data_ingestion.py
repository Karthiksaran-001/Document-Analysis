import os
from pathlib import Path 
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentException
import warnings
warnings.filterwarnings("ignore")


class DocumentComparator:
    def __init__(self):
        pass 
    def delete_existing_file(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error Occured while Delete the Documents", e)
            raise DocumentException("Error Occured while Delete the Documents")  
    def save_uploaded_files(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error Occured while Save the Documents", e)
            raise DocumentException("Error Occured while Save the Documents") 
    def read_pdf(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error Occured while Reading the Documents", e)
            raise DocumentException("Error Occured while Reading the Documents") 
