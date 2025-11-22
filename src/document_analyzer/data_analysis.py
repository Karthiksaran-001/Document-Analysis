import os 
from utils.model_loader import ModelLoader
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException
from model.models import Metadata
from prompt.prompt_library import PROMPT_REGISTRY 
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
import warnings
warnings.filterwarnings("ignore")


class DocumentAnalyzer:
    def __init__(self):
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
            self.prompt = PROMPT_REGISTRY["document_analysis"]
            log.info("DocumentAnalyzer initialized successfully")

        except Exception as e:
            log.error(f"Error in DocumentAnalyzer initializer {e}")
            raise DocumentException("Error in DocumentAnalyzer initializer")

    def analyze_document(self,document_text:str)->dict:
        """
        Analyze a document's text and extract structured metadata & summary.
        """
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            
            log.info("Meta-data analysis chain initialized")

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": document_text
            })

            log.info("Metadata extraction successful", keys=list(response.keys()))
            
            return response

        except Exception as e:
            log.error("Metadata analysis failed", error=str(e))
            raise DocumentException("Metadata extraction failed",)


