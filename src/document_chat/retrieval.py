import os
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
from utils.config_loader import load_config
from model.models import PromptType
from astrapy import DataAPIClient
import streamlit as st
warnings.filterwarnings("ignore")

class ConversationalRAG:
    def __init__(self,session_id:str , retriever):
        try:
            load_dotenv()
            self.session_id = session_id
            self.retriever = retriever
            self.llm = self._load_llm()
            self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
            self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
            self.config = load_config()
            self.db_keyspace = self.config["astra_db"]["key_space"]
            self.collection_name=self.config["astra_db"]["collection_name"]
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.history_aware_retriever = create_history_aware_retriever(
                self.llm , retriever=self.retriever , prompt= self.contextualize_prompt)
            self.qa_chain = create_stuff_documents_chain(self.llm,self.contextualize_prompt)
            self.rag_chain = create_retrieval_chain(self.history_aware_retriever , self.qa_chain)
            log.info("Initalize the Conversational RAG" , session_id = self.session_id)
            self.chain = RunnableWithMessageHistory(
                self.rag_chain , self._get_session_history, input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer")
        except Exception as e:
            log.error("Error in ConversationalRAG Initalizer" , error=str(e))
            raise DocumentException("Error in ConversationalRAG Initalizer")
    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            log.info("LLM loads successfully" , class_name = llm.__class__.__name__)
            return llm 
        except Exception as e:
            log.error("Error in Load LLM" , error=str(e))
            raise DocumentException("Error in Load LLM")
    def _get_session_history(self,session_id):
        try:
            if "store" not in st.session_state:
                st.session_state.store = {}

            if session_id not in st.session_state.store:
                st.session_state.store[session_id] = ChatMessageHistory()
                self.log.info("New chat session history created", session_id=session_id)
            return st.session_state.store[session_id]
        except Exception as e:
            self.log.error("Failed in get session history",session_id = session_id , error = str(e))
            raise DocumentException(e)
    def load_retriver_asda(self, collection_name:str):
        try:
            embedding = ModelLoader().load_embeddings()
            db = DataAPIClient(self.db_application_token).get_database(self.db_api_endpoint)
            collections = db.list_collections()
            if collection_name not in collections:
                raise DocumentException("ASTRA DB doent have the collection name" , collection_name =collection_name , collection_list =  collections)
            vectorstore = AstraDBVectorStore(
            embedding= embedding,
            collection_name=self.collection_name,
            api_endpoint=self.db_api_endpoint,
            token=self.db_application_token,
            namespace=self.db_keyspace,)
            log.info("Loaded Retriver", collection = collection_name)
            top_k = self.config["retriever"]["top_k"] if "retriver" in self.config else 3
            retriever = vectorstore.as_retriever(search_type = "similarity" , search_kwargs = {"k" : top_k})
            log.info("Retriever created Successfully" , retriever_type = str(type(retriever)))
        except Exception as e:
            self.log.error("Failed in load retriver faiss" , error = str(e))
            raise DocumentException(e)
    def invoke(self, user_input:str):
        try:
            response = self.chain.invoke({"input" : user_input},config= {"configurable":{"session_id" : self.session_id}})
            answer = response.get("answer" , "Not Found")
            if not answer:
                log.warning("Empty answer received", session_id=self.session_id)
            log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_preview=answer[:150])
        except Exception as e:
            self.log.error("Failed in invoke" , error = str(e))
            raise DocumentException(e)
    