import os
import fitz
import uuid 
from datetime import datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentException

class DocumentHandler:
    """
        Handle PDF saving and reading operations.
        Automatically logs all actions and support session based organization. 
    """
    def __init__(self,data_dir=None,session_id=None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = data_dir or os.getenv("DATA_STORAGE_PATH" , os.path.join(os.getcwd(),"data","document_analysis"))
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_id_path = os.path.join(self.data_dir , self.session_id)
            os.makedirs(self.session_id_path , exist_ok= True)
            self.log.info("PDF handler Initialized" , session_id = self.session_id ,session_path = self.session_id_path)
        except Exception as e:
            self.log.error(f"erorr initalized DocumentHandler {e}")
            raise DocumentException("erorr initalized DocumentHandler")
        
    def save_pdf(self,pdf_data):
        try:
            filename = os.path.basename(pdf_data.name)
            if not filename.lower().endswith(".pdf"):
                raise DocumentException("Invalid File Type Only PDf files are Allowed")
            filename = f"document_{self.session_id}.pdf"
            save_path = os.path.join(self.session_id_path,filename)
            with open(save_path ,"wb") as f:
                f.write(pdf_data.getbuffer())
            self.log.info("PDF Save Succesfully" , path = save_path)
            return save_path
        except Exception as e:
            self.log.error(f"erorr initalized Save PDF {e}") 

    def read_pdf(self,pdf_path:str):
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError("PDF is encrypted Cannot read from path :{file_path}")
                for page_num, page in enumerate(doc, start=1): # type: ignore
                    text_chunks.append(f"\n--- Page {page_num} ---\n{page.get_text()}")
            text = "\n".join(text_chunks)

            self.log.info("PDF read successfully", pdf_path=pdf_path, session_id=self.session_id, pages=len(text_chunks))
            return text
        except Exception as e:
            self.log.error(f"Error reading PDF: {e}")
            raise DocumentException("Error reading PDF", e) from e
