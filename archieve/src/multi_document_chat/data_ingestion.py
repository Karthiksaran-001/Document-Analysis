import os
from pathlib import Path
import warnings
import uuid
from datetime import datetime , timezone
from langchain_community.document_loaders import PyPDFLoader , Docx2txtLoader , TextLoader , UnstructuredWordDocumentLoader
from utils.model_loader import ModelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_astradb.vectorstores import AstraDBVectorStore
from logger import GLOBAL_LOGGER as log
from utils.config_loader import load_config
from exception.custom_exception import DocumentException


class DocumentIngestion:
    SUPPORTED_EXTENSIONS = {".pdf" : "" , ".txt" : "" , ".docx" : "" , ".doc" : ""  , ".md" : ""}
    def __init__(self, temp_dir:str = r"./data/multi_doc_chat",session_id=None):
        try:
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True , exist_ok=True)
            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_dir = self.temp_dir/self.session_id
            self.session_dir.mkdir(parents=True, exist_ok=True)
            self.model_loader = ModelLoader()
            self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
            self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
            self.config = load_config()
            self.db_keyspace = self.config["astra_db"]["key_space"]
            self.collection_name=self.config["astra_db"]["multi_doc_colection_name"]
            log.info("DocumentIngestion Initialized",
                     dir_path = str(self.temp_dir),
                     session_id = str(self.session_id),
                     session_dir = str(self.session_dir),
                     db_collection_name =self.collection_name ) 
        except Exception as e:
            log.error("Error in DocumentIngestion Initalizer" , error = e)
            raise DocumentException("Error in DocumentIngestion Initalizer")
    def ingest_file(self,uploaded_files):
        try:
            documents = []
            for file in uploaded_files:
                ext = Path(file.name).suffix.lower()
                if ext not in self.SUPPORTED_EXTENSIONS:
                    log.warning("Unsupported File Type Skipped" , file = file , supported_file = self.SUPPORT_FILE_TYPES)
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}" 
                temp_path = self.session_dir/unique_filename
                with open(temp_path, "wb") as f:
                    f.write(file.read())
                log.info("File Saved for Ingestion", filename= file.name , saved_as =str(temp_path),session_id = self.session_id)
                if ext == ".pdf":
                    loader = PyPDFLoader(str(temp_path))
                elif ext in [".txt" , ".md"]:
                    loader = TextLoader(str(temp_path),encoding="utf-8")
                elif ext in [".doc" , ".docx"]:
                    if ext == ".docx":
                        loader = Docx2txtLoader(str(temp_path))
                    else:
                        loader = UnstructuredWordDocumentLoader(str(temp_path))
                else:
                    log.warning("Unsupported File type encountered" , filename = file.name)
                docs = loader.load()
                documents.extend(docs)
            if not documents:
                raise DocumentException("No Valid Documents Found")
            log.info("All documents loaded" , session_id = self.session_id, no_of_docs = len(documents)) 
            return self._create_retriever(documents)                
        except Exception as e:
            log.error("Error in Ingest File" , error = e)
            raise DocumentException("Error in Ingest File")
    def _create_retriever(self , documents):
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
            log.info("Retriever created Successfully" , retriever_type = str(type(retriever)) , collection_name = str(self.collection_name))
            return retriever 
        except Exception as e:
            log.error("Error in Create Retrieval" , error = e)
            raise DocumentException("Error in Create Retrieval") 