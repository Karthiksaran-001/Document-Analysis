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
        pass 
    def compare_documents(self):
        pass 
    def _format_response(self):
        pass
    

