import os
from pathlib import Path
import warnings
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException
from utils.model_loader import ModelLoader


class ConversationalRAG:
    def __init__(self):
        try:
            pass
        except Exception as e:
            log.error("Error in ConversationalRAG Initalizer" , error=str(e))
            raise DocumentException("Error in ConversationalRAG Initalizer")
    def load_retriever_from_asda(self):
        try:
            pass
        except Exception as e:
            log.error("Error in Load Retriever" , error=str(e))
            raise DocumentException("Error in Load Retriever")
    def invoke(self):
        try:
            pass
        except Exception as e:
            self.log.error("Failed in load retriver faiss" , error = str(e))
            raise DocumentException(e)
    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            log.info("LLM loads successfully" , class_name = llm.__class__.__name__)
            return llm 
        except Exception as e:
            log.error("Error in Load LLM" , error=str(e))
            raise DocumentException("Error in Load LLM")
    @staticmethod
    def _format_docs():
        try:
            pass
        except Exception as e:
            log.error("Error in Formatting Document" , error=str(e))
            raise DocumentException("Error in Formatting Document")
        
    def _build_lcel_chain(self):
        try:
            pass
        except Exception as e:
            log.error("Error in Building LCEL" , error=str(e))
            raise DocumentException("Error in Building LCEL")