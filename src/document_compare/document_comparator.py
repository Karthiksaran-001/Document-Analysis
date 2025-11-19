import os
from pathlib import Path 
from dotenv import load_dotenv
import pandas as pd
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
import warnings
warnings.filterwarnings("ignore")

class DocumentComparator:
    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm() 
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(parser = self.parser , llm = self.llm)
        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.parser | self.fixing_parser
        self.log("DocumentComparator Initalized the model with parser")
    def compare_documents(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error Occured with Comparing the Documents", e)
            raise DocumentException("Error Occured with Comparing the Documents") 
    def _format_response(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error Occured with Formating the Documents", e)
            raise DocumentException("Error Occured with Formating the Documents") 


