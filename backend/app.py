import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import graph, state, dan check_config
from agents.graph import app_graph
from config import check_config

# Jalankan pengecekan konfigurasi saat startup
check_config()

app = FastAPI(title="Resume & Cover Letter Analyzer API")

# Konfigurasi CORS agar frontend React bisa mengakses backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# PYDANTIC MODEL SCHEMAS
# ==========================================

class AnalyzeRequest(BaseModel):
    cv: str
    job_description: str

class FeedbackRequest(BaseModel):
    thread_id: str
    feedback: str


# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/api/health")
def read_root():
    return {"message": "Resume & Cover Letter Analyzer API Aktif!"}

@app.post("/api/analyze")
async def start_analysis(req: AnalyzeRequest):
    """
    Memulai alur analisis CV & pembuatan Cover Letter.
    Ini akan berjalan sampai terhenti (interrupt) sebelum Node Human Review.
    """
    if not req.cv.strip() or not req.job_description.strip():
        raise HTTPException(status_code=400, detail="CV dan Job Description tidak boleh kosong.")
        
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "cv": req.cv,
        "job_description": req.job_description,
        "analysis": "",
        "cover_letter": "",
        "feedback": "",
        "status": "starting",
        "revision_count": 0
    }
    
    try:
        # Jalankan graph sampai terhenti di interrupt_before=["human_review"]
        # Kita menggunakan stream() atau invoke()
        app_graph.invoke(initial_state, config=config)
        
        # Ambil state terbaru setelah interrupt terjadi
        current_state = app_graph.get_state(config)
        state_data = current_state.values
        
        return {
            "thread_id": thread_id,
            "analysis": state_data.get("analysis", ""),
            "cover_letter": state_data.get("cover_letter", ""),
            "status": "waiting_feedback",
            "revision_count": state_data.get("revision_count", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menjalankan analisis: {str(e)}")

@app.post("/api/feedback")
async def process_feedback(req: FeedbackRequest):
    """
    Memproses masukan revisi atau persetujuan dari user untuk melanutkan graph.
    """
    config = {"configurable": {"thread_id": req.thread_id}}
    
    # Ambil state saat ini
    current_state = app_graph.get_state(config)
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Sesi analisis tidak ditemukan.")
        
    # Update state dengan feedback user
    feedback_text = req.feedback.strip()
    
    # Kita update state di thread tersebut
    app_graph.update_state(config, {"feedback": feedback_text})
    
    try:
        # Lanjutkan eksekusi graph (kirim None untuk melanjutkan dari checkpoint)
        app_graph.invoke(None, config=config)
        
        # Ambil state setelah graph berjalan lagi (apakah terhenti lagi atau selesai)
        next_state = app_graph.get_state(config)
        next_values = next_state.values
        
        # Cek apakah graph sudah selesai (next_state.next kosong)
        is_done = len(next_state.next) == 0
        
        return {
            "thread_id": req.thread_id,
            "analysis": next_values.get("analysis", ""),
            "cover_letter": next_values.get("cover_letter", ""),
            "status": "done" if is_done else "waiting_feedback",
            "revision_count": next_values.get("revision_count", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses feedback: {str(e)}")

@app.get("/api/status/{thread_id}")
async def get_session_status(thread_id: str):
    """
    Mendapatkan detail state terbaru dari sesi yang sedang berjalan.
    """
    config = {"configurable": {"thread_id": thread_id}}
    current_state = app_graph.get_state(config)
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan.")
        
    values = current_state.values
    is_done = len(current_state.next) == 0
    
    return {
        "thread_id": thread_id,
        "analysis": values.get("analysis", ""),
        "cover_letter": values.get("cover_letter", ""),
        "status": "done" if is_done else "waiting_feedback",
        "revision_count": values.get("revision_count", 0)
    }

from fastapi.staticfiles import StaticFiles
import os

# Sajikan file frontend secara statis pada URL root
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
