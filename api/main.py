import os
import warnings
from astrapy import DataAPIClient
from fastapi import FastAPI , UploadFile , File , Form , HTTPException , Request
from fastapi.responses import JSONResponse , HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict , List , Optional , Any
from logger import GLOBAL_LOGGER as log
from src.document_ingestion.data_ingestion import (DocHandler,DocumentComparator,ChatIngestor)
from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_compare.document_comparator import DocumentComparatorLLM
from src.document_chat.retrieval import ConversationalRAG
from utils.config_loader import load_config
from utils.document_ops import FastAPIFileAdapter, read_pdf
from dotenv import load_dotenv
load_dotenv()
warnings.filterwarnings("ignore")

UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")
CONFIG = load_config()
COLLECTION_NAME = CONFIG["astra_db"]["collection_name"]
DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
DB_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

app = FastAPI(title="Document Portal API", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

app.mount("/static" , StaticFiles(directory="./static"),name="static")
template = Jinja2Templates(directory="./templates")

@app.get("/",response_class=HTMLResponse)
async def serve_ui(request:Request):
    return template.TemplateResponse("index.html",{"request":request})

@app.get("/health")
async def check_api()->Dict[str,str]:
    return {"status" : "ok" , "service" : "document-portal"}

@app.post("/analyze")
async def analyze_document(file:UploadFile = File(...))->Any:
    try:
        log.info(f"Received file for analysis: {file.filename}")
        dh = DocHandler()
        file_path = dh.save_pdf(FastAPIFileAdapter(file))
        text = read_pdf(file_path,session_id=dh.session_id)
        analyze = DocumentAnalyzer()
        result = analyze.analyze_document(text)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error during document analysis")
        raise HTTPException(status_code=500, detail=f"Analysis Failed {e}")

@app.post("/compare")
async def compare_document(reference:UploadFile = File(...) , actual:UploadFile = File(...))->Any:
    try:
        dc = DocumentComparator()
        ref_path , act_path = dc.save_uploaded_files(FastAPIFileAdapter(reference),FastAPIFileAdapter(actual))
        _ , _ = ref_path , act_path
        combined_text = dc.combine_documents()
        comp = DocumentComparatorLLM()
        df = comp.compare_documents(combined_text)
        return {"rows" : df.to_dict(orient = "records"), "session_id":dc.session_id} # type:ignore
    except Exception:
        raise
    except Exception as e:
        log.error("Comparison failed")
        raise HTTPException(status_code=500, detail=f"Comparision Failed {e}")

@app.post("/chat/index")
async def chat_index( 
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),)->Any:
    try:
        log.info(f"Indexing chat session. Session ID: {session_id}, Files: {[f.filename for f in files]}")
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
            temp_base=UPLOAD_BASE,
            collection_name=COLLECTION_NAME,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,)
        _ , chunks = ci.build_retriever( wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
        if chunks ==0:
            log.info(f"Index Already created for session: {ci.session_id}")
            return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs} 
        else:    
            log.info(f"Index created successfully for session: {ci.session_id}")
            return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}           
    except HTTPException:
        raise
    except Exception as e:
        log.error("Chat index building failed")
        raise HTTPException(status_code=500, detail=f"Chat Index Failed {e}")
    
@app.post("/chat/query")
async def chat_query(question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),)->Any:
    try:
        log.info(f"Received chat query: '{question}' | session: {session_id}")
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs=True")
        db = DataAPIClient(DB_TOKEN).get_database(DB_API_ENDPOINT)
        collections = db.list_collections()
        if not any(col.name == COLLECTION_NAME for col in collections):
                raise HTTPException(status_code=404, detail=f"COLLECTION NAME : {COLLECTION_NAME} not found")
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_asda(COLLECTION_NAME , k = k)
        response = rag.invoke(question, chat_history=[])
        log.info("Chat query handled successfully.")
        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"}

    except HTTPException:
        raise
    except Exception as e:
        log.error("Chat query building failed")
        raise HTTPException(status_code=500, detail=f"Chat query Failed {e}")