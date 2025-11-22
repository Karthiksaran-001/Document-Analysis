import os , sys 
from pathlib import Path 
from logger import GLOBAL_LOGGER as log
from exception.custom_exception  import DocumentException 
from utils.model_loader import ModelLoader
from prompt.prompt_library import PROMPT_REGISTRY
from dotenv import load_dotenv
import pandas as pd 
from model.models import *
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import JsonOutputParser

class DocumentComparatorLLM:
    def __init__(self):
        load_dotenv()
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm() 
        self.parser = JsonOutputParser(pydantic_object= SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.parser
        log.info("DocumentComparatorLLM initialized with model and parser")
    def compare_documents(self , combined_doc):
        try:
            inputs = {
                "combined_docs" : combined_doc,
                "format_instruction" : self.parser.get_format_instructions()    
            } 
            log.info("Starting Doc Comparision" , inputs = inputs)
            response = self.chain.invoke(inputs)
            log.info("Document Comparision completed" , response = response)
            return self._format_response(response)
        except Exception as e:
            log.error(f"Error Occured while compare_documents : {e}")
            raise DocumentException("Error Occured while compare_documents")
    
    def _format_response(self,response:list[dict])->pd.DataFrame:
        try:
            response_df = pd.DataFrame(response)
            log.info("Convert response into DataFrame" , df = response_df)
            return response_df 
        except Exception as e:
            log.error(f"Error Occured while compare_documents : {e}")
            raise DocumentException("Error Occured while compare_documents")