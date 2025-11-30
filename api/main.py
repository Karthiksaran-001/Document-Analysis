import os
import warnings
from fastapi import FastAPI , UploadFile , File , Form , HTTPException , Request
from fastapi.responses import JSONResponse , HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict , List , Optional , Any
warnings.filterwarnings("ignore")

app = FastAPI(title="Document Portal API", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static" , StaticFiles(directory="./static"),name="static")
template = Jinja2Templates(directory="./templates")

@app.get("/",response_class=HTMLResponse)
async def serve_ui(request:Request):
    return template.TemplateResponse("index.html",{"request":request})

@app.get("/health")
async def check_api()->Dict[str,str]:
    return {"status" : "ok" , "service" : "document-portal"}

@app.post("/analysis")
async def analyze_document(file:UploadFile = File(...))->Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Failed {e}")

@app.post("/compare")
async def compare_document(reference:UploadFile = File(...) , actual:UploadFile = File(...))->Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparision Failed {e}")

@app.post("/chat/index")
async def chat_index()->Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat Index Failed {e}")
    
@app.post("/chat/query")
async def chat_query()->Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat query Failed {e}")