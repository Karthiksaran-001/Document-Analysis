import os 
from pathlib import Path 
import fitz
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException
from datetime import datetime, timezone
import uuid


class DocumentIngestion:
    def __init__(self,base_dir:str = "data\document_compare", session_id = None):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)

    def save_uploaded_files(self , ref_file , act_file):
        try:
            ref_path = self.session_path / ref_file.name
            act_path = self.session_path / act_file.name
            #ref_path = Path(os.path.join(self.base_dir , ref_file.name))
            #act_path = Path(os.path.join(self.base_dir , act_file.name))
            if not ref_file.name.lower().endswith(".pdf") or not act_file.name.lower().endswith(".pdf"):
                raise ValueError("Only PDF files are allowed.")
            #print(ref_path)
            with open(ref_path, "wb") as f:
                f.write(ref_file.get_buffer())

            with open(act_path, "wb") as f:
                f.write(act_file.get_buffer())

            log.info("Files saved", reference=str(ref_path), actual=str(act_path))
            return ref_path, act_path
        except Exception as e:
            log.error(f"Error Occured while upload file : {e}")
            raise DocumentException("Error Occured while upload file") 
    def read_pdf(self, pdf_path: Path) -> str:
        """
        Read text content of a PDF page-by-page.
        """
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted: {pdf_path.name}")
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()  # type: ignore
                    if text.strip():
                         all_text.append(f"\n --- Page {page_num + 1} --- \n{text}")
            log.info("PDF read successfully", file=str(pdf_path), pages=len(all_text))
            return "\n".join(all_text)

        except Exception as e:
            log.error("Error reading PDF", file=str(pdf_path), error=str(e))
            raise DocumentException("Error reading PDF")
        
    def combined_documents(self):
        try:
            concat_dict = {}
            doc_part = []
            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix == ".pdf":
                    concat_dict[filename.name] = self.read_pdf(filename)
            for filename , content in concat_dict.items():
                doc_part.append(f"Document: {filename}\n{content}")
            combined_doc = "\n\n".join(doc_part)
            log.info("Document Combined", count = len(doc_part))
            return combined_doc
            
        except Exception as e:
            log.error(f"Error Occured while combined_documents : {e}")
            raise DocumentException("Error Occured while combined_documents")
        

    def clean_old_sessions(self, keep_latest: int = 3):
        """
        Optional method to delete older session folders, keeping only the latest N.
        """
        try:
            session_folders = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                reverse=True
            )
            for folder in session_folders[keep_latest:]:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
                log.info("Old session folder deleted", path=str(folder))

        except Exception as e:
            log.error("Error cleaning old sessions", error=str(e))
            raise DocumentException("Error cleaning old sessions")