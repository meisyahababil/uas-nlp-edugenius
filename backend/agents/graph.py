import os
from typing import Dict, Any, Literal
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Import state dan config
from agents.state import AgentState
from config import GROQ_API_KEY

# Inisialisasi LLM via Groq (free tier cepat & longgar)
# Model: llama-3.3-70b-versatile — gratis, konteks besar, cocok untuk analisis teks panjang
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY or "dummy_key_for_startup",
    temperature=0.3
)

# ==========================================
# PROMPTS DEFINITIONS
# ==========================================

# 1. Prompt untuk Menganalisis CV terhadap Lowongan Pekerjaan
analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Anda adalah seorang perekrut HR (Human Resources) profesional dan ahli sistem ATS (Applicant Tracking System).\n"
        "Tugas Anda adalah menganalisis CV/Resume pelamar kerja terhadap Deskripsi Pekerjaan (Job Description) yang diberikan.\n\n"
        "Berikan output analisis yang sangat terstruktur dalam format Markdown berisi:\n"
        "1. **Skor Kecocokan (ATS Match Score)**: Berikan nilai persentase (0% - 100%) dengan justifikasi logis singkat.\n"
        "2. **Kelebihan Utama (Key Strengths)**: 3-4 poin di mana CV pelamar sangat cocok dengan persyaratan pekerjaan.\n"
        "3. **Kesenjangan Keterampilan (Skill Gaps / Missing Keywords)**: Daftar keterampilan penting, sertifikasi, atau kata kunci dari lowongan kerja yang TIDAK ditemukan di CV.\n"
        "4. **Rekomendasi Perbaikan CV**: Saran praktis untuk meningkatkan relevansi CV pelamar.\n\n"
        "Gunakan Bahasa Indonesia yang profesional dan objektif."
    )),
    ("user", "CV/Resume:\n{cv}\n\nDeskripsi Pekerjaan (Job Description):\n{job_description}")
])

# 2. Prompt untuk Membuat Cover Letter
cover_letter_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Anda adalah seorang konsultan karir profesional.\n"
        "Tugas Anda adalah menulis Cover Letter (Surat Lamaran Kerja) yang persuasif, profesional, dan disesuaikan secara khusus (tailored) berdasarkan CV pelamar dan Deskripsi Pekerjaan.\n\n"
        "Panduan Penulisan:\n"
        "- Hubungkan kelebihan pelamar (berdasarkan Analisis CV) dengan kebutuhan perusahaan di Deskripsi Pekerjaan.\n"
        "- Buat tulisan terstruktur: Pembukaan yang menarik perhatian, tubuh surat yang menonjolkan kecocokan skill dan kontribusi yang bisa diberikan, serta penutup yang menunjukkan antusiasme untuk wawancara.\n"
        "- Jangan mengada-ada fakta yang tidak ada di CV.\n"
        "- Tulis dalam Bahasa Indonesia yang formal dan profesional.\n"
        "- Jika ada masukan (feedback) revisi sebelumnya dari pengguna, Anda WAJIB menyesuaikan Cover Letter tersebut sesuai dengan instruksi feedback."
    )),
    ("user", (
        "CV/Resume:\n{cv}\n\n"
        "Deskripsi Pekerjaan:\n{job_description}\n\n"
        "Hasil Analisis CV:\n{analysis}\n\n"
        "Draf Cover Letter Sebelumnya (jika ada):\n{prev_cover_letter}\n\n"
        "Masukan Revisi Pengguna (jika ada):\n{feedback}"
    ))
])


# ==========================================
# GRAPH NODES
# ==========================================

def analyze_cv_node(state: AgentState) -> Dict[str, Any]:
    """Node untuk menganalisis kecocokan CV dengan Job Description."""
    print("--- MENJALANKAN: NODE ANALIS CV ---")
    
    # Jalankan Chain
    chain = analysis_prompt | llm
    response = chain.invoke({
        "cv": state["cv"],
        "job_description": state["job_description"]
    })
    
    return {
        "analysis": response.content,
        "status": "analyzing_done"
    }

def generate_cover_letter_node(state: AgentState) -> Dict[str, Any]:
    """Node untuk membuat atau merevisi Cover Letter."""
    print("--- MENJALANKAN: NODE GENERATOR COVER LETTER ---")
    
    # Ambil data revisi
    prev_cl = state.get("cover_letter", "") or ""
    feedback = state.get("feedback", "") or ""
    revision_count = state.get("revision_count", 0)
    
    # Jika ini adalah loop revisi (ada feedback)
    if feedback:
        revision_count += 1
        
    chain = cover_letter_prompt | llm
    response = chain.invoke({
        "cv": state["cv"],
        "job_description": state["job_description"],
        "analysis": state["analysis"],
        "prev_cover_letter": prev_cl,
        "feedback": feedback
    })
    
    # Reset feedback setelah dibaca agar tidak terjadi loop tak terbatas
    return {
        "cover_letter": response.content,
        "feedback": "",
        "revision_count": revision_count,
        "status": "generating_cl_done"
    }

def human_review_node(state: AgentState) -> Dict[str, Any]:
    """
    Node penampung untuk interupsi manusia (Human-in-the-loop).
    Di sinilah alur kerja akan di-interrupt (jeda) sebelum masuk ke node ini,
    sehingga user bisa melihat draf Cover Letter dan menuliskan feedback atau menyetujuinya.
    """
    print("--- MENJALANKAN: NODE HUMAN REVIEW ---")
    return {
        "status": "waiting_feedback"
    }


# ==========================================
# CONDITIONAL EDGES & ROUTING
# ==========================================

def decide_next_step(state: AgentState) -> Literal["generate_cl", "end"]:
    """Menentukan apakah alur lanjut ke revisi atau selesai berdasarkan feedback user."""
    feedback = state.get("feedback", "")
    
    # Jika feedback kosong atau user menginput kata kunci persetujuan, kita selesai
    if not feedback or feedback.strip().lower() in ["approve", "setuju", "oke", "ok", "selesai"]:
        print("--- ROUTING: DISETUJUI, SELESAI ---")
        return "end"
    
    # Jika ada feedback revisi dari user, kembali ke node pembuatan Cover Letter
    print(f"--- ROUTING: ADA REVISI -> {feedback} ---")
    return "generate_cl"


# ==========================================
# WORKFLOW CONSTRUCTION
# ==========================================

# Buat workflow graph
workflow = StateGraph(AgentState)

# Daftarkan Nodes
workflow.add_node("analyze_cv", analyze_cv_node)
workflow.add_node("generate_cl", generate_cover_letter_node)
workflow.add_node("human_review", human_review_node)

# Konfigurasi Alur (Edges)
workflow.add_edge(START, "analyze_cv")
workflow.add_edge("analyze_cv", "generate_cl")
workflow.add_edge("generate_cl", "human_review")

# Tambahkan percabangan bersyarat (Conditional Edge) dari Node Human Review
workflow.add_conditional_edges(
    "human_review",
    decide_next_step,
    {
        "generate_cl": "generate_cl",
        "end": END
    }
)

# Tambahkan checkpoint memory saver agar graph bisa menyimpan state-nya saat interrupt
memory = MemorySaver()

# Compile graph dengan konfigurasi interrupt sebelum node human_review
app_graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)

# Untuk keperluan testing lokal
if __name__ == "__main__":
    # Test sederhana
    print("Graf berhasil dibangun dan dicompile.")
