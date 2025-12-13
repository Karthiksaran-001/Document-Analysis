import os
import uuid
from dotenv import load_dotenv
import warnings
from pathlib import Path 
from datetime import datetime , timezone
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_astradb.vectorstores import AstraDBVectorStore
from logger import GLOBAL_LOGGER as log 
from exception.custom_exception import DocumentException
from utils.model_loader import ModelLoader
from utils.config_loader import load_config
warnings.filterwarnings("ignore")
class SingleDocIngestor:
    def __init__(self,data_dir = r"./data/single_doc_chat" , session_id = None):
        try:
            load_dotenv()
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True , exist_ok= True)
            self.file_path = self.data_dir / f"{uuid.uuid4()}.pdf"
            self.model_loader = ModelLoader()
            self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
            self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
            self.config = load_config()
            self.db_keyspace = self.config["astra_db"]["key_space"]
            self.collection_name=self.config["astra_db"]["collection_name"]
            log.info("SingleDocIngestor Initalized Successfully" , data_dir = self.data_dir)
        except Exception as e:
            log.error("Error in SingleDocIngestor Initalizer" , error=str(e))
            raise DocumentException("Error in SingleDocIngestor Initalizer")
    def ingest_files(self , uploaded_files):
        try:
            documents = []
            for file in uploaded_files:
                unique_filename = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = self.data_dir / unique_filename
                with open(temp_path , "wb") as f_out:
                    f_out.write(file.read())
                log.info("PDF are Saved for Ingestion", file_name =file.name)
                loader = PyMuPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
            log.info("PDF file Load" , count = len(documents))
            return self._create_retriever(documents)
        except Exception as e:
            log.error("Error in Ingest File" , error=str(e))
            raise DocumentException("Error in Ingest File")
        
    def _create_retriever(self,documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap = 300)
            chunks = splitter.split_documents(documents)
            log.info("Split the Document into Chunks",chunk_size = len(chunks))
            embedding = self.model_loader.load_embeddings()
            vectorstore = AstraDBVectorStore(
            embedding= embedding,
            collection_name=self.collection_name,
            api_endpoint=self.db_api_endpoint,
            token=self.db_application_token,
            namespace=self.db_keyspace,)
            inserted_ids = vectorstore.add_documents(chunks)
            log.info(f"Successfully inserted {len(inserted_ids)} documents into AstraDB.")
            top_k = self.config["retriever"]["top_k"] if "retriever" in self.config else 3
            retriever = vectorstore.as_retriever(search_type = "similarity" , search_kwargs = {"k" : top_k})
            log.info("Retriever created Successfully" , retriever_type = str(type(retriever)))
            return retriever
        except Exception as e:
            log.error("Error in Retriever Creation" , error=str(e))
            raise DocumentException("Error in Retriever Creation")
    
