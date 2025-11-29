import os
from pathlib import Path
from typing import Optional , List
from operator import itemgetter
from astrapy import DataAPIClient
from langchain_core.runnables import RunnableWithMessageHistory , RunnablePassthrough
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_astradb.vectorstores import AstraDBVectorStore
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.output_parsers  import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from logger import GLOBAL_LOGGER as log
from model.models import PromptType
from exception.custom_exception import DocumentException
from utils.model_loader import ModelLoader
from prompt.prompt_library import PROMPT_REGISTRY
from utils.config_loader import load_config
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

class ConversationalRAG:
    def __init__(self,session_id:str , retriever=None):
        try:
            self.session_id = session_id
            self.llm = self._load_llm()
            self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
            self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
            self.config = load_config()
            self.db_keyspace = self.config["astra_db"]["key_space"]
            self.collection_name=self.config["astra_db"]["collection_name"]
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            if retriever is None:
                raise ValueError("Retriever cannot be empty")
            self.retriever = retriever
            self._build_lcel_chain()
            log.info("ConversationalRAG Initialized")
        except Exception as e:
            log.error("Error in ConversationalRAG Initalizer" , error=str(e))
            raise DocumentException("Error in ConversationalRAG Initalizer")
    def load_retriever_from_asda(self,collection_name:str):
        try:
            embedding = ModelLoader().load_embeddings()
            db = DataAPIClient(self.db_application_token).get_database(self.db_api_endpoint)
            collections = db.list_collections()
            if not any(col.name == collection_name for col in collections):
                raise DocumentException("ASTRA DB doent have the collection name" , collection_name =collection_name , collection_list =  collections)
            vectorstore = AstraDBVectorStore(
            embedding= embedding,
            collection_name=self.collection_name,
            api_endpoint=self.db_api_endpoint,
            token=self.db_application_token,
            namespace=self.db_keyspace,)
            log.info("Loaded Retriver", collection = collection_name)
            top_k = self.config["retriever"]["top_k"] if "retriever" in self.config else 3
            self.retriever = vectorstore.as_retriever(search_type = "similarity" , search_kwargs = {"k" : top_k})
            log.info("Retriever created Successfully" , retriever_type = str(type(self.retriever)))
            self._build_lcel_chain()
            return self.retriever
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
    def _format_docs(docs):
        try:
            return "\n]\n".join(d.page_content for d in docs)
        except Exception as e:
            log.error("Error in Formatting Document" , error=str(e))
            raise DocumentException("Error in Formatting Document")
        
    def _build_lcel_chain(self):
        try:
            question_rewritter = (
                {"input" : itemgetter("input"),"chat_history" : itemgetter("chat_history")}
                | self.contextualize_prompt | self.llm | StrOutputParser()
            )
            retrieved_docs = self.retriever | self._format_docs
            self.chain = (
                {
                    "context" : retrieved_docs,
                    "input": itemgetter("input"),
                    "chat_history" : itemgetter("chat_history"),

                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser())
            log.info("Chain is Created")
        except Exception as e:
            log.error("Error in Building LCEL" , error=str(e))
            raise DocumentException("Error in Building LCEL")