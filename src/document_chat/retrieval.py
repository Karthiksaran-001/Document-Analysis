import os
from typing import Optional , List , Dict , Any
from operator import itemgetter
from astrapy import DataAPIClient
from langchain_astradb.vectorstores import AstraDBVectorStore
from langchain_core.output_parsers  import StrOutputParser
from langchain_core.messages import BaseMessage, HumanMessage
from logger import GLOBAL_LOGGER as log
from model.models import PromptType
from exception.custom_exception import DocumentException
from utils.model_loader import ModelLoader
from prompt.prompt_library import PROMPT_REGISTRY
from utils.config_loader import load_config
from dotenv import load_dotenv
load_dotenv()
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
            self.retriever = retriever
            self.chain = None
            if self.retriever is not None:
                self._build_lcel_chain()
            log.info("ConversationalRAG Initialized")
        except Exception as e:
            log.error("Error in ConversationalRAG Initalizer" , error=str(e))
            raise DocumentException("Error in ConversationalRAG Initalizer")
    def load_retriever_from_asda(self,collection_name:str, k: int = 5,search_type: str = "similarity",search_kwargs: Optional[Dict[str, Any]] = None):
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
            if search_kwargs is None:
                search_kwargs = {"k": k}
            log.info("Loaded Retriver", collection = collection_name)
            self.retriever = vectorstore.as_retriever(search_type = search_type , search_kwargs = search_kwargs)
            self._build_lcel_chain()
            log.info(
                "ASDA  retriever loaded successfully",
                collection=collection_name,
                k=k,session_id=self.session_id,)
        except Exception as e:
            log.error("Error in Load Retriever" , error=str(e))
            raise DocumentException("Error in Load Retriever")
        
    
    def invoke(self, messages: List[BaseMessage] , chat_history : Optional[List[BaseMessage]] = None):
        try:
            if self.chain is None:
                raise DocumentException(
                    "RAG chain not initialized. Call load_retriever_from_asda() before invoke().")
            user_input = messages[-1]
            if not isinstance(user_input, HumanMessage):
                raise ValueError("Last message is not HumanMessage")
            chat_history = messages[:-1]
            payload = {"input" : user_input,"chat_history" : chat_history}
            answer = self.chain.invoke(payload) 
            if answer is None:
                log.warning("Answer is None" ,input = user_input ,session_id = self.session_id)
                return "No answer found"
            log.info("Answer generated" , session_id = self.session_id, input = user_input , answer_preview = answer[:100])
            return answer
        except Exception as e:
            log.error("Failed in load retriver DB" , error = str(e))
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
            return "\n\n".join([d.page_content for d in docs]) 
        except Exception as e:
            log.error("Error in Formatting Document" , error=str(e))
            raise DocumentException("Error in Formatting Document")
        
    def _build_lcel_chain(self):
        try:
            if self.retriever is None:
                raise DocumentException
            ("No retriever set before building chain")
            question_rewritter = (
                {"input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )
            retrieve_docs = question_rewritter | self.retriever | self._format_docs
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history"),
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )
            log.info("LCEL Chain is Created")
        except Exception as e:
            log.error("Error in Building LCEL" , error=str(e))
            raise DocumentException("Error in Building LCEL")