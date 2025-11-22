import sys
from dotenv import load_dotenv
import warnings
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_astradb.vectorstores import AstraDBVectorStore
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.model_loader import ModelLoader
from logger import GLOBAL_LOGGER as log 
from exception.custom_exception import DocumentException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self):
        try:
            pass 
        except Exception as e:
            log.error("Error in ConversationalRAG Initalizer" , error=str(e))
            raise DocumentException("Error in ConversationalRAG Initalizer")
    def _load_llm(self):
        try:
            pass 
        except Exception as e:
            log.error("Error in Load LLM" , error=str(e))
            raise DocumentException("Error in Load LLM")
    def _get_session_history(self,session_id):
        try:
            pass
        except Exception as e:
            self.log.error("Failed in get session history",session_id = session_id , error = str(e))
            raise DocumentException(e)
    def load_retriver_faiss(self, index_path:str):
        try:
            pass 
        except Exception as e:
            self.log.error("Failed in load retriver faiss" , error = str(e))
            raise DocumentException(e)
    def invoke(self, user_input):
        try:
            pass 
        except Exception as e:
            self.log.error("Failed in invoke" , error = str(e))
            raise DocumentException(e)
    